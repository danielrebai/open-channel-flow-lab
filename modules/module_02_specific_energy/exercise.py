"""Module 02: automatically generated, fully worked specific-energy exercises."""
import math
import random

import plotly.graph_objects as go
import streamlit as st

G = 9.81


def critical_depth(q):
    return (q * q / G) ** (1.0 / 3.0)


def energy(h, q):
    return h + q * q / (2.0 * G * h * h)


def two_depths(q, E):
    """Bisection on either side of the minimum of E(h)."""
    hc = critical_depth(q)
    ec = 1.5 * hc
    if E <= ec:
        raise ValueError("Specific energy must exceed its critical minimum.")
    a, b = 1e-10, hc
    for _ in range(100):
        m = (a + b) / 2
        if energy(m, q) > E:
            a = m
        else:
            b = m
    super_depth = (a + b) / 2
    a, b = hc, E
    for _ in range(100):
        m = (a + b) / 2
        if energy(m, q) < E:
            a = m
        else:
            b = m
    return super_depth, (a + b) / 2


def make_case(kind=None):
    rng = random.SystemRandom()
    B = round(rng.uniform(3.0, 8.0), 1)
    Q = round(rng.uniform(5.0, 16.0), 1)
    q = Q / B
    hc = critical_depth(q)
    kind = rng.choice([1, 2, 3, 4]) if kind is None else kind
    if kind == 1:
        E = round(rng.uniform(1.7, 2.7) * hc, 2)
        if E <= 1.5 * hc:
            E = round(1.8 * hc, 2)
        return dict(kind=1, B=B, Q=Q, E=E)
    if kind == 3:
        # Keep E fixed and change q. Both states remain on the same flow branch.
        E = round(rng.uniform(1.9, 2.7) * hc, 2)
        q2 = round(q * rng.uniform(0.55, 1.35), 3)
        if E <= 1.65 * critical_depth(q2):
            q2 = round(q * 0.70, 3)
        return dict(kind=3, B=B, Q=Q, E=E, q2=q2,
                    branch=rng.choice(['subcritical', 'supercritical']))
    if kind == 4:
        E1 = round(rng.uniform(1.9, 2.5) * hc, 2)
        E2 = round(E1 * rng.uniform(0.80, 1.35), 2)
        if E2 <= 1.65 * hc:
            E2 = round(1.85 * hc, 2)
        return dict(kind=4, B=B, Q=Q, E=E1, E2=E2,
                    branch=rng.choice(['subcritical', 'supercritical']))
    # Choose a well-separated branch and compute its alternate depth.
    h = round(hc * rng.choice([rng.uniform(0.37, 0.65), rng.uniform(1.55, 2.5)]), 3)
    return dict(kind=2, B=B, Q=Q, h=h)


def iterate_subcritical(q, E, hc, count=7):
    h = 2 * hc
    result = [h]
    for _ in range(count - 1):
        h = E - q * q / (2 * G * h * h)
        result.append(h)
    return result


def iterate_supercritical(q, E, hc, count=7):
    h = hc / 2
    result = [h]
    for _ in range(count - 1):
        h = math.sqrt(q * q / (2 * G * (E - h)))
        result.append(h)
    return result


def plot_energy(q, E, h_super, h_sub, hc, key):
    ymax = max(E * 1.15, h_sub * 1.25, hc * 2.0)
    h_min = max(0.015, min(h_super * 0.4, hc * 0.12))
    depths = [h_min + (ymax - h_min) * i / 450 for i in range(451)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=depths, y=[energy(h, q) for h in depths],
                             name="Specific energy E(h)", mode="lines",
                             line=dict(color="#2563eb", width=3)))
    fig.add_trace(go.Scatter(x=[0, ymax], y=[E, E], name="Assigned energy",
                             mode="lines", line=dict(color="#64748b", dash="dash")))
    fig.add_trace(go.Scatter(x=[h_super, h_sub], y=[E, E],
                             mode="markers+text", name="Alternate depths",
                             text=["Supercritical", "Subcritical"],
                             textposition=["bottom right", "top left"],
                             marker=dict(size=11, color=["#f59e0b", "#16a34a"])))
    fig.add_trace(go.Scatter(x=[hc], y=[1.5 * hc], mode="markers",
                             name="Critical point", marker=dict(color="#dc2626", size=13)))
    locus_x = [ymax * i / 200 for i in range(201)]
    fig.add_trace(go.Scatter(x=locus_x, y=[1.5 * h for h in locus_x],
                             mode="lines", name="Critical locus: E = 3h/2",
                             line=dict(color="#dc2626", dash="dot")))
    fig.update_layout(title="Specific energy and alternate depths",
                      xaxis_title="Flow depth h [m]", yaxis_title="Specific energy E [m]",
                      xaxis=dict(range=[0, ymax]),
                      yaxis=dict(range=[0, max(E * 1.65, hc * 2.4)]),
                      height=510, legend=dict(orientation="h", y=-0.27),
                      margin=dict(t=60, b=75))
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.caption("Blue: specific-energy curve; grey: assigned energy; red: critical locus and critical point. "
               "The two intersections represent the two alternate depths.")



def plot_constant_energy(q, E, h_super, h_sub, hc, key):
    """Depth against specific discharge along the assigned-energy curve."""
    h_critical_locus = 2.0 * E / 3.0
    q_max = math.sqrt(G * h_critical_locus**3)
    depths = [E * i / 500 for i in range(501)]
    discharges = [h * math.sqrt(max(0.0, 2.0 * G * (E - h))) for h in depths]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=discharges, y=depths, mode="lines",
        name="Constant specific energy", line=dict(color="#2563eb", width=3)))
    fig.add_trace(go.Scatter(
        x=[q, q], y=[0, E], mode="lines", name="Assigned q = Q/B",
        line=dict(color="#64748b", dash="dash", width=2)))
    fig.add_trace(go.Scatter(
        x=[q, q], y=[h_super, h_sub], mode="markers+text",
        text=["Supercritical", "Subcritical"],
        textposition=["bottom left", "top left"],
        name="Alternate depths",
        marker=dict(size=12, color=["#f59e0b", "#16a34a"])))
    fig.add_trace(go.Scatter(
        x=[q_max], y=[h_critical_locus], mode="markers",
        name="Critical state at assigned E",
        marker=dict(size=13, color="#dc2626")))
    # Critical locus: q_c = sqrt(g h_c^3), independent of E.
    locus_h = [E * i / 500 for i in range(501)]
    fig.add_trace(go.Scatter(
        x=[math.sqrt(G * h**3) for h in locus_h], y=locus_h,
        mode="lines", name="Critical locus",
        line=dict(color="#dc2626", dash="dot", width=2)))
    fig.update_layout(
        title="Flow depth vs specific discharge at constant energy",
        xaxis_title="Specific discharge q = Q/B [m²/s]",
        yaxis_title="Flow depth h [m]",
        xaxis=dict(range=[0, max(q_max * 1.15, q * 1.3)]),
        yaxis=dict(range=[0, E * 1.08]),
        height=510, legend=dict(orientation="h", y=-0.27),
        margin=dict(t=60, b=75))
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.caption(
        "The vertical line q = Q/B intersects the constant-energy curve at the "
        "supercritical and subcritical alternate depths. The red marker is the "
        "maximum possible specific discharge at the assigned energy (critical flow).")

def plot_comparison(case, q1, E1, h1, q2, E2, h2):
    """Type 3: two E(h), one h(q). Type 4: one E(h), two h(q)."""
    kind = case["kind"]
    initial_color = "#64748b"
    final_color = "#2563eb"
    critical_color = "#dc2626"
    h_limit = 1.15 * max(E1, E2)
    h_grid = [h_limit * i / 600 for i in range(1, 601)]

    fig_e = go.Figure()
    if kind == 3:
        energy_curves = [
            (q1, "Initial q₁", initial_color, "dash"),
            (q2, "Final q₂", final_color, "solid"),
        ]
    else:
        energy_curves = [(q1, "Constant q", final_color, "solid")]

    for q, label, color, dash in energy_curves:
        fig_e.add_trace(go.Scatter(
            x=h_grid, y=[energy(h, q) for h in h_grid],
            mode="lines", name=label,
            line=dict(color=color, dash=dash, width=3),
        ))

    for E, label, color in (
        [(E1, "Constant E", "#64748b")] if kind == 3 else
        [(E1, "Initial E₁", initial_color), (E2, "Final E₂", final_color)]
    ):
        fig_e.add_trace(go.Scatter(
            x=[0, h_limit], y=[E, E], mode="lines", name=label,
            line=dict(color=color, dash="dot", width=1.5),
        ))

    for h, E, label, color in [
        (h1, E1, "Initial state", initial_color),
        (h2, E2, "Final state", final_color),
    ]:
        fig_e.add_trace(go.Scatter(
            x=[h], y=[E], mode="markers", name=label,
            marker=dict(size=12, color=color, line=dict(width=1, color="white")),
        ))

    fig_e.add_trace(go.Scatter(
        x=[0, h_limit], y=[0, 1.5 * h_limit],
        mode="lines", name="Critical locus", line=dict(color=critical_color, dash="dot"),
    ))
    for q in sorted({q1, q2}):
        hc = critical_depth(q)
        fig_e.add_trace(go.Scatter(
            x=[hc], y=[1.5 * hc], mode="markers",
            name="Critical state", showlegend=False,
            marker=dict(size=10, color=critical_color),
        ))
    fig_e.update_layout(
        title="Specific energy E vs depth h",
        xaxis_title="Depth h [m]", yaxis_title="Specific energy E [m]",
        xaxis=dict(range=[0, h_limit]),
        yaxis=dict(range=[0, max(E1, E2) * 1.65]),
        height=520, legend=dict(orientation="h", y=-0.28),
        margin=dict(t=60, b=75),
    )

    fig_q = go.Figure()
    if kind == 4:
        discharge_curves = [
            (E1, "Initial E₁", initial_color, "dash"),
            (E2, "Final E₂", final_color, "solid"),
        ]
    else:
        discharge_curves = [(E1, "Constant E", final_color, "solid")]

    for E, label, color, dash in discharge_curves:
        hs = [E * i / 500 for i in range(501)]
        qs = [h * math.sqrt(max(0.0, 2 * G * (E - h))) for h in hs]
        fig_q.add_trace(go.Scatter(
            x=qs, y=hs, mode="lines", name=label,
            line=dict(color=color, dash=dash, width=3),
        ))

    for q, label, color in (
        [(q1, "Constant q", "#64748b")] if kind == 4 else
        [(q1, "Initial q₁", initial_color), (q2, "Final q₂", final_color)]
    ):
        fig_q.add_trace(go.Scatter(
            x=[q, q], y=[0, h_limit], mode="lines", name=label,
            line=dict(color=color, dash="dot", width=1.5),
        ))

    for q, h, label, color in [
        (q1, h1, "Initial state", initial_color),
        (q2, h2, "Final state", final_color),
    ]:
        fig_q.add_trace(go.Scatter(
            x=[q], y=[h], mode="markers", name=label,
            marker=dict(size=12, color=color, line=dict(width=1, color="white")),
        ))

    locus_h = [h_limit * i / 400 for i in range(401)]
    fig_q.add_trace(go.Scatter(
        x=[math.sqrt(G * h**3) for h in locus_h], y=locus_h,
        mode="lines", name="Critical locus",
        line=dict(color=critical_color, dash="dot"),
    ))
    for E in sorted({E1, E2}):
        hc = 2 * E / 3
        fig_q.add_trace(go.Scatter(
            x=[math.sqrt(G * hc**3)], y=[hc],
            mode="markers", name="Critical state", showlegend=False,
            marker=dict(size=10, color=critical_color),
        ))

    q_max = max(math.sqrt(G * (2 * E / 3)**3) for E in (E1, E2))
    fig_q.update_layout(
        title="Depth h vs specific discharge Q/B",
        xaxis_title="Specific discharge q = Q/B [m²/s]",
        yaxis_title="Depth h [m]",
        xaxis=dict(range=[0, 1.15 * max(q1, q2, q_max)]),
        yaxis=dict(range=[0, h_limit]),
        height=520, legend=dict(orientation="h", y=-0.28),
        margin=dict(t=60, b=75),
    )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(fig_e, use_container_width=True, key="se_compare_energy")
    with right:
        st.plotly_chart(fig_q, use_container_width=True, key="se_compare_discharge")

    if kind == 3:
        st.caption("Type 3: two E(h) curves for q₁ and q₂; one h(q) curve at constant E.")
    else:
        st.caption("Type 4: one E(h) curve at constant q; two h(q) curves for E₁ and E₂.")

def render_change_exercise(case, q1, hc):
    kind = case['kind']
    E1 = case['E']
    q2 = case['q2'] if kind == 3 else q1
    E2 = case['E2'] if kind == 4 else E1
    branch = case['branch']
    h1 = two_depths(q1, E1)[1 if branch == 'subcritical' else 0]
    h2 = two_depths(q2, E2)[1 if branch == 'subcritical' else 0]
    st.subheader('Problem statement')
    st.markdown('Consider steady flow in a **rectangular open channel**. Neglect energy losses and the kinetic-energy correction factor.')
    st.markdown('#### Given data')
    st.latex(rf'B={case["B"]:.1f}\ \mathrm{{m}},\quad Q_1={case["Q"]:.1f}\ \mathrm{{m^3/s}},\quad h_1={h1:.4f}\ \mathrm{{m}}')
    if kind == 3:
        st.latex(rf'q_2=(Q/B)_2={q2:.3f}\ \mathrm{{m^2/s}},\qquad E_2=E_1')
        st.markdown('#### Required\nDetermine the **new flow depth** at the specified specific discharge, **keeping the specific energy constant** and remaining on the same flow branch. Check physical admissibility.')
    else:
        st.latex(rf'E_2={E2:.3f}\ \mathrm{{m}},\qquad q_2=q_1')
        st.markdown('#### Required\nDetermine the **new flow depth** at the specified specific energy, **keeping the specific discharge constant** and remaining on the same flow branch. Check physical admissibility.')
    st.divider()
    st.subheader('Complete worked solution')
    st.markdown('### 1. Initial state and critical conditions')
    st.latex(r'E=h+\frac{q^2}{2gh^2},\qquad q=\frac QB')
    st.latex(rf'q_1=\frac{{{case["Q"]:.1f}}}{{{case["B"]:.1f}}}={q1:.4f}\ \mathrm{{m^2/s}}')
    st.latex(rf'E_1=h_1+\frac{{q_1^2}}{{2gh_1^2}}=\boxed{{{E1:.4f}\ \mathrm{{m}}}}')
    hc1 = critical_depth(q1)
    fr1 = math.sqrt(q1*q1/(G*h1**3))
    st.latex(rf'h_{{c,1}}=\left(\frac{{q_1^2}}{{g}}\right)^{{1/3}}={hc1:.4f}\ \mathrm{{m}},\quad Fr_1={fr1:.4f}')
    st.markdown(f'The initial flow is **{branch}**; retain the same branch for the final state.')
    st.markdown('### 2. New state and feasibility')
    hc2 = critical_depth(q2)
    ec2 = 1.5*hc2
    st.latex(rf'q_2={q2:.4f}\ \mathrm{{m^2/s}},\quad E_2={E2:.4f}\ \mathrm{{m}}')
    st.latex(rf'h_{{c,2}}=\left(\frac{{q_2^2}}{{g}}\right)^{{1/3}}={hc2:.4f}\ \mathrm{{m}}')
    st.latex(rf'E_{{\min,2}}=\frac32 h_{{c,2}}={ec2:.4f}\ \mathrm{{m}}')
    st.markdown(f'Since **E₂ = {E2:.4f} m > E_min,2 = {ec2:.4f} m**, two positive depths exist; choose the **{branch}** branch.')
    st.markdown('### 3. Fixed-point solution')
    if branch == 'subcritical':
        st.markdown('Isolate the depth from the hydrostatic term:')
        st.latex(r'\boxed{h_{j+1}=E_2-\frac{q_2^2}{2gh_j^2}},\qquad h_1^{(\mathrm{iter})}=2h_{c,2}')
        values = iterate_subcritical(q2, E2, hc2, count=10)
    else:
        st.markdown('Isolate the depth from the kinetic term:')
        st.latex(r'\boxed{h_{j+1}=\sqrt{\frac{q_2^2}{2g(E_2-h_j)}}},\qquad h_1^{(\mathrm{iter})}=\frac{h_{c,2}}2')
        values = iterate_supercritical(q2, E2, hc2, count=10)
    st.dataframe([{'Step': i, 'Depth h [m]': round(h, 6)} for i, h in enumerate(values, 1)],
                 hide_index=True, use_container_width=True)
    fr2 = math.sqrt(q2*q2/(G*h2**3))
    st.latex(rf'\boxed{{h_2={h2:.5f}\ \mathrm{{m}}}},\qquad Fr_2={fr2:.4f}')
    st.caption('Final depth verified by bisection on the selected branch; the table illustrates the course fixed-point method.')
    st.markdown('### 4. Graphical interpretation')
    plot_comparison(case, q1, E1, h1, q2, E2, h2)


def render():
    st.header("Exercise · Specific Energy")
    st.caption("Automatically generated numerical data · Complete worked solutions · Rectangular channel")

    exercise_types = {
        "Type 1 — Two depths for a given E": 1,
        "Type 2 — Flow regime and alternate depth": 2,
        "Type 3 — Different Q/B, constant E": 3,
        "Type 4 — Different E, constant Q/B": 4,
    }
    selected_label = st.radio(
        "Choose exercise type",
        options=list(exercise_types),
        horizontal=True,
        key="se_exercise_type_selection",
    )
    selected_kind = exercise_types[selected_label]

    # Switching the selected type generates a new case of that type.
    if ("se_exercise_case" not in st.session_state
            or st.session_state.se_exercise_case["kind"] != selected_kind):
        st.session_state.se_exercise_case = make_case(selected_kind)
        st.session_state.se_exercise_number = 1

    if st.button("Generate another exercise", type="primary", key="se_generate"):
        st.session_state.se_exercise_case = make_case(selected_kind)
        st.session_state.se_exercise_number += 1

    case = st.session_state.se_exercise_case
    B, Q = case["B"], case["Q"]
    q = Q / B
    hc = critical_depth(q)
    ec = 1.5 * hc
    kind = case["kind"]
    if kind in (3, 4):
        st.caption(f"Exercise {st.session_state.se_exercise_number} · Type {kind} · Randomly generated and numerically verified")
        render_change_exercise(case, q, hc)
        return
    st.caption(f"Exercise {st.session_state.se_exercise_number} · Type {kind} · Randomly generated and numerically verified")

    st.subheader("Problem statement")
    st.markdown("Consider steady flow in a **rectangular open channel**. Neglect kinetic-energy correction factors.")
    if kind == 1:
        E = case["E"]
        st.markdown("#### Given data")
        st.latex(rf"B={B:.1f}\ \mathrm{{m}},\qquad Q={Q:.1f}\ \mathrm{{m^3/s}},\qquad E={E:.2f}\ \mathrm{{m}}")
        st.markdown("#### Required\nDetermine the **subcritical** and **supercritical** flow depths corresponding to the given specific energy.")
    else:
        h_given = case["h"]
        E = energy(h_given, q)
        st.markdown("#### Given data")
        st.latex(rf"B={B:.1f}\ \mathrm{{m}},\qquad Q={Q:.1f}\ \mathrm{{m^3/s}},\qquad h={h_given:.3f}\ \mathrm{{m}}")
        st.markdown("#### Required\n1. Determine whether the flow is **subcritical** or **supercritical**.\n"
                    "2. Find the **alternate depth**, i.e. the other depth corresponding to the same specific energy.")

    h_super, h_sub = two_depths(q, E)
    st.divider()
    st.subheader("Complete worked solution")
    st.markdown("### 1. Specific energy and critical depth")
    st.markdown("For a rectangular cross-section, the specific-energy equation is")
    st.latex(r"E=h+\frac{Q^2}{2gB^2h^2}=h+\frac{q^2}{2gh^2},\qquad q=\frac QB")
    st.latex(rf"q=\frac{{{Q:.1f}}}{{{B:.1f}}}={q:.4f}\ \mathrm{{m^2/s}}")
    st.markdown("At critical flow, the specific energy is minimum and the Froude number equals one:")
    st.latex(r"Fr=1,\qquad h_c=\left(\frac{Q^2}{gB^2}\right)^{1/3}=\left(\frac{q^2}{g}\right)^{1/3}")
    st.latex(rf"h_c=\left(\frac{{{Q:.1f}^2}}{{{G:.2f}\cdot {B:.1f}^2}}\right)^{{1/3}}"
             rf"=\boxed{{{hc:.4f}\ \mathrm{{m}}}}")
    st.latex(rf"E_{{\min}}=\frac32 h_c=\boxed{{{ec:.4f}\ \mathrm{{m}}}}")

    if kind == 2:
        st.markdown("### 2. Flow-regime classification")
        fr = math.sqrt(q * q / (G * h_given**3))
        regime = "supercritical" if h_given < hc else "subcritical"
        relation = "<" if h_given < hc else ">"
        st.latex(rf"h={h_given:.3f}\ \mathrm{{m}}\;{relation}\;h_c={hc:.4f}\ \mathrm{{m}}")
        st.latex(rf"Fr=\frac{{Q}}{{B\sqrt{{gh^3}}}}=\boxed{{{fr:.4f}}}")
        st.markdown(f"Therefore, the given flow is **{regime}**.")
        st.markdown("The specific energy corresponding to the given depth is")
        st.latex(rf"E={h_given:.3f}+\frac{{{Q:.1f}^2}}{{2\cdot {G:.2f}\cdot {B:.1f}^2\cdot {h_given:.3f}^2}}"
                 rf"=\boxed{{{E:.4f}\ \mathrm{{m}}}}")
        st.markdown("### 3. Alternate depth by fixed-point iteration")
        alternate_is_sub = h_given < hc
        if alternate_is_sub:
            st.markdown("The alternate depth is **subcritical** (`Fr < 1`). Isolate the depth from the hydrostatic term:")
            st.latex(r"h=E-\frac{Q^2}{2gB^2h^2}")
            st.latex(r"\boxed{h_{j+1}=E-\frac{Q^2}{2gB^2h_j^2}}")
            values = iterate_subcritical(q, E, hc)
            st.latex(r"h_1=2h_c")
            expected = h_sub
        else:
            st.markdown("The alternate depth is **supercritical** (`Fr > 1`). Isolate the depth from the dynamic term:")
            st.latex(r"h=\sqrt{\frac{Q^2}{2gB^2(E-h)}}")
            st.latex(r"\boxed{h_{j+1}=\sqrt{\frac{Q^2}{2gB^2(E-h_j)}}}")
            values = iterate_supercritical(q, E, hc)
            st.latex(r"h_1=\frac{h_c}{2}")
            expected = h_super
        st.dataframe([{"Step": i, "Depth h [m]": round(v, 5)} for i, v in enumerate(values, 1)],
                     hide_index=True, use_container_width=True)
        st.latex(rf"\boxed{{h_{{\mathrm{{alternate}}}}={expected:.4f}\ \mathrm{{m}}}}")
    else:
        st.markdown("### 2. Subcritical depth (`Fr < 1`)")
        st.markdown("Isolate the flow depth from the **hydrostatic term**:")
        st.latex(r"h=E-\frac{Q^2}{2gB^2h^2}")
        st.latex(r"\boxed{h_{j+1}=E-\frac{Q^2}{2gB^2h_j^2}},\qquad h_1=2h_c")
        sub_values = iterate_subcritical(q, E, hc)
        st.markdown("### 3. Supercritical depth (`Fr > 1`)")
        st.markdown("Isolate the flow depth from the **dynamic term**:")
        st.latex(r"h=\sqrt{\frac{Q^2}{2gB^2(E-h)}}")
        st.latex(r"\boxed{h_{j+1}=\sqrt{\frac{Q^2}{2gB^2(E-h_j)}}},\qquad h_1=\frac{h_c}{2}")
        super_values = iterate_supercritical(q, E, hc)
        st.markdown("### 4. Iteration table")
        st.dataframe([{"Step": i, "Subcritical h [m]": round(sub_values[i-1], 5),
                       "Supercritical h [m]": round(super_values[i-1], 5)}
                      for i in range(1, len(sub_values)+1)],
                     hide_index=True, use_container_width=True)
        st.latex(rf"\boxed{{h_{{\mathrm{{subcritical}}}}={h_sub:.4f}\ \mathrm{{m}}}}\qquad"
                 rf"\boxed{{h_{{\mathrm{{supercritical}}}}={h_super:.4f}\ \mathrm{{m}}}}")

    st.markdown("### Graphical interpretation")
    col_energy, col_discharge = st.columns(2)
    with col_energy:
        plot_energy(q, E, h_super, h_sub, hc, key="se_exercise_graph")
    with col_discharge:
        plot_constant_energy(q, E, h_super, h_sub, hc, key="se_exercise_constant_energy")
    st.caption("The reported final depths are numerically verified with bisection. "
               "The iteration table follows the fixed-point algorithms used in the course material.")
