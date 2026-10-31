"""Module 04 lecture notes with fixed, illustrative Plotly figures."""
from pathlib import Path
import numpy as np
import plotly.graph_objects as go
import streamlit as st

G = 9.81
B = 5.0       # m
N = 0.030     # s/m^(1/3)
Q_REF = 10.0  # m^3/s
S_RATING = 0.002


def _discharge(y, slope):
    if y <= 0 or slope <= 0:
        return 0.0
    area = B * y
    radius = area / (B + 2.0 * y)
    return area * radius ** (2.0 / 3.0) * np.sqrt(slope) / N


def _normal_depth(q, slope):
    if q <= 0:
        return 0.0
    if slope <= 0:
        raise ValueError("A positive bed slope is required for normal depth.")
    low, high = 0.0, 1.0
    while _discharge(high, slope) < q:
        high *= 2.0
    for _ in range(80):
        mid = (low + high) / 2.0
        if _discharge(mid, slope) < q:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def _rating_curve():
    q = np.linspace(0, 25, 101)
    y = np.array([_normal_depth(float(v), S_RATING) for v in q])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=q, y=y, mode="lines", name="Normal depth", line=dict(color="#16a34a", width=3)))
    fig.update_layout(
        title="Normal rating curve · rectangular channel",
        xaxis_title="Discharge Q [m³/s]", yaxis_title="Normal depth y₀ [m]",
        template="plotly_white", height=420,
        annotations=[dict(x=0.99, y=0.03, xref="paper", yref="paper", xanchor="right", yanchor="bottom",
                          text=f"b = {B:g} m · n = {N:.3f} · S₀ = {S_RATING:g}", showarrow=False)],
    )
    fig.update_xaxes(range=[0, 25])
    fig.update_yaxes(rangemode="tozero")
    return fig


def _slope_figure(kind):
    yc = ((Q_REF / B) ** 2 / G) ** (1 / 3)
    a = B * yc
    r = a / (B + 2 * yc)
    sc = (N * Q_REF / (a * r ** (2 / 3))) ** 2
    factors = {"critical": 1.0, "mild": 0.35, "steep": 3.0}
    slope = sc * factors[kind] if kind in factors else (0.0 if kind == "horizontal" else -0.35 * sc)
    y0 = _normal_depth(Q_REF, slope) if slope > 0 else None
    # Longitudinal distance is schematic; reference lines are vertical offsets from the bed.
    x = np.array([0.0, 100.0])
    bed = -slope * x
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=bed, mode="lines", name="Channel bed", line=dict(color="#a16207", width=4)))
    fig.add_trace(go.Scatter(x=x, y=bed + yc, mode="lines", name="Critical-depth reference (y꜀)",
                             line=dict(color="#dc2626", width=3, dash="dash")))
    if y0 is not None:
        fig.add_trace(go.Scatter(x=x, y=bed + y0, mode="lines", name="Uniform-flow surface (y₀)",
                                 line=dict(color="#16a34a", width=3)))
    fig.update_layout(
        title={"critical":"Critical slope", "mild":"Mild slope", "steep":"Steep slope",
               "horizontal":"Horizontal bed", "adverse":"Adverse slope"}[kind],
        xaxis_title="Downstream distance x [m]", yaxis_title="Elevation [m]",
        template="plotly_white", height=360, margin=dict(t=60, b=50),
        legend=dict(orientation="h", y=-0.32),
    )
    fig.update_xaxes(range=[0, 100])
    return fig, slope, sc, yc, y0


def render():
    text = Path(__file__).with_name("theory.md").read_text(encoding="utf-8")
    import re
    sections = re.split(r"<!-- FIGURE: (normal_rating|critical|mild|steep|horizontal|adverse) -->", text)
    st.caption("Uniform flow · Normal depth · Resistance · Channel slopes")
    st.markdown(sections[0])
    for tag, content in zip(sections[1::2], sections[2::2]):
        if tag == "normal_rating":
            st.plotly_chart(_rating_curve(), use_container_width=True, key="uf_rating")
            st.caption("Computed with Manning's equation at fixed geometry, roughness and bed slope.")
        else:
            fig, slope, sc, yc, y0 = _slope_figure(tag)
            st.plotly_chart(fig, use_container_width=True, key=f"uf_{tag}")
            if y0 is None:
                st.caption(f"S₀ = {slope:.5f}; y꜀ = {yc:.3f} m. No finite normal depth exists for Q > 0. The red line is a critical-depth reference, not a water surface.")
            else:
                st.caption(f"Q = {Q_REF:g} m³/s, b = {B:g} m, n = {N:.3f}; S₀ = {slope:.5f}, S꜀ = {sc:.5f}; y₀ = {y0:.3f} m, y꜀ = {yc:.3f} m. The red line is a critical-depth reference, not a second water surface.")
        st.markdown(content)
