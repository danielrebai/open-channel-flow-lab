"""Illustrative specific-energy diagram for the theory section."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from ..hydraulics import G


def plot_specific_energy_denominator():
    """Show dE/dy < 0 below critical depth and > 0 above it."""
    q = 1.0  # Illustrative unit discharge, m^2/s
    yc = (q**2 / G) ** (1.0 / 3.0)
    emin = 1.5 * yc

    def energy(y):
        return y + q**2 / (2.0 * G * y**2)

    supercritical = np.linspace(0.35 * yc, yc, 250)
    subcritical = np.linspace(yc, 3.2 * yc, 250)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=supercritical, y=energy(supercritical), mode="lines",
        name="Supercritical: dE/dy < 0",
        line=dict(color="#dc2626", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=subcritical, y=energy(subcritical), mode="lines",
        name="Subcritical: dE/dy > 0",
        line=dict(color="#2563eb", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=[yc], y=[emin], mode="markers",
        name="Critical: dE/dy = 0",
        marker=dict(color="#111827", size=11),
        hovertemplate="Critical depth: %{x:.3f} m<br>Minimum energy: %{y:.3f} m<extra></extra>",
    ))
    fig.add_vline(x=yc, line_dash="dot", line_color="#64748b")
    fig.add_annotation(
        x=yc, y=emin, text="Critical depth", showarrow=True,
        arrowhead=2, ax=70, ay=-40,
    )
    fig.update_layout(
        title="Specific energy: sign of dE/dy",
        xaxis_title="Flow depth y [m]",
        yaxis_title="Specific energy E [m]",
        height=440,
        legend=dict(orientation="h", y=-0.22, x=0),
        margin=dict(t=65, b=95, l=55, r=25),
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Illustrative rectangular channel with q = 1 m²/s. "
        "Red: supercritical (dE/dy < 0); blue: subcritical (dE/dy > 0)."
    )
