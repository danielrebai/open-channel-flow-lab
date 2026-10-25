from pathlib import Path
import re

import numpy as np
import plotly.graph_objects as go
import streamlit as st


def plot_specific_energy():
    """Specific energy for a rectangular channel at fixed unit discharge."""
    g, q = 9.81, 1.0
    yc = (q**2 / g) ** (1 / 3)
    emin = 1.5 * yc

    def energy(y):
        return y + q**2 / (2 * g * y**2)

    fig = go.Figure()
    for depths, color, label in [
        (np.linspace(0.35 * yc, yc, 200), "#dc2626", "Supercritical: dE/dy < 0"),
        (np.linspace(yc, 3 * yc, 200), "#2563eb", "Subcritical: dE/dy > 0"),
    ]:
        fig.add_trace(go.Scatter(x=depths, y=energy(depths), mode="lines",
                                 name=label, line=dict(color=color, width=3)))
    fig.add_trace(go.Scatter(x=[yc], y=[emin], mode="markers",
                             name="Critical: dE/dy = 0",
                             marker=dict(color="#dc2626", size=11)))
    fig.add_vline(x=yc, line_dash="dot", line_color="#dc2626")
    fig.add_annotation(x=yc, y=emin, text="Critical depth", showarrow=True,
                       arrowhead=2, ax=70, ay=-35)
    fig.update_layout(title="Specific energy and the sign of dE/dy",
                      xaxis_title="Flow depth y [m]",
                      yaxis_title="Specific energy E [m]", height=450,
                      legend=dict(orientation="h", y=-0.25, x=0),
                      margin=dict(t=60, b=105, l=55, r=25))
    st.plotly_chart(fig, width="stretch")
    st.caption("Illustrative rectangular channel, q = 1 m²/s.")


def plot_numerator():
    """Bed slope, friction slope and their difference versus flow depth."""
    Q, b, n, S0 = 3.0, 3.0, 0.025, 0.002

    def friction_slope(y):
        area = b * y
        radius = area / (b + 2 * y)
        return (n * Q / (area * radius ** (2 / 3))) ** 2

    lo, hi = 0.01, 10.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if friction_slope(mid) > S0:
            lo = mid
        else:
            hi = mid
    y0 = (lo + hi) / 2
    y = np.linspace(0.45 * y0, 2.5 * y0, 400)
    sf = friction_slope(y)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y, y=sf, mode="lines", name="Friction slope Sf",
                             line=dict(color="#475569", width=3)))
    fig.add_trace(go.Scatter(x=y, y=np.full_like(y, S0), mode="lines",
                             name="Bed slope S0",
                             line=dict(color="#d97706", width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=y, y=S0 - sf, mode="lines",
                             name="Numerator S0 − Sf",
                             line=dict(color="#16a34a", width=3)))
    fig.add_hline(y=0, line_color="#94a3b8", line_width=1)
    fig.add_vline(x=y0, line_dash="dot", line_color="#16a34a")
    fig.add_trace(go.Scatter(x=[y0], y=[0], mode="markers", name="Normal depth y0",
                             marker=dict(color="#16a34a", size=10)))
    fig.add_annotation(x=y0, y=0, text="Normal depth y₀", showarrow=True,
                       arrowhead=2, ax=75, ay=40)
    fig.update_layout(title="Numerator: bed slope versus friction slope",
                      xaxis_title="Flow depth y [m]", yaxis_title="Slope [−]",
                      height=470, legend=dict(orientation="h", y=-0.24, x=0),
                      margin=dict(t=60, b=115, l=65, r=25))
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Illustrative rectangular channel: Q = {Q:g} m³/s, b = {b:g} m, "
               f"n = {n:g}, S₀ = {S0:g}, normal depth y₀ = {y0:.3f} m.")




def plot_m_profile(kind):
    """GVF profiles obtained from dy/ds = (S0-Sf)/(1-Fr²)."""
    Q, b, n, S0, g = 3.0, 3.0, 0.025, 0.002, 9.81

    def sf(y):
        a = b * y
        r = a / (b + 2 * y)
        return (n * Q / (a * r ** (2 / 3))) ** 2

    def gradient(y):
        fr2 = Q**2 / (g * b**2 * y**3)
        return (S0 - sf(y)) / (1 - fr2)

    low, high = 0.01, 10.0
    for _ in range(90):
        mid = (low + high) / 2
        if sf(mid) > S0:
            low = mid
        else:
            high = mid
    y0 = (low + high) / 2
    yc = (Q**2 / (g * b**2)) ** (1 / 3)

    # Integrate ds/dy rather than dy/ds; this also captures the
    # vertical tangent at critical depth without numerical instability.
    if kind == "m1":
        depths = np.linspace(y0 * 1.015, y0 * 2.25, 600)
    elif kind == "m2":
        depths = np.linspace(y0 * 0.985, yc * 1.001, 600)
    else:
        depths = np.linspace(yc * 0.18, yc * 0.999, 600)
    reciprocal = 1.0 / gradient(depths)
    dx = 0.5 * (reciprocal[1:] + reciprocal[:-1]) * np.diff(depths)
    distance = np.r_[0.0, np.cumsum(dx)]
    distance -= distance.min()
    bed = -S0 * distance
    surface = bed + depths

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=distance, y=bed, name="Channel bed",
                             line=dict(color="#8b5e3c", width=3)))
    fig.add_trace(go.Scatter(x=distance, y=bed + y0, name="Normal-depth line h₀",
                             line=dict(color="#16a34a", width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=distance, y=bed + yc, name="Critical-depth line h꜀",
                             line=dict(color="#dc2626", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=distance, y=surface, name=f"{kind.upper()} water surface",
                             line=dict(color="#0284c7", width=4)))
    fig.update_layout(title=f"{kind.upper()} water-surface profile · mild slope",
                      xaxis_title="Downstream distance s [m]",
                      yaxis_title="Elevation [m]",
                      height=460, legend=dict(orientation="h", y=-0.25, x=0),
                      margin=dict(t=60, b=110, l=65, r=25))
    st.plotly_chart(fig, width="stretch")
    if kind == "m1":
        st.caption("M1: h > h₀ > h꜀. Subcritical, decelerating flow. "
                   "Depth increases downstream; the profile approaches normal depth "
                   "asymptotically upstream. At large depths, dh/ds approaches S₀ "
                   "and the water surface approaches a horizontal line.")
    elif kind == "m2":
        st.caption("M2: h꜀ < h < h₀. Subcritical, accelerating flow. "
                   "Depth decreases downstream, approaching h₀ asymptotically upstream "
                   "and meeting h꜀ with a vertical tangent in the depth-versus-distance diagram.")
    else:
        st.caption("M3: 0 < h < h꜀ < h₀. Supercritical, decelerating flow. "
                   "Depth increases downstream and reaches h꜀ with a vertical tangent. "
                   "The mathematical continuation toward h = 0 is not physically "
                   "attainable in this model.")
    st.caption(f"Illustrative rectangular channel: Q={Q:g} m³/s, b={b:g} m, "
               f"n={n:g}, S₀={S0:g}; h₀={y0:.3f} m, h꜀={yc:.3f} m. "
               "Computed from the gradually varied flow equation.")


def plot_m1():
    plot_m_profile("m1")


def plot_m2():
    plot_m_profile("m2")


def plot_m3():
    plot_m_profile("m3")



def plot_s_profile(kind):
    """Steep-slope GVF solution, integrating dx/dy to resolve critical endpoints."""
    Q, b, n, S0, g = 3.0, 3.0, 0.025, 0.02, 9.81

    def sf(y):
        area = b * y
        radius = area / (b + 2 * y)
        return (n * Q / (area * radius ** (2 / 3))) ** 2

    lo, hi = 0.001, 10.0
    for _ in range(90):
        mid = (lo + hi) / 2
        if sf(mid) > S0:
            lo = mid
        else:
            hi = mid
    y0 = (lo + hi) / 2
    yc = (Q**2 / (g * b**2)) ** (1 / 3)
    assert y0 < yc, "Choose a steeper bed slope: normal depth must be below critical depth."

    if kind == "s1":
        depths = np.linspace(yc * 1.001, yc * 2.8, 700)
    elif kind == "s2":
        depths = np.linspace(yc * 0.999, y0 * 1.015, 700)
    elif kind == "s3":
        depths = np.linspace(y0 * 0.18, y0 * 0.985, 700)
    else:
        raise ValueError(f"Unknown profile: {kind}")

    fr2 = Q**2 / (g * b**2 * depths**3)
    grad = (S0 - sf(depths)) / (1 - fr2)
    dx = 0.5 * (1 / grad[1:] + 1 / grad[:-1]) * np.diff(depths)
    distance = np.r_[0.0, np.cumsum(dx)]
    distance -= distance.min()
    order = np.argsort(distance)
    distance = distance[order]
    depths = depths[order]
    bed = -S0 * distance

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=distance, y=bed, name="Channel bed",
                             line=dict(color="#8b5e3c", width=3)))
    fig.add_trace(go.Scatter(x=distance, y=bed + y0, name="Normal depth y₀",
                             line=dict(color="#16a34a", width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=distance, y=bed + yc, name="Critical depth y꜀",
                             line=dict(color="#dc2626", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=distance, y=bed + depths,
                             name=f"{kind.upper()} water surface",
                             line=dict(color="#0284c7", width=4)))
    fig.update_layout(title=f"{kind.upper()} water-surface profile · steep slope",
                      xaxis_title="Downstream distance x [m]",
                      yaxis_title="Elevation [m]", height=460,
                      legend=dict(orientation="h", y=-0.25, x=0),
                      margin=dict(t=60, b=110, l=65, r=25))
    st.plotly_chart(fig, width="stretch")
    notes = {
        "s1": "S1: y > yc > y₀. Subcritical, decelerating flow; depth increases downstream. The critical depth is approached at a vertical tangent in the depth–distance plane.",
        "s2": "S2: y₀ < y < yc. Supercritical, accelerating flow; depth decreases downstream. Normal depth is approached asymptotically downstream; the critical-depth endpoint has a vertical tangent.",
        "s3": "S3: 0 < y < y₀ < yc. Supercritical, decelerating flow; depth increases downstream toward normal depth asymptotically.",
    }
    st.caption(notes[kind])
    st.caption(f"Illustrative rectangular channel: Q={Q:g} m³/s, b={b:g} m, "
               f"n={n:g}, S₀={S0:g}; y₀={y0:.3f} m, yc={yc:.3f} m. "
               "Computed from the gradually varied flow equation.")


def plot_s1():
    plot_s_profile("s1")


def plot_s2():
    plot_s_profile("s2")


def plot_s3():
    plot_s_profile("s3")




def plot_h_profile(kind):
    """Horizontal-bed GVF profile; integrate dx/dy near critical depth."""
    Q, b, n, g = 3.0, 3.0, 0.025, 9.81
    yc = (Q**2 / (g * b**2)) ** (1 / 3)

    def friction_slope(y):
        area = b * y
        radius = area / (b + 2 * y)
        return (n * Q / (area * radius ** (2 / 3))) ** 2

    if kind == "h2":
        depths = np.linspace(2.6 * yc, 1.001 * yc, 650)
    elif kind == "h3":
        depths = np.linspace(0.16 * yc, 0.999 * yc, 650)
    else:
        raise ValueError(f"Unknown horizontal profile: {kind}")

    fr2 = Q**2 / (g * b**2 * depths**3)
    # S0=0, hence dy/dx=-Sf/(1-Fr²), dx/dy=-(1-Fr²)/Sf.
    dx_dy = -(1 - fr2) / friction_slope(depths)
    dx = 0.5 * (dx_dy[1:] + dx_dy[:-1]) * np.diff(depths)
    distance = np.r_[0.0, np.cumsum(dx)]
    distance -= distance.min()
    order = np.argsort(distance)
    distance, depths = distance[order], depths[order]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=distance, y=np.zeros_like(distance),
                             name="Horizontal channel bed",
                             line=dict(color="#8b5e3c", width=3)))
    fig.add_trace(go.Scatter(x=distance, y=np.full_like(distance, yc),
                             name="Critical depth y꜀",
                             line=dict(color="#dc2626", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=distance, y=depths,
                             name=f"{kind.upper()} water surface",
                             line=dict(color="#0284c7", width=4)))
    fig.update_layout(title=f"{kind.upper()} water-surface profile · horizontal bed",
                      xaxis_title="Downstream distance x [m]",
                      yaxis_title="Elevation above bed [m]", height=460,
                      legend=dict(orientation="h", y=-0.25, x=0),
                      margin=dict(t=60, b=110, l=65, r=25))
    st.plotly_chart(fig, width="stretch")
    if kind == "h2":
        st.caption("H2: y > yc. Accelerating subcritical flow: depth decreases "
                   "downstream and approaches critical depth with a vertical tangent "
                   "in the depth–distance diagram. There is no finite normal depth.")
    else:
        st.caption("H3: 0 < y < yc. Decelerating supercritical flow: depth "
                   "increases downstream and approaches critical depth with a vertical "
                   "tangent. The formal zero-depth limit is not physically realizable.")
    st.caption(f"Illustrative rectangular channel: Q={Q:g} m³/s, b={b:g} m, "
               f"n={n:g}, S₀=0; yc={yc:.3f} m. "
               "Computed from the gradually varied flow equation.")


def plot_h2():
    plot_h_profile("h2")


def plot_h3():
    plot_h_profile("h3")


PLOTS = {
    "specific_energy": plot_specific_energy,
    "specific_energy_plot": plot_specific_energy,
    "specific_energy_denominator": plot_specific_energy,
    "numerator": plot_numerator,
    "m1": plot_m1,
    "m2": plot_m2,
    "m3": plot_m3,
    "s1": plot_s1,
    "s2": plot_s2,
    "s3": plot_s3,
    "h2": plot_h2,
    "h3": plot_h3,
}

# Accepts normal markers, escaped brackets, and whitespace inside brackets.
MARKER = re.compile(r"\\?\[\\?\[\s*([A-Za-z_][A-Za-z_0-9]*)\s*\\?\]\\?\]", re.I)
LEGACY = re.compile(r"\\?<!--\s*SPECIFIC_ENERGY_DENOMINATOR\s*-->", re.I)

M_TEXT = {
    "m1": ("### M1 Profile — h > h₀ > h꜀\n\n"
           "Subcritical, decelerating flow: **dh/ds > 0**. The depth increases downstream; "
           "upstream the profile approaches normal depth asymptotically. At very large "
           "depth the water surface tends to a horizontal asymptote."),
    "m2": ("### M2 Profile — h꜀ < h < h₀\n\n"
           "Subcritical, accelerating flow: **dh/ds < 0**. The depth decreases "
           "downstream, approaching normal depth upstream and critical depth with "
           "a vertical tangent downstream."),
    "m3": ("### M3 Profile — 0 < h < h꜀ < h₀\n\n"
           "Supercritical, decelerating flow: **dh/ds > 0**. The depth increases "
           "downstream and approaches critical depth with a vertical tangent. "
           "The limit h → 0 is not physically attainable in this model."),
}


def render():
    st.header("Theory · Gradually Varied Flow")
    # Visible version ID: if absent, the browser is connected to an old Streamlit process.
    st.caption("Theory renderer · M + S + H profiles v1 · critical red / normal green")
    theory_file = Path(__file__).resolve().parent / "theory.md"
    if not theory_file.exists():
        st.error(f"Missing theory.md: {theory_file}")
        return
    content = theory_file.read_text(encoding="utf-8")
    # Legacy HTML comment is converted into a normal marker.
    content = LEGACY.sub("[[specific_energy_denominator]]", content)
    seen = set()
    position = 0
    for match in MARKER.finditer(content):
        name = match.group(1).lower()
        plot = PLOTS.get(name)
        if plot is None:
            continue
        st.markdown(content[position:match.start()])
        plot()
        seen.add(name)
        position = match.end()
    st.markdown(content[position:])

    # Fail-safe: the three M graphs ALWAYS appear, even if the Markdown
    # markers were omitted, escaped unusually, or pasted into a code block.
    missing = [key for key in ("m1", "m2", "m3") if key not in seen]
    if missing:
        st.markdown("## M Profiles — Mild Slope")
        st.markdown("For a mild slope, **h₀ > h꜀**. The profiles below "
                    "follow the gradually varied flow equation.")
        for key in missing:
            st.markdown(M_TEXT[key])
            PLOTS[key]()

    # S profiles are displayed even before their Markdown sections are written.
    missing_s = [key for key in ("s1", "s2", "s3") if key not in seen]
    if missing_s:
        st.markdown("## S Profiles — Steep Slope")
        st.markdown("For a steep slope, $y_0<y_c$. The plots below are preliminary; "
                    "the full mathematical commentary will be added after reviewing the notes.")
        for key in missing_s:
            st.markdown(f"### {key.upper()} Profile")
            PLOTS[key]()

    # H profiles also render if their Markdown placeholders are absent.
    missing_h = [key for key in ("h2", "h3") if key not in seen]
    if missing_h:
        st.markdown("## H Profiles — Horizontal Bed")
        st.markdown("For a horizontal bed, $S_0=0$. No finite normal depth exists; "
                    "the critical depth $y_c$ separates the H2 and H3 profiles.")
        for key in missing_h:
            st.markdown(f"### {key.upper()} Profile")
            PLOTS[key]()
