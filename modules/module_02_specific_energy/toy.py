"""Module 02 — Specific Energy: interactive baseline comparisons."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

G = 9.81
DEFAULT = {"Q": 3.0, "b": 3.0, "E": 1.5}
COLORS = {"baseline": "#64748b", "current": "#2563eb", "critical": "#dc2626"}


def _specific_energy(y, q):
    return y + q**2 / (2 * G * y**2)


def _critical_depth(q):
    return (q**2 / G) ** (1.0 / 3.0)


def _specific_discharge(y, energy):
    return y * np.sqrt(np.maximum(0.0, 2 * G * (energy - y)))


def _add_curve(fig, x, y, name, baseline=False):
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines", name=name,
        line=dict(color=COLORS["baseline" if baseline else "current"],
                  width=3, dash="dash" if baseline else "solid"),
    ))


def _energy_plot(Q, b, base):
    q = Q / b
    q_base = base["Q"] / base["b"]
    yc = _critical_depth(q)
    yc_base = _critical_depth(q_base)
    # Fixed axes across the full slider domain, including the baseline.
    y = np.linspace(0.12, 5.0, 700)
    fig = go.Figure()
    # Critical-state locus in the (h, E) plane: E_c = 3 h_c / 2.
    h_locus = np.linspace(0.0, 5.0, 400)
    fig.add_trace(go.Scatter(
        x=h_locus, y=1.5 * h_locus, mode="lines",
        name="Critical-state locus (E = 3h/2)",
        line=dict(color=COLORS["critical"], width=2, dash="dot"),
    ))
    _add_curve(fig, y, _specific_energy(y, q_base),
               f"Baseline (q = {q_base:.2f} m²/s)", baseline=True)
    _add_curve(fig, y, _specific_energy(y, q),
               f"Current (q = {q:.2f} m²/s)")
    for depth, discharge, name, symbol in [
        (yc_base, q_base, "Baseline critical point", "circle-open"),
        (yc, q, "Current critical point", "circle"),
    ]:
        fig.add_trace(go.Scatter(
            x=[depth], y=[1.5 * depth], mode="markers", name=name,
            marker=dict(color=COLORS["critical"], size=11, symbol=symbol),
        ))
    fig.update_layout(
        title="Specific energy versus depth — constant discharge",
        xaxis=dict(title="Depth h [m]", range=[0, 5.0]),
        yaxis=dict(title="Specific energy E [m]", range=[0, 12]),
        height=470, legend=dict(orientation="h", y=-0.28, x=0),
        margin=dict(t=60, b=120, l=55, r=25),
    )
    return fig, yc, 1.5 * yc


def _discharge_plot(energy, base):
    e_base = base["E"]
    fig = go.Figure()
    # Critical-state locus in the (q, h) plane: q_c = sqrt(g h_c^3).
    h_locus = np.linspace(0.0, 3.1, 400)
    fig.add_trace(go.Scatter(
        x=np.sqrt(G * h_locus**3), y=h_locus, mode="lines",
        name="Critical-state locus (q = sqrt(g h³))",
        line=dict(color=COLORS["critical"], width=2, dash="dot"),
    ))
    for e, name, baseline in [(e_base, "Baseline", True), (energy, "Current", False)]:
        y = np.linspace(0.0, e, 550)
        q = _specific_discharge(y, e)
        _add_curve(fig, q, y, f"{name} (E = {e:.2f} m)", baseline=baseline)
        yc = 2 * e / 3
        qc = _specific_discharge(yc, e)
        fig.add_trace(go.Scatter(
            x=[qc], y=[yc], mode="markers",
            name=f"{name} critical point",
            marker=dict(color=COLORS["critical"], size=11,
                        symbol="circle-open" if baseline else "circle"),
        ))
    fig.update_layout(
        title="Depth versus unit discharge — constant specific energy",
        xaxis=dict(title="Unit discharge q = Q/b [m²/s]", range=[0, 11]),
        yaxis=dict(title="Depth h [m]", range=[0, 3.1]),
        height=470, legend=dict(orientation="h", y=-0.28, x=0),
        margin=dict(t=60, b=120, l=55, r=25),
    )
    return fig


def render():
    st.subheader("Specific Energy · Interactive Toy")
    st.markdown("Compare the **current** curve (solid blue) with a **fixed baseline** "
                "(dashed gray). Critical points are shown in red, and the **red dotted line** shows the critical-state locus.")

    if "se_baseline_energy_curve" not in st.session_state:
        st.session_state.se_baseline_energy_curve = {"Q": DEFAULT["Q"], "b": DEFAULT["b"]}
    if "se_baseline_discharge_curve" not in st.session_state:
        st.session_state.se_baseline_discharge_curve = {"E": DEFAULT["E"]}

    st.markdown("### 1. Specific energy E versus depth h")
    st.caption("Only these sliders affect the first graph.")
    c1, c2 = st.columns(2)
    with c1:
        Q = st.slider("Discharge Q [m³/s]", 0.5, 10.0, DEFAULT["Q"], 0.1, key="se_Q")
    with c2:
        b = st.slider("Channel width b [m]", 1.0, 8.0, DEFAULT["b"], 0.1, key="se_b")

    a, z, _ = st.columns([1, 1, 3])
    with a:
        if st.button("Set baseline · graph 1", key="se_set_1", use_container_width=True):
            st.session_state.se_baseline_energy_curve = {"Q": Q, "b": b}
    with z:
        if st.button("Reset baseline · graph 1", key="se_reset_1", use_container_width=True):
            st.session_state.se_baseline_energy_curve = {"Q": DEFAULT["Q"], "b": DEFAULT["b"]}
    base1 = st.session_state.se_baseline_energy_curve
    fig1, yc, emin = _energy_plot(Q, b, base1)
    st.plotly_chart(fig1, width="stretch")
    st.caption(f"Baseline: Q = {base1['Q']:.2f} m³/s, b = {base1['b']:.2f} m. "
               f"Current: q = {Q/b:.3f} m²/s; critical depth = {yc:.3f} m; "
               f"minimum energy = {emin:.3f} m.")

    st.divider()
    st.markdown("### 2. Depth h versus unit discharge q = Q/b")
    st.caption("This slider affects only the second graph.")
    energy = st.slider("Specific energy E [m]", 0.5, 3.0, DEFAULT["E"], 0.05,
                       key="se_E")
    a, z, _ = st.columns([1, 1, 3])
    with a:
        if st.button("Set baseline · graph 2", key="se_set_2", use_container_width=True):
            st.session_state.se_baseline_discharge_curve = {"E": energy}
    with z:
        if st.button("Reset baseline · graph 2", key="se_reset_2", use_container_width=True):
            st.session_state.se_baseline_discharge_curve = {"E": DEFAULT["E"]}
    base2 = st.session_state.se_baseline_discharge_curve
    st.plotly_chart(_discharge_plot(energy, base2), width="stretch")
    hc = 2 * energy / 3
    qmax = _specific_discharge(hc, energy)
    st.caption(f"Baseline: E = {base2['E']:.2f} m. "
               f"Current: critical depth = {hc:.3f} m; "
               f"maximum unit discharge = {qmax:.3f} m²/s.")
