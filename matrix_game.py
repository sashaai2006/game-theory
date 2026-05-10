from __future__ import annotations

from typing import Any

import numpy as np
from scipy.optimize import linprog

from config import COL_NAMES, MATRIX, ROW_NAMES


def saddle_point(matrix: np.ndarray) -> tuple[float, float, tuple[int, int] | None]:
    row_mins = matrix.min(axis=1)
    col_maxs = matrix.max(axis=0)
    alpha = float(row_mins.max())
    beta = float(col_maxs.min())

    coords = None
    if np.isclose(alpha, beta):
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if np.isclose(matrix[i, j], alpha):
                    coords = (i, j)
                    break
    return alpha, beta, coords


def dominance_reduction(
    matrix: np.ndarray,
    row_names: list[str],
    col_names: list[str],
) -> tuple[np.ndarray, list[str], list[str], list[int], list[dict[str, Any]]]:
    m = matrix.copy()
    rn = list(row_names)
    cn = list(col_names)
    kept_col_idx = list(range(matrix.shape[1]))
    removed: list[dict[str, Any]] = []

    changed = True
    while changed:
        changed = False

        drop_cols: set[int] = set()
        for j in range(m.shape[1]):
            for k in range(m.shape[1]):
                if j != k and j not in drop_cols and k not in drop_cols:
                    if np.all(m[:, k] <= m[:, j]):
                        drop_cols.add(j)
                        removed.append({
                            "type": "col",
                            "removed": cn[j],
                            "dominates": cn[k],
                            "reason": f"∀i: a[i,{cn[k]}] ≤ a[i,{cn[j]}]",
                        })
                        break
        if drop_cols:
            changed = True
            keep = [j for j in range(m.shape[1]) if j not in drop_cols]
            m = m[:, keep]
            cn = [cn[j] for j in keep]
            kept_col_idx = [kept_col_idx[j] for j in keep]

        drop_rows: set[int] = set()
        for i in range(m.shape[0]):
            for k in range(m.shape[0]):
                if i != k and i not in drop_rows and k not in drop_rows:
                    if np.all(m[k, :] >= m[i, :]):
                        drop_rows.add(i)
                        removed.append({
                            "type": "row",
                            "removed": rn[i],
                            "dominates": rn[k],
                            "reason": f"∀j: a[{rn[k]},j] ≥ a[{rn[i]},j]",
                        })
                        break
        if drop_rows:
            changed = True
            keep = [i for i in range(m.shape[0]) if i not in drop_rows]
            m = m[keep, :]
            rn = [rn[i] for i in keep]

    return m, rn, cn, kept_col_idx, removed


def solve_lp(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    m_rows, n_cols = matrix.shape
    c_shift = max(0.0, -matrix.min()) + 1.0
    A = matrix + c_shift

    res_a = linprog(
        c=np.ones(m_rows),
        A_ub=-A.T,
        b_ub=-np.ones(n_cols),
        bounds=[(0, None)] * m_rows,
        method="highs",
    )
    v_prime_a = 1.0 / res_a.fun
    p_opt = res_a.x * v_prime_a
    v_opt = v_prime_a - c_shift

    res_b = linprog(
        c=-np.ones(n_cols),
        A_ub=A,
        b_ub=np.ones(m_rows),
        bounds=[(0, None)] * n_cols,
        method="highs",
    )
    opt_sum_y = -res_b.fun
    v_prime_b = 1.0 / opt_sum_y
    q_opt = res_b.x * v_prime_b

    return p_opt, q_opt, v_opt


def brown_robinson(
    matrix: np.ndarray,
    n_iter: int = 1000,
) -> tuple[np.ndarray, np.ndarray, float, np.ndarray, np.ndarray, list[int], list[int]]:
    m_rows, n_cols = matrix.shape

    a_count = np.zeros(m_rows)
    b_count = np.zeros(n_cols)
    A_cum = np.zeros(m_rows)
    B_cum = np.zeros(n_cols)

    v_lower_history: list[float] = []
    v_upper_history: list[float] = []
    rows_hist: list[int] = []
    cols_hist: list[int] = []

    a_row = int(np.argmax(matrix.min(axis=1)))

    for t in range(1, n_iter + 1):
        a_count[a_row] += 1
        B_cum += matrix[a_row, :]
        rows_hist.append(a_row)

        b_col = int(np.argmin(B_cum))
        b_count[b_col] += 1
        A_cum += matrix[:, b_col]
        cols_hist.append(b_col)

        v_lower_history.append(float(B_cum.min() / t))
        v_upper_history.append(float(A_cum.max() / t))

        a_row = int(np.argmax(A_cum))

    p_br = a_count / n_iter
    q_br = b_count / n_iter
    v_br = (v_lower_history[-1] + v_upper_history[-1]) / 2.0

    return (
        p_br,
        q_br,
        v_br,
        np.array(v_lower_history),
        np.array(v_upper_history),
        rows_hist,
        cols_hist,
    )


def lp_shift_constant(matrix: np.ndarray) -> float:
    return max(0.0, -matrix.min()) + 1.0


def expected_payoff_lines_2rows(
    red_matrix: np.ndarray,
    n_points: int = 600,
) -> tuple[np.ndarray, np.ndarray]:
    if red_matrix.shape[0] != 2:
        raise ValueError("Ожидается матрица с двумя строками (игрок A).")
    p_vals = np.linspace(0, 1, n_points)
    E_lines = np.empty((red_matrix.shape[1], n_points))
    for j in range(red_matrix.shape[1]):
        E_lines[j] = (
            red_matrix[0, j] * p_vals + red_matrix[1, j] * (1.0 - p_vals)
        )
    return p_vals, E_lines


def run_all_computations(n_br_iter: int = 1000) -> dict[str, Any]:
    red_matrix, red_rows, red_cols, kept, removed = dominance_reduction(
        MATRIX, ROW_NAMES, COL_NAMES
    )

    alpha_orig, beta_orig, sp_orig = saddle_point(MATRIX)
    alpha_red, beta_red, sp_red = saddle_point(red_matrix)

    p_lp, q_lp_r, v_lp = solve_lp(red_matrix)
    p_br, q_br_r, v_br, v_lo, v_hi, rows_hist, cols_hist = brown_robinson(
        red_matrix, n_iter=n_br_iter
    )

    R = red_matrix
    a11, a12 = R[0, 0], R[0, 1]
    a21, a22 = R[1, 0], R[1, 1]
    d = a11 - a21 - a12 + a22
    p_ex = (a22 - a21) / d
    q_ex = (a22 - a12) / d
    v_ex = a11 * p_ex + a21 * (1.0 - p_ex)

    q_ex_vec = np.array([q_ex, 1.0 - q_ex])
    n_full = int(MATRIX.shape[1])
    q_lp_full = np.zeros(n_full)
    q_br_full = np.zeros(n_full)
    q_ex_full = np.zeros(n_full)
    for ir, io in enumerate(kept):
        q_lp_full[io] = q_lp_r[ir]
        q_br_full[io] = q_br_r[ir]
        q_ex_full[io] = q_ex_vec[ir]

    c_shift = lp_shift_constant(red_matrix)

    rlog = [
        {"type": r["type"], "removed": r["removed"], "dominant": r["dominates"]}
        for r in removed
    ]

    return {
        "R": red_matrix,
        "rn": red_rows,
        "cn": red_cols,
        "kept": kept,
        "rlog": rlog,
        "alpha": alpha_orig,
        "beta": beta_orig,
        "sp": sp_orig,
        "a_r": alpha_red,
        "b_r": beta_red,
        "sp_r": sp_red,
        "p_lp": p_lp,
        "q_lp_r": q_lp_r,
        "q_lp_full": q_lp_full,
        "v_lp": v_lp,
        "c_shift": c_shift,
        "p_br": p_br,
        "q_br_r": q_br_r,
        "q_br_full": q_br_full,
        "v_br": v_br,
        "vlo": v_lo,
        "vhi": v_hi,
        "rows_hist": rows_hist,
        "cols_hist": cols_hist,
        "p_ex": p_ex,
        "q_ex": q_ex,
        "q_ex_vec": q_ex_vec,
        "q_ex_full": q_ex_full,
        "v_ex": v_ex,
        "a11": a11,
        "a12": a12,
        "a21": a21,
        "a22": a22,
        "d": d,
    }
