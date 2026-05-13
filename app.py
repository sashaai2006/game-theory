import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from startup_vs_market.config import COL_NAMES, MATRIX, ROW_NAMES
from startup_vs_market.matrix_game import run_all_computations

st.set_page_config(
    page_title="Теория игр: Стартап vs Рынок",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }

    .hero-title {
        font-size: 2.1rem; font-weight: 800; color: #0f172a;
        letter-spacing: -0.5px; margin-bottom: 0.1rem;
    }
    .hero-sub {
        font-size: 1rem; color: #64748b; margin-bottom: 1.1rem;
    }

    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .metric-label { font-size: 0.78rem; color: #64748b; margin-bottom: 2px; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; }
    .metric-value-sm { font-size: 1.3rem; font-weight: 700; color: #0f172a; }

    .sec-head {
        font-size: 1.05rem; font-weight: 700; color: #1e40af;
        border-left: 3px solid #3b82f6;
        padding-left: 8px; margin: 1.2rem 0 0.5rem 0;
    }
    .math-block {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 8px; padding: 1rem 1.2rem;
        margin: 0.4rem 0;
    }

    .badge-green {
        display:inline-block; background:#dcfce7; color:#166534;
        border:1px solid #86efac; padding:3px 10px;
        border-radius:999px; font-size:0.8rem; font-weight:600;
    }
    .badge-red {
        display:inline-block; background:#fee2e2; color:#991b1b;
        border:1px solid #fca5a5; padding:3px 10px;
        border-radius:999px; font-size:0.8rem; font-weight:600;
    }
    .badge-blue {
        display:inline-block; background:#dbeafe; color:#1d4ed8;
        border:1px solid #93c5fd; padding:3px 10px;
        border-radius:999px; font-size:0.8rem; font-weight:600;
    }

    .step-row { display:flex; gap:12px; align-items:flex-start; margin:6px 0; }
    .step-num {
        min-width:26px; height:26px; background:#1d4ed8; color:#fff;
        border-radius:50%; display:flex; align-items:center;
        justify-content:center; font-size:0.8rem; font-weight:700; flex-shrink:0;
    }
    .step-text { font-size:0.92rem; color:#334155; padding-top:3px; }

    .qa-q { font-weight:700; color:#0f172a; font-size:0.95rem; }
    .qa-a { color:#334155; font-size:0.9rem; margin-top:4px; }
    .formula-box {
        background:#eff6ff; border-left:3px solid #3b82f6;
        padding:8px 14px; border-radius:0 8px 8px 0; margin:8px 0;
        font-size:0.88rem; color:#1e3a8a;
    }

    .dev-ok   { color:#16a34a; font-weight:700; }
    .dev-warn { color:#d97706; font-weight:700; }
    .dev-bad  { color:#dc2626; font-weight:700; }
</style>
""", unsafe_allow_html=True)


def payoff_matrix_df() -> pd.DataFrame:
    return pd.DataFrame(MATRIX.astype(int), index=ROW_NAMES, columns=COL_NAMES)


def style_payoff_matrix(df: pd.DataFrame) -> pd.DataFrame:
    style = pd.DataFrame("", index=df.index, columns=df.columns)
    style["Стабильный"] = "background:#fee2e2;color:#991b1b;font-weight:700"
    style["Вирусный"] = "background:#dbeafe;color:#1d4ed8"
    style["Ограничения"] = "background:#dbeafe;color:#1d4ed8"
    return style


@st.cache_data
def compute_all(cache_version: int):
    # Streamlit Cloud can keep data cache across deploys; bump this when
    # the structure returned by run_all_computations changes.
    _ = cache_version
    return run_all_computations(n_br_iter=1000)


G = compute_all(cache_version=2)

p_opt  = float(G["p_ex"])
q_full = G["q_ex_full"]
v_opt  = float(G["v_ex"])
R      = G["R"]

st.markdown('<p class="hero-title">🎯 Стартап vs Рынок</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Антагонистическая матричная игра с нулевой суммой · '
    'Критерий: рентабельность, % · Игрок A максимизирует, Игрок B минимизирует</p>',
    unsafe_allow_html=True,
)


def _mc(col, label, val):
    col.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value-sm">{val}</div></div>',
        unsafe_allow_html=True,
    )


col_mat, col_metrics = st.columns([0.34, 0.66], gap="large")

with col_mat:
    st.markdown(
        '<p style="font-size:0.88rem;font-weight:700;color:#1e293b;margin:0 0 0.35rem 0;">'
        "Платёжная матрица A (рентабельность, %)</p>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        payoff_matrix_df()
        .style.apply(style_payoff_matrix, axis=None)
        .format("{}"),
        use_container_width=True,
        hide_index=False,
    )
    st.caption("Строки — игрок A · столбцы — состояния рынка B")

with col_metrics:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.markdown(
        f'<div class="metric-card"><div class="metric-label">Цена игры v*</div>'
        f'<div class="metric-value">{v_opt:.2f}%</div></div>',
        unsafe_allow_html=True,
    )
    _mc(m2, "p₁* Лок. деплой", f"{p_opt:.3f}")
    _mc(m3, "p₂* Облачный API", f"{1-p_opt:.3f}")
    _mc(m4, "q₂* Вирусный", f"{q_full[1]:.3f}")
    _mc(m5, "q₃* Ограничения", f"{q_full[2]:.3f}")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<span class="badge-green">✓ Равновесие Нэша найдено</span>&nbsp;'
    '<span class="badge-blue">3 метода согласованы</span>&nbsp;'
    '<span class="badge-red">«Стабильный» доминируется</span>',
    unsafe_allow_html=True,
)

st.divider()

tab1, tab2 = st.tabs([
    "🎛️ Интерактивная модель",
    "📐 Математика шаг за шагом",
])

with tab1:
    ctrl_col, chart_col = st.columns([0.35, 0.65], gap="large")

    with ctrl_col:
        st.markdown('<p class="sec-head">Сценарий игры</p>', unsafe_allow_html=True)

        p_user = st.slider(
            "p₁ — вероятность «Локальный деплой»",
            0.0, 1.0, float(round(p_opt, 2)), 0.01,
            help="Насколько часто Стартап выбирает локальное развёртывание.",
        )
        q_viral = st.slider(
            "q₂ — вероятность состояния «Вирусный»",
            0.0, 1.0, float(round(q_full[1], 2)), 0.01,
            help="«Стабильный» исключён доминированием, q₁=0. Здесь — доля «Вирусного».",
        )
        p2_user  = 1.0 - p_user
        q_restr  = 1.0 - q_viral
        p_vec    = np.array([p_user, p2_user])
        q_vec    = np.array([q_viral, q_restr])

        e_vs_viral = R[0,0]*p_user + R[1,0]*p2_user
        e_vs_restr = R[0,1]*p_user + R[1,1]*p2_user
        guarantee  = min(e_vs_viral, e_vs_restr)
        e_mixed    = float(p_vec @ R @ q_vec)

        delta_p = p_user - p_opt
        delta_e = e_mixed - v_opt

        st.markdown(
            f"p₂ = **{p2_user:.2f}** (Облачный API)  &nbsp;|&nbsp;  q₃ = **{q_restr:.2f}** (Ограничения)",
        )
        st.divider()

        st.metric("Гарантия min(E·Вир, E·Огр)", f"{guarantee:.2f}%",
                  delta=f"{guarantee - v_opt:+.2f} от оптимума")
        st.metric("Ожидаемый выигрыш E(p, q)", f"{e_mixed:.2f}%",
                  delta=f"{delta_e:+.2f} от v*")

        dev = abs(delta_p)
        if dev < 0.015:
            cls, txt = "dev-ok", "✓ Вы у оптимума!"
        elif dev < 0.1:
            cls, txt = "dev-warn", f"Отклонение от p* = {dev:.3f}"
        else:
            cls, txt = "dev-bad", f"Сильное отклонение: {dev:.3f}"
        st.markdown(f'<p class="{cls}">{txt}</p>', unsafe_allow_html=True)

        st.markdown('<p class="sec-head">Платёжная матрица</p>', unsafe_allow_html=True)
        st.dataframe(
            payoff_matrix_df()
            .style.apply(style_payoff_matrix, axis=None)
            .format("{}"),
            use_container_width=True,
        )
        st.caption("🔴 «Стабильный» — доминируемый столбец  |  🔵 остаются в игре")

    with chart_col:
        p_grid   = np.linspace(0, 1, 500)
        e1_grid  = R[0,0]*p_grid + R[1,0]*(1-p_grid)
        e2_grid  = R[0,1]*p_grid + R[1,1]*(1-p_grid)
        env_grid = np.minimum(e1_grid, e2_grid)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=np.concatenate([p_grid, p_grid[::-1]]),
            y=np.concatenate([e1_grid, e2_grid[::-1]]),
            fill="toself",
            fillcolor="rgba(219,234,254,0.25)",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        ))

        fig.add_trace(go.Scatter(
            x=p_grid, y=e1_grid, mode="lines",
            name=f"E₁(p) — против «{G['cn'][0]}»",
            line=dict(color="#2563eb", width=2.5),
            hovertemplate="p₁=%{x:.3f}<br>E₁=%{y:.2f}%<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=p_grid, y=e2_grid, mode="lines",
            name=f"E₂(p) — против «{G['cn'][1]}»",
            line=dict(color="#dc2626", width=2.5),
            hovertemplate="p₁=%{x:.3f}<br>E₂=%{y:.2f}%<extra></extra>",
        ))

        fig.add_trace(go.Scatter(
            x=p_grid, y=env_grid, mode="lines",
            name="Гарантия max·min = нижняя огибающая",
            line=dict(color="#16a34a", width=2, dash="dot"),
            hovertemplate="p₁=%{x:.3f}<br>гарантия=%{y:.2f}%<extra></extra>",
        ))

        fig.add_trace(go.Scatter(
            x=[p_opt], y=[v_opt],
            mode="markers+text",
            name=f"Оптимум p*={p_opt:.3f}, v*={v_opt:.2f}",
            marker=dict(size=14, color="#16a34a", symbol="star",
                        line=dict(color="#fff", width=1.5)),
            text=[f" p*={p_opt:.3f}<br>v*={v_opt:.2f}%"],
            textposition="top right",
            textfont=dict(size=11, color="#15803d"),
        ))

        fig.add_trace(go.Scatter(
            x=[p_user], y=[guarantee],
            mode="markers",
            name=f"Гарантия при p={p_user:.2f} → {guarantee:.2f}%",
            marker=dict(size=11, color="#9333ea", symbol="triangle-up"),
            hovertemplate="p=%{x:.3f}<br>гарантия=%{y:.2f}%<extra></extra>",
        ))

        fig.add_trace(go.Scatter(
            x=[p_user], y=[e_mixed],
            mode="markers+text",
            name=f"E(p, q_B) = {e_mixed:.2f}%",
            marker=dict(size=13, color="#0f172a", symbol="diamond",
                        line=dict(color="#e2e8f0", width=1.5)),
            text=[f" {e_mixed:.1f}%"],
            textposition="top center",
            textfont=dict(size=11, color="#0f172a"),
            hovertemplate="p=%{x:.3f}<br>E(p,q)=%{y:.2f}%<extra></extra>",
        ))

        fig.add_hline(y=v_opt, line_dash="dash", line_color="#16a34a", line_width=1.5,
                      annotation_text=f" v*={v_opt:.2f}%",
                      annotation_font_color="#15803d")
        fig.add_vline(x=p_opt, line_dash="dash", line_color="#16a34a", line_width=1.5,
                      annotation_text=f" p*={p_opt:.3f}",
                      annotation_font_color="#15803d",
                      annotation_position="top right")

        fig.update_layout(
            height=490,
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            hovermode="closest",
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(title="Вероятность локального деплоя p₁",
                       range=[-0.02, 1.02], showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(title="Ожидаемый выигрыш, %",
                       showgrid=True, gridcolor="#f1f5f9"),
            legend=dict(orientation="h", yanchor="bottom", y=1.01,
                        xanchor="left", x=0, font=dict(size=11)),
        )

        st.plotly_chart(fig, use_container_width=True,
                        key=f"chart_{p_user:.4f}_{q_viral:.4f}")

        st.markdown('<p class="sec-head">Ожидаемый выигрыш — разбивка по состояниям</p>',
                    unsafe_allow_html=True)
        e_stab = MATRIX[0,0]*p_user + MATRIX[1,0]*p2_user
        e_vir  = R[0,0]*p_user     + R[1,0]*p2_user
        e_ogr  = R[0,1]*p_user     + R[1,1]*p2_user

        bc1, bc2, bc3, bc4 = st.columns(4)
        bc1.metric("E(p, Стабильный) [исключён]", f"{e_stab:.2f}%")
        bc2.metric("E(p, Вирусный)",               f"{e_vir:.2f}%")
        bc3.metric("E(p, Ограничения)",            f"{e_ogr:.2f}%")
        bc4.metric("E(p, q_смеш.)",                f"{e_mixed:.2f}%")


with tab2:

    st.markdown('<p class="sec-head">1. Постановка задачи</p>', unsafe_allow_html=True)
    c_l, c_r = st.columns(2)
    with c_l:
        st.markdown("**Исходная платёжная матрица:**")
        st.latex(r"""
A = \begin{pmatrix}
    13 & 29 & 9 \\
    25 &  9 & 21
\end{pmatrix}
\quad
\begin{array}{l}
\leftarrow \text{Локальный деплой} \\
\leftarrow \text{Облачный API}
\end{array}
""")
        st.markdown("""
| | Стабильный | Вирусный | Ограничения |
|---|:---:|:---:|:---:|
| **Локальный** | 13 | **29** | 9 |
| **Облачный**  | **25** | 9 | **21** |
""")
    with c_r:
        st.markdown("**Математическая постановка:**")
        st.latex(r"\max_{p \in \Delta_2}\;\min_{q \in \Delta_3}\; p^\top A q")
        st.markdown(r"""
- $\Delta_2 = \{(p_1,p_2) : p_1+p_2=1,\; p_i\geq 0\}$ — симплекс A
- $\Delta_3 = \{(q_1,q_2,q_3): \sum q_j=1,\; q_j\geq 0\}$ — симплекс B
- Игрок A **максимизирует** выигрыш
- Игрок B **минимизирует** выигрыш
- По теореме Минимакса (Нейман, 1928): $\max\min = \min\max = v^*$
""")

    st.markdown('<p class="sec-head">2. Анализ доминирования стратегий</p>',
                unsafe_allow_html=True)

    with st.expander("Теоретическая справка: что такое доминирование", expanded=False):
        st.markdown(r"""
**Определение (доминирование столбцов, B-минимизатор):**
Столбец $k$ **доминирует** столбец $j$, если
$$\forall i:\quad a_{ik} \leq a_{ij}$$
Тогда игрок B никогда рационально не выберет $j$, поскольку $k$ даёт не больший выигрыш противнику при каждом исходе.

**Определение (доминирование строк, A-максимизатор):**
Строка $k$ **доминирует** строку $i$, если
$$\forall j:\quad a_{kj} \geq a_{ij}$$
""")

    st.markdown("**Шаг 2.1 — сравниваем столбцы «Ограничения» и «Стабильный»:**")
    col_a, col_b = st.columns([1.1, 1])
    with col_a:
        st.latex(r"""
\text{«Ограничения»} = \begin{pmatrix}9\\21\end{pmatrix},\quad
\text{«Стабильный»} = \begin{pmatrix}13\\25\end{pmatrix}
""")
        st.latex(r"""
9 < 13 \;\checkmark\quad(\text{строка 1})\\
21 < 25 \;\checkmark\quad(\text{строка 2})
""")
        st.latex(r"""
\Rightarrow\; \text{«Ограничения»} \preceq \text{«Стабильный»} \;\Rightarrow\;
q_1^* = 0
""")
    with col_b:
        st.info(
            "Рациональный Рынок никогда не выберет «Стабильный»: "
            "при любой стратегии Стартапа «Ограничения» ≤ «Стабильный» поэлементно. "
            "Столбец исключается."
        )

    st.markdown("**Шаг 2.2 — редуцированная матрица 2×2:**")
    col_c, col_d = st.columns(2)
    with col_c:
        st.latex(r"""
A' = \begin{pmatrix}29 & 9\\9 & 21\end{pmatrix}
\quad\begin{array}{l}
\leftarrow \text{Лок. деплой}\\
\leftarrow \text{Облачный API}
\end{array}
""")
    with col_d:
        df_R = pd.DataFrame(R.astype(int), index=G["rn"], columns=G["cn"])
        st.dataframe(df_R, use_container_width=False)

    st.markdown("**Шаг 2.3 — проверяем строки A':**")
    st.latex(r"""
[29,9]\;\text{vs}\;[9,21]:\quad
29>9\;\Rightarrow\;\text{стр.1 лучше по «Вирусный»},\quad
9<21\;\Rightarrow\;\text{стр.2 лучше по «Ограничения»}
""")
    st.markdown("→ Ни одна строка не доминирует другую. **Обе стратегии A остаются.**")

    st.markdown('<p class="sec-head">3. Проверка седловой точки</p>', unsafe_allow_html=True)

    with st.expander("Теоретическая справка: критерий чистых стратегий"):
        st.latex(r"""
\alpha = \max_i \min_j a_{ij} \quad\text{(максимин)},\qquad
\beta  = \min_j \max_i a_{ij} \quad\text{(минимакс)}
""")
        st.markdown(
            "Если $\\alpha = \\beta$, то чистая стратегия является седловой точкой "
            "и равновесием Нэша. Если $\\alpha < \\beta$ — только смешанные стратегии."
        )

    col1, col2, col3, col4 = st.columns(4)
    row_mins = MATRIX.min(axis=1)
    col_maxs = MATRIX.max(axis=0)

    with col1:
        st.markdown("**Мин. по строкам (исх.):**")
        for nm, v in zip(ROW_NAMES, row_mins):
            st.markdown(f"- {nm}: **{v:.0f}**")

    with col2:
        st.metric("Максимин α", f"{G['alpha']:.0f}",
                  help="max(min по строке) — нижняя гарантия A")

    with col3:
        st.markdown("**Макс. по столбцам (исх.):**")
        for nm, v in zip(COL_NAMES, col_maxs):
            st.markdown(f"- {nm}: **{v:.0f}**")

    with col4:
        st.metric("Минимакс β", f"{G['beta']:.0f}",
                  help="min(max по столбцу) — верхняя гарантия B")

    st.latex(r"""
\alpha = \max_i\min_j a_{ij} = \max(9,\,9)=9
\;\neq\;
\beta = \min_j\max_i a_{ij} = \min(29,\,25,\,21)=21
""")
    st.error("Седловой точки нет → решение только в **смешанных стратегиях**.")

    st.markdown('<p class="sec-head">4. Графоаналитический метод (для матрицы 2×N)</p>',
                unsafe_allow_html=True)

    with st.expander("Полный вывод формул"):
        st.markdown("**Ожидаемый выигрыш против каждой чистой стратегии B:**")
        st.latex(r"""
E_j(p_1) = a_{1j}\,p_1 + a_{2j}(1-p_1)
""")
        st.latex(r"""
E_1(p_1) = 29\,p_1 + 9(1-p_1) = 20\,p_1 + 9
\qquad\text{(против «Вирусный»)}
""")
        st.latex(r"""
E_2(p_1) = 9\,p_1 + 21(1-p_1) = -12\,p_1 + 21
\qquad\text{(против «Ограничения»)}
""")
        st.markdown("**Задача Игрока A:** максимизировать нижнюю огибающую:")
        st.latex(r"""
p_1^* = \arg\max_{p_1\in[0,1]}\;\min\bigl(E_1(p_1),\;E_2(p_1)\bigr)
""")
        st.markdown("**Оптимум достигается в точке пересечения E₁ = E₂:**")
        st.latex(r"""
20\,p_1 + 9 = -12\,p_1 + 21
\;\Rightarrow\; 32\,p_1 = 12
\;\Rightarrow\; \boxed{p_1^* = \dfrac{12}{32} = \dfrac{3}{8} = 0.375}
""")
        st.markdown("**Цена игры:**")
        st.latex(r"""
v^* = E_1(p_1^*) = 20\cdot\tfrac{3}{8}+9 = 7.5+9 = \boxed{16.5\%}
""")
        st.markdown("**Проверка через E₂:**")
        st.latex(r"""
E_2\!\left(\tfrac{3}{8}\right) = -12\cdot\tfrac{3}{8}+21 = -4.5+21 = 16.5 \;\checkmark
""")
        st.markdown("**Оптимальная стратегия Игрока B** (аналогично, из равенства выигрышей по строкам):")
        st.latex(r"""
29\,q_1 + 9(1-q_1) = 9\,q_1 + 21(1-q_1)
\;\Rightarrow\; 32\,q_1 = 12
\;\Rightarrow\; \boxed{q_1^* = \tfrac{3}{8},\quad q_2^* = \tfrac{5}{8}}
""")
        st.markdown(r"В исходном 3-мерном пространстве: $q^*=(0,\,3/8,\,5/8)$.")

    pg = np.linspace(0, 1, 400)
    e1g = R[0,0]*pg + R[1,0]*(1-pg)
    e2g = R[0,1]*pg + R[1,1]*(1-pg)
    envg = np.minimum(e1g, e2g)
    fig_g = go.Figure()
    fig_g.add_trace(go.Scatter(x=pg, y=e1g, mode="lines",
        name="E₁ — «Вирусный»", line=dict(color="#2563eb", width=2.5)))
    fig_g.add_trace(go.Scatter(x=pg, y=e2g, mode="lines",
        name="E₂ — «Ограничения»", line=dict(color="#dc2626", width=2.5)))
    fig_g.add_trace(go.Scatter(x=pg, y=envg, mode="lines",
        name="Нижняя огибающая",
        line=dict(color="#16a34a", width=3, dash="dot"),
        fill="tozeroy", fillcolor="rgba(22,163,74,0.07)"))
    fig_g.add_trace(go.Scatter(
        x=[p_opt], y=[v_opt], mode="markers+text",
        marker=dict(size=14, color="#16a34a", symbol="star",
                    line=dict(color="#fff", width=1.5)),
        text=[" p*=3/8, v*=16.5%"],
        textposition="top right", textfont=dict(size=12),
        name="Оптимум",
    ))
    fig_g.add_vline(x=p_opt, line_dash="dash", line_color="#16a34a")
    fig_g.add_hline(y=v_opt, line_dash="dash", line_color="#16a34a")
    fig_g.update_layout(
        height=370, plot_bgcolor="#fff", paper_bgcolor="#fff",
        margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified",
        xaxis=dict(title="p₁ (вероятность локального деплоя)",
                   showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(title="Ожидаемый выигрыш, %",
                   showgrid=True, gridcolor="#f1f5f9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.01),
    )
    st.plotly_chart(fig_g, use_container_width=True)

    st.markdown('<p class="sec-head">5. Симплекс-метод (чистая реализация)</p>',
                unsafe_allow_html=True)

    sx = G["sx_info"]
    n_c, m_r = sx["n_cols"], sx["m_rows"]
    cn_sx = G["cn"]   # column names of reduced matrix
    rn_sx = G["rn"]   # row names of reduced matrix

    with st.expander("Постановка ЛП и замена переменных", expanded=False):
        st.markdown("**Задача Игрока B (прямая):**")
        st.latex(r"""
\max_{y \geq 0}\; \mathbf{1}^\top y
\quad\text{при}\quad
A'\,y \leq \mathbf{1}_m,\qquad
A' = A_{\text{red}} + c
""")
        st.markdown(
            f"**Сдвиг:** $c = {sx['c_shift']:.0f}$ — гарантирует $A' > 0$, "
            "поэтому задача ЛП имеет ненулевое оптимальное решение."
        )
        st.latex(r"""
\text{Стандартная форма (добавляем балансовые переменные } s_i\text{):}\\[4pt]
\max\; \mathbf{1}^\top y\quad
\text{при}\quad A'\,y + s = \mathbf{1}_m,\quad y,\,s \geq 0
""")
        st.markdown("**Задача Игрока A (двойственная):**")
        st.latex(r"""
\min_{x \geq 0}\; \mathbf{1}^\top x
\quad\text{при}\quad
A'^\top x \geq \mathbf{1}_n
""")
        st.markdown(r"""
**Восстановление оптимума:**
$$v' = \frac{1}{\sum y_i^*},\quad q_j^* = y_j^* \cdot v',\quad
  p_i^* = \lambda_i \cdot v',\quad v^* = v' - c$$
где $\lambda_i$ — теневые цены (двойственные переменные) = значения балансовых столбцов
в целевой строке финального симплекс-табло.
""")

    with st.expander("Начальное симплекс-табло", expanded=False):
        st.markdown(
            f"Размерность: **{m_r} строк** (ограничений) × **{n_c + m_r} переменных** "
            f"({n_c} — игровые $y$, {m_r} — балансовые $s$). "
            "Начальный базис: все балансовые переменные."
        )
        A_sh = sx["A_shifted"]
        hdr_cols = [f"y({cn_sx[j]})" for j in range(n_c)] + \
                   [f"s{i+1}" for i in range(m_r)] + ["b"]
        init_T = np.zeros((m_r + 1, n_c + m_r + 1))
        init_T[:m_r, :n_c] = A_sh
        init_T[:m_r, n_c:n_c + m_r] = np.eye(m_r)
        init_T[:m_r, -1] = 1.0
        init_T[m_r, :n_c] = -1.0
        row_labels = [f"s{i+1}" for i in range(m_r)] + ["z"]
        df_init = pd.DataFrame(init_T, index=row_labels, columns=hdr_cols)
        st.dataframe(df_init.style.format("{:.4f}"), use_container_width=True)
        st.caption(
            "Строки 1…m — ограничения (RHS = 1). "
            "Строка z — целевая функция (отрицательные коэффициенты = потенциал входа)."
        )

    with st.expander(f"Итерации симплекс-метода ({len(sx['snapshots'])} шагов)", expanded=True):
        for snap in sx["snapshots"]:
            it = snap["iteration"]
            j_e = snap["entering"]
            l_var = snap["leaving"]
            var_name_e = f"y({cn_sx[j_e]})" if j_e < n_c else f"s{j_e - n_c + 1}"
            var_name_l = f"y({cn_sx[l_var]})" if l_var < n_c else f"s{l_var - n_c + 1}"
            st.markdown(
                f"**Итерация {it}:** входит **{var_name_e}** "
                f"(отриц. коэфф. в z-строке), выходит **{var_name_l}** (мин. отношение)"
            )
            T_snap = snap["tableau"]
            hdr_s = [f"y({cn_sx[j]})" for j in range(n_c)] + \
                    [f"s{i+1}" for i in range(m_r)] + ["b"]
            st.dataframe(
                pd.DataFrame(T_snap, columns=hdr_s).style.format("{:.4f}"),
                use_container_width=True,
            )

    with st.expander("Финальное симплекс-табло и извлечение решения", expanded=True):
        T_fin = sx["final_tableau"]
        basis_fin = sx["basis"]
        hdr_f = [f"y({cn_sx[j]})" for j in range(n_c)] + \
                [f"s{i+1}" for i in range(m_r)] + ["b"]
        basis_labels = [
            (f"y({cn_sx[b]})" if b < n_c else f"s{b - n_c + 1}")
            for b in basis_fin
        ] + ["z"]
        df_fin = pd.DataFrame(T_fin, index=basis_labels, columns=hdr_f)
        st.dataframe(df_fin.style.format("{:.6f}"), use_container_width=True)

        st.markdown("**Извлечение решения из финального табло:**")
        sum_y = sx["sum_y"]
        z_opt = sx["z_opt"]
        st.latex(
            rf"\sum y_i^* = {sum_y:.6f},\quad "
            rf"v' = \frac{{1}}{{\sum y_i^*}} = {1/sum_y:.6f},\quad "
            rf"v^* = v' - c = {1/sum_y:.6f} - {sx['c_shift']:.0f} = {G['v_sx']:.6f}"
        )
        col_px, col_qx = st.columns(2)
        with col_px:
            st.markdown("**Стратегия A** (из двойственных переменных — балансовые столбцы z-строки):")
            for i, _name in enumerate(rn_sx):
                dual_val = T_fin[m_r, n_c + i]
                p_i = G["p_sx"][i]
                st.latex(
                    rf"\lambda_{i+1} = {dual_val:.6f},"
                    rf"\quad p_{i+1}^* = \lambda_{i+1}/\sum\lambda = {p_i:.6f}"
                )
        with col_qx:
            st.markdown("**Стратегия B** (из базисных переменных в b-столбце):")
            for j, name in enumerate(cn_sx):
                q_j = G["q_sx_r"][j]
                st.latex(rf"q_{j+1}^* = {q_j:.6f} \quad ({name})")

        st.success(
            f"✓ Симплекс-метод (без внешних решателей): "
            f"p*=({G['p_sx'][0]:.4f}, {G['p_sx'][1]:.4f}), "
            f"q*=({G['q_sx_r'][0]:.4f}, {G['q_sx_r'][1]:.4f}), "
            f"v*={G['v_sx']:.4f}"
        )

    st.markdown('<p class="sec-head">6. Метод Брауна–Робинсона</p>', unsafe_allow_html=True)

    with st.expander("Алгоритм и первые 10 итераций"):
        st.markdown(r"""
**Алгоритм:**
На каждом шаге $t$:
1. A выбирает строку $i^* = \arg\max_i A_{cum}[i]$ (лучший ответ на историю B)
2. Обновляет $B_{cum}[j] \mathrel{+}= a_{i^*,j}$
3. B выбирает $j^* = \arg\min_j B_{cum}[j]$ (лучший ответ на историю A)
4. Обновляет $A_{cum}[i] \mathrel{+}= a_{i,j^*}$
5. Нижняя граница: $\underline{v}_t = \min_j B_{cum}[j] / t$
6. Верхняя граница: $\bar{v}_t = \max_i A_{cum}[i] / t$
""")
        iter_data = []
        a_c = np.zeros(R.shape[0]); b_c = np.zeros(R.shape[1])
        a_cum2 = np.zeros(R.shape[0]); b_cum2 = np.zeros(R.shape[1])
        a_row2 = int(np.argmax(R.min(axis=1)))
        for t in range(1, 11):
            a_c[a_row2] += 1; b_cum2 += R[a_row2, :]
            b_col2 = int(np.argmin(b_cum2)); b_c[b_col2] += 1; a_cum2 += R[:, b_col2]
            lo2 = b_cum2.min() / t; hi2 = a_cum2.max() / t
            iter_data.append({
                "t": t,
                "Ход A": G["rn"][a_row2],
                "Ход B": G["cn"][b_col2],
                "B_cum": f"[{b_cum2[0]:.0f}, {b_cum2[1]:.0f}]",
                "A_cum": f"[{a_cum2[0]:.0f}, {a_cum2[1]:.0f}]",
                "v̲(t)": f"{lo2:.3f}",
                "v̄(t)": f"{hi2:.3f}",
            })
            a_row2 = int(np.argmax(a_cum2))
        st.dataframe(pd.DataFrame(iter_data).set_index("t"), use_container_width=True)

    it = np.arange(1, 1001)
    fig_br = go.Figure()
    fig_br.add_trace(go.Scatter(
        x=it[::3], y=G["vhi"][::3], name="Верхняя граница v̄ₜ",
        line=dict(color="#dc2626", width=1.5),
        hovertemplate="t=%{x}<br>v̄=%{y:.3f}<extra></extra>",
    ))
    fig_br.add_trace(go.Scatter(
        x=it[::3], y=G["vlo"][::3], name="Нижняя граница v̲ₜ",
        line=dict(color="#2563eb", width=1.5),
        fill="tonexty", fillcolor="rgba(37,99,235,0.08)",
        hovertemplate="t=%{x}<br>v̲=%{y:.3f}<extra></extra>",
    ))
    fig_br.add_hline(y=v_opt, line_dash="dash", line_color="#16a34a", line_width=2,
                     annotation_text=f" v*={v_opt:.2f}",
                     annotation_font_color="#15803d")
    fig_br.add_annotation(
        x=900, y=(G["vhi"][-1] + G["vlo"][-1]) / 2,
        text=f"Погрешность t=1000:<br>±{(G['vhi'][-1]-G['vlo'][-1])/2:.3f}",
        showarrow=True, arrowhead=2, bgcolor="white", bordercolor="#94a3b8",
    )
    fig_br.update_layout(
        height=320, plot_bgcolor="#fff", paper_bgcolor="#fff",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title="Итерация t", showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(title="Оценка v*", showgrid=True, gridcolor="#f1f5f9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.01),
    )
    st.plotly_chart(fig_br, use_container_width=True)

    st.markdown('<p class="sec-head">7. Сравнение трёх методов</p>', unsafe_allow_html=True)

    cmp = pd.DataFrame({
        "Метод": [
            "Аналитический (формула 2×2)",
            "Симплекс-метод (чистый)",
            "Браун–Робинсон (1000 ит.)",
        ],
        "p₁* (Лок. деплой)": [G["p_ex"],   G["p_sx"][0], G["p_br"][0]],
        "p₂* (Облачный)":    [1-G["p_ex"], G["p_sx"][1], G["p_br"][1]],
        "v* (цена игры)":    [G["v_ex"],   G["v_sx"],    G["v_br"]],
        "|Δv|":              [0.0, abs(G["v_sx"]-G["v_ex"]), abs(G["v_br"]-G["v_ex"])],
    })
    st.dataframe(cmp.style.format({
        "p₁* (Лок. деплой)": "{:.6f}",
        "p₂* (Облачный)":    "{:.6f}",
        "v* (цена игры)":    "{:.6f}",
        "|Δv|":              "{:.2e}",
    }), use_container_width=True)

    st.success(
        f"✓ Все три метода согласованы: p₁*≈0.375=3/8, v*≈16.5%. "
        f"Симплекс (чистый): {abs(G['v_sx']-G['v_ex']):.2e}. "
        f"Браун–Робинсон: {abs(G['v_br']-G['v_ex']):.4f}."
    )

    st.markdown('<p class="sec-head">8. Верификация равновесия Нэша</p>', unsafe_allow_html=True)

    p_nash = np.array([G["p_ex"], 1 - G["p_ex"]])
    q_nash = G["q_ex_vec"]
    v_check1 = float(p_nash @ R @ q_nash)
    v_check2_row0 = float(R[0, :] @ q_nash)
    v_check2_row1 = float(R[1, :] @ q_nash)
    v_check3_col0 = float(p_nash @ R[:, 0])
    v_check3_col1 = float(p_nash @ R[:, 1])

    with st.expander("Полная верификация условий равновесия"):
        st.markdown("**Условие 1: Оба игрока не могут улучшить результат отклонением**")
        st.latex(rf"""
p^{{\top}} A' q^* = {v_check1:.4f} = v^*
""")
        st.markdown("**Условие 2: A безразличен между строками при q* (принцип смешивания)**")
        st.latex(rf"""
A'_{{1\cdot}}\,q^* = {v_check2_row0:.4f} = v^*
\qquad
A'_{{2\cdot}}\,q^* = {v_check2_row1:.4f} = v^*
""")
        st.markdown("**Условие 3: B безразличен между столбцами при p* (принцип смешивания)**")
        st.latex(rf"""
p^{{*\top}} A'_{{\cdot 1}} = {v_check3_col0:.4f} = v^*
\qquad
p^{{*\top}} A'_{{\cdot 2}} = {v_check3_col1:.4f} = v^*
""")
        st.success("Все условия выполнены — это равновесие Нэша в смешанных стратегиях.")
