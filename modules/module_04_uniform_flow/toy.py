"""Interactive uniform-flow toy for a prismatic rectangular channel."""

import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st

G = 9.81


def _flow_at_depth(y: float, b: float, ks: float, slope: float) -> float:
    if y <= 0:
        return 0.0
    area = b * y
    radius = area / (b + 2 * y)
    return ks * area * radius ** (2 / 3) * math.sqrt(slope)


def _normal_depth(q: float, b: float, ks: float, slope: float) -> float:
    low = 0.0
    high = max(1.0, (q / (ks * b * math.sqrt(slope))) ** (3 / 5) * 2)
    while _flow_at_depth(high, b, ks, slope) < q:
        high *= 2
    for _ in range(90):
        mid = (low + high) / 2
        if _flow_at_depth(mid, b, ks, slope) < q:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def render():
    st.header("Toy · Uniform Flow")
    st.markdown(
        "Change the channel parameters and observe the **bed**, **normal-depth line**, "
        "and **critical-depth line**. All depths are measured vertically above the bed."
    )

    a, bcol = st.columns(2)
    with a:
        q = st.slider("Discharge Q (m³/s)", 0.5, 30.0, 10.0, 0.5, key="uf_toy_q")
        width = st.slider("Channel width b (m)", 1.0, 15.0, 4.0, 0.5, key="uf_toy_b")
    with bcol:
        ks = st.slider("Strickler coefficient Ks (m⅓/s)", 20.0, 100.0, 75.0, 5.0, key="uf_toy_ks")
        slope = st.slider("Bed slope S₀ (m/m)", 0.0001, 0.0500, 0.0100, 0.0001,
                          format="%.4f", key="uf_toy_slope")

    y0 = _normal_depth(q, width, ks, slope)
    yc = (q * q / (G * width * width)) ** (1 / 3)
    ac = width * yc
    rc = ac / (width + 2 * yc)
    sc = (q / (ks * ac * rc ** (2 / 3))) ** 2

    if abs(slope - sc) / sc < 1e-8:
        classification = "Critical slope"
        explanation = "The normal and critical depths coincide: uniform flow is critical."
    elif y0 > yc:
        classification = "Mild slope · Subcritical uniform flow"
        explanation = "Normal depth exceeds critical depth (y₀ > yc); equivalently, S₀ < Sc."
    else:
        classification = "Steep slope · Supercritical uniform flow"
        explanation = "Normal depth is below critical depth (y₀ < yc); equivalently, S₀ > Sc."

    m1, m2, m3 = st.columns(3)
    m1.metric("Normal depth y₀", f"{y0:.3f} m")
    m2.metric("Critical depth yc", f"{yc:.3f} m")
    m3.metric("Critical slope Sc", f"{sc:.5f}")
    st.markdown(f"**{classification}** — {explanation}")

    x = np.linspace(0.0, 80.0, 160)
    bed = -slope * x
    uniform = bed + y0
    critical = bed + yc

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=bed, mode="lines", name="Channel bed",
        line=dict(color="#A16207", width=4),
        hovertemplate="x = %{x:.1f} m<br>Bed elevation = %{y:.3f} m<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=uniform, mode="lines", name="Uniform water surface (y₀)",
        line=dict(color="#16A34A", width=3),
        fill="tonexty", fillcolor="rgba(22,163,74,0.10)",
        hovertemplate="x = %{x:.1f} m<br>Uniform water elevation = %{y:.3f} m<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=critical, mode="lines", name="Critical-depth reference (yc)",
        line=dict(color="#DC2626", width=3, dash="dash"),
        hovertemplate="x = %{x:.1f} m<br>Critical reference elevation = %{y:.3f} m<extra></extra>",
    ))
    fig.update_layout(
        title="Longitudinal channel profile · flow from left to right →",
        xaxis_title="Distance along channel x (m)",
        yaxis_title="Elevation relative to upstream bed (m)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=15, r=15, t=95, b=15),
        height=470,
        hovermode="x unified",
    )
    fig.update_xaxes(range=[0, 80])
    fig.update_yaxes(range=[min(bed) - 0.15 * max(y0, yc, 1), max(y0, yc) + 0.2 * max(y0, yc, 1)])
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "The green line is the actual uniform-flow free surface. The red dashed line is "
        "a theoretical critical-depth reference, not a second water surface. "
        "The profile is a longitudinal elevation view; the vertical axis is not to scale with the horizontal axis."
    )

    with st.expander("Equations and interpretation"):
        st.latex(r"Q=K_s A(y_0)R(y_0)^{2/3}\sqrt{S_0},\qquad A=by,\quad R=\frac{by}{b+2y}")
        st.latex(r"y_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}")
        st.latex(r"S_c=\left(\frac{Q}{K_s A(y_c)R(y_c)^{2/3}}\right)^2")
        st.markdown(
            "Increasing **Q** generally raises both depths. Increasing **Ks** or **S₀** "
            "lowers the normal depth while leaving the critical depth unchanged at fixed Q and b. "
            "Changing **b** affects both depths."
        )
