import numpy as np
import plotly.graph_objects as go
import streamlit as st
from .hydraulics import G


def render():
    with st.sidebar:
        st.header("Channel parameters")
        Q = st.number_input("Discharge Q [m³/s]", min_value=0.01, value=3.0, step=0.1)
        b = st.number_input("Channel width b [m]", min_value=0.1, value=3.0, step=0.1)
        S0 = st.number_input("Bed slope S₀ [m/m]", min_value=0.00001, max_value=0.2, value=0.002, step=0.0005, format="%.5f")
        n = st.number_input("Manning n [s/m¹ᐟ³]", min_value=0.005, max_value=0.2, value=0.025, step=0.001, format="%.3f")
        auto_length = st.checkbox("Auto-fit channel length to the water-surface profile", value=True)
        max_length = st.number_input("Maximum channel length [m]", min_value=50.0, max_value=20000.0, value=5000.0, step=100.0) if auto_length else None
        manual_length = None if auto_length else st.number_input("Channel length L [m]", min_value=10.0, max_value=20000.0, value=200.0, step=10.0)
        side = st.radio("Boundary condition", ["Downstream", "Upstream"])
        yb = st.number_input("Prescribed depth y [m]", min_value=0.02, max_value=30.0, value=1.2, step=0.05)


    def area(y):
        return b * y


    def radius(y):
        return area(y) / (b + 2 * y)


    def friction_slope(y):
        return (n * Q / (area(y) * radius(y) ** (2 / 3))) ** 2


    def froude_squared(y):
        return Q**2 / (G * b**2 * y**3)


    def rhs(y):
        if y <= 0:
            raise ValueError("Non-positive depth")
        denominator = 1 - froude_squared(y)
        if abs(denominator) < 0.002:
            raise ValueError("Near critical depth")
        return (S0 - friction_slope(y)) / denominator


    def normal_depth():
        lo, hi = 1e-6, 1.0
        while friction_slope(hi) > S0 and hi < 1e6:
            hi *= 2
        for _ in range(90):
            mid = (lo + hi) / 2
            if friction_slope(mid) > S0:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2


    yc = (Q**2 / (G * b**2)) ** (1 / 3)
    yn = normal_depth()
    regime = "M (mild slope)" if yn > yc else "S (steep slope)" if yn < yc else "C (critical slope)"
    subcritical = yb > yc
    critical_boundary = abs(yb - yc) < 1e-7
    compatible = (subcritical and side == "Downstream") or ((yb < yc) and side == "Upstream")

    # A single prescribed depth is a valid GVF control only downstream for
    # subcritical flow, and upstream for supercritical flow.
    # Do not integrate or render a profile for an invalid control.
    critical_boundary = abs(yb - yc) <= max(1e-5, 0.001 * yc)
    if critical_boundary:
        st.error(
            "Invalid boundary condition: the prescribed depth is at (or too close to) "
            "critical depth (Fr ≈ 1). The GVF equation is singular here. "
            "Choose a non-critical depth; a critical control needs a separate model."
        )

    if not compatible:
        current = "subcritical (Fr < 1)" if subcritical else "supercritical (Fr > 1)"
        required = "Downstream" if subcritical else "Upstream"
        st.error(
            f"Invalid boundary condition: the prescribed depth gives {current} flow. "
            f"For this regime, prescribe the depth at the **{required.lower()}** end. "
            "No water-surface profile has been calculated or displayed."
        )

    if compatible and not critical_boundary:
        # Integrate from the prescribed boundary, measuring distance t away from it.
        # Auto-fit stops when the profile has nearly reached normal depth, near
        # critical flow, or the user-selected safety limit.
        sign = -1 if side == "Downstream" else 1
        limit = max_length if auto_length else manual_length
        t_values, depth_values = [0.0], [yb]
        warning = None
        stop_reason = None
        initial_departure = abs(yb - yn)
        normal_tolerance = max(0.005, 0.02 * initial_departure)
        critical_tolerance = max(0.003, 0.005 * yc)
        min_display_length = 20.0

        # Defina (2010), Section 8.2.1, equations (99)-(101): explicit Euler.
        # Subcritical: y_(i+1) = y_i - f_i * Δx (integrate upstream).
        # Supercritical: y_(i+1) = y_i + f_i * Δx (integrate downstream).
        # f_i = (S0 - Sf_i)/(1 - Fr_i²). All quantities evaluated at i.
        # Recommended step limits: 1-10*y (subcritical), <= 0.5-2*y
        # (supercritical); shorten further close to critical flow.
        MAX_STEPS = 30000
        for _ in range(MAX_STEPS):
            t, y = t_values[-1], depth_values[-1]
            if t >= limit - 1e-9:
                stop_reason = "Maximum channel length reached"
                break
            if auto_length and t >= min_display_length:
                if initial_departure <= normal_tolerance:
                    stop_reason = "Uniform-flow condition"
                    break
                if abs(y - yn) <= normal_tolerance:
                    stop_reason = "Profile approached normal depth"
                    break
                if abs(y - yc) <= critical_tolerance:
                    stop_reason = "Profile approached critical depth"
                    break

            try:
                f = rhs(y)
                # A conservative step inside the source's recommended ranges.
                # Near critical depth use smaller steps to avoid crossing Fr=1.
                base_step = (1.0 if subcritical else 0.5) * y
                if abs(f) > 1e-12:
                    base_step = min(base_step, 0.025 * max(y, 0.05) / abs(f))
                # Limit relative proximity to critical depth and the normal-depth
                # asymptote without forcing the profile onto either reference line.
                if abs(f) > 1e-12 and abs(y - yc) > critical_tolerance:
                    base_step = min(base_step, 0.25 * abs(y - yc) / abs(f))
                dx = min(base_step, limit - t)
                if dx < 1e-8:
                    stop_reason = "Step became too small near critical depth"
                    break
                # First-order explicit step, with local step-halving to keep the
                # same flow regime and ensure a positive physical depth.
                for attempt in range(35):
                    next_y = y + sign * f * dx
                    if (np.isfinite(next_y) and next_y > 0
                            and (next_y - yc) * (y - yc) > 0
                            and abs(next_y - y) <= 0.05 * max(y, 0.05)):
                        break
                    dx *= 0.5
                else:
                    stop_reason = "Unable to advance without crossing critical depth"
                    break
            except (ValueError, ZeroDivisionError, OverflowError) as exc:
                warning = str(exc)
                stop_reason = "Integration stopped near a singularity"
                break
            t_values.append(t + dx)
            depth_values.append(next_y)
        else:
            stop_reason = "Numerical step limit reached"
            warning = "Maximum number of explicit integration steps reached"

        extent = max(t_values[-1], 0.01)
        # Add a small amount of horizontal breathing room, but do not distort
        # the numerical results or extend the water-surface curve artificially.
        L = max(min_display_length, extent * 1.04) if auto_length else manual_length
        x0 = L if side == "Downstream" else 0.0
        xs = np.array([L - t if side == "Downstream" else t for t in t_values])
        ys = np.array(depth_values)
        order = np.argsort(xs)
        xs, ys = xs[order], ys[order]

        # Always show an inclined bed. For steep channels, apply a clearly labelled
        # vertical exaggeration to the DEVIATION from the straight bed datum.
        # The numerical water-surface profile and hydraulic calculations are unchanged.


        vertical_exaggeration = st.slider(
            "Vertical exaggeration of flow depths (visual only)",
            min_value=1, max_value=30, value=8, step=1,
            help="Magnifies distances above the sloping bed so the hydraulic profile remains visible. This does not alter the computed depths."
        )

        xline = np.linspace(0, L, 300)
        zline = -S0 * xline
        bed_at_profile = -S0 * xs

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=xline, y=zline, name="Channel bed",
            line=dict(color="#475569", width=3),
            hovertemplate="x = %{x:.1f} m<br>Bed elevation = %{y:.3f} m<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=xline, y=zline + vertical_exaggeration * yn,
            name="Uniform flow (normal depth)",
            line=dict(color="#16a34a", width=2.5, dash="dash"),
            customdata=np.full_like(xline, yn),
            hovertemplate="x = %{x:.1f} m<br>Normal depth = %{customdata:.3f} m<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=xline, y=zline + vertical_exaggeration * yc,
            name="Critical depth", line=dict(color="#dc2626", width=2.5, dash="dot"),
            customdata=np.full_like(xline, yc),
            hovertemplate="x = %{x:.1f} m<br>Critical depth = %{customdata:.3f} m<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=xs, y=bed_at_profile + vertical_exaggeration * ys,
            name="Water surface", line=dict(color="#0284c7", width=3.5),
            customdata=ys,
            hovertemplate="x = %{x:.1f} m<br>Flow depth = %{customdata:.3f} m<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=[x0], y=[-S0 * x0 + vertical_exaggeration * yb],
            mode="markers", name="Boundary condition",
            marker=dict(symbol="circle", size=15, color="white", line=dict(color="#075985", width=3)),
            hovertemplate=f"Boundary at x = {x0:.1f} m<br>Prescribed depth = {yb:.3f} m<extra></extra>",
        ))
        fig.update_yaxes(title_text="Display elevation [m] (depths vertically exaggerated)")
        st.caption(
            f"The channel bed is always inclined at S₀ = {S0:.5f}. "
            f"Water depths are magnified ×{vertical_exaggeration} for display only; "
            "hover labels report true depths. Display elevations above the bed are not physical elevations when exaggeration > 1."
        )

        fig.update_layout(
            height=510,
            xaxis=dict(title="Distance x [m]", range=[0, L], showgrid=True, gridcolor="rgba(148,163,184,.18)"),
            hovermode="closest",
            legend=dict(orientation="h", y=-0.22, x=0),
            margin=dict(l=30, r=35, t=25, b=65),
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)


