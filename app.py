import numpy as np
import plotly.graph_objects as go
import streamlit as st

G = 9.81

st.set_page_config(page_title="Open Channel Flow Lab", page_icon="🌊", layout="wide")
st.title("🌊 Open Channel Flow Lab · v8")
st.caption("Module 01 · Prismatic rectangular channel · Steady gradually varied flow")


toy_tab, theory_tab, exercise_tab = st.tabs(["Toy", "Theory", "Exercise"])

with toy_tab:
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


with theory_tab:

    st.header("Theory · Gradually Varied Flow")
    st.markdown("""
    ### 1. Physical model and assumptions

    We consider **steady, one-dimensional, gradually varied flow** in a
    **prismatic rectangular open channel**. The discharge, width, bed slope and
    Manning roughness are constant along the channel.

    The gradually varied flow approximation assumes nearly hydrostatic pressure
    distribution, small streamline curvature and sufficiently gradual changes in
    depth. Hydraulic jumps, gates and other rapidly varied transitions are **not**
    described by this equation.

    ### 2. Channel geometry and hydraulic quantities

    For a rectangular section of width \\(b\\) and water depth \\(y\\):
    """)
    st.latex(r"A=by,\qquad P=b+2y,\qquad R=\frac{A}{P}")
    st.latex(r"V=\frac{Q}{A},\qquad Fr^2=\frac{Q^2b}{gA^3}=\frac{Q^2}{gb^2y^3}")
    st.markdown("The **critical depth** is obtained by imposing \\(Fr=1\\):")
    st.latex(r"y_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}")
    st.markdown("""
    ### 3. Friction and uniform flow

    With Manning's resistance law, the energy (friction) slope is
    """)
    st.latex(r"j=S_f=\left(\frac{nQ}{AR^{2/3}}\right)^2")
    st.markdown("""
    **Uniform flow** occurs when friction slope equals bed slope:
    \\(j=S_0\\). The corresponding **normal depth** \\(y_n\\) is obtained
    numerically from Manning's equation:
    """)
    st.latex(r"Q=\frac{1}{n}A(y_n)R(y_n)^{2/3}\sqrt{S_0}")
    st.markdown("""
    ### 4. Governing equation

    Let \\(x\\) increase **downstream** and let \\(S_0\\) be the positive
    downward bed slope. For a prismatic channel, the gradually varied flow
    equation is
    """)
    st.latex(r"\boxed{\frac{dy}{dx}=\frac{S_0-j}{1-Fr^2}}")
    st.markdown("""
    The numerator compares bed slope and friction losses; the denominator
    expresses the effect of flow regime. At \\(Fr=1\\), this form is
    singular, so an ordinary GVF integration cannot be continued through
    critical flow.

    ### 5. Flow regimes and profile families

    A channel is classified by comparing normal and critical depths:
    """)
    st.markdown("""
    - **Mild slope (M):** \\(y_n>y_c\\).
    - **Steep slope (S):** \\(y_n<y_c\\).
    - **Critical slope (C):** \\(y_n=y_c\\).

    Within an M or S channel, the digit 1, 2 or 3 identifies the position
    of the local depth relative to \\(y_n\\) and \\(y_c\\):
    **Zone 1** is above both, **Zone 2** lies between them, and
    **Zone 3** is below both. This gives the familiar M1–M3 and S1–S3
    families.

    ### 6. Boundary conditions and direction of integration

    The mathematical integration direction follows the physical propagation
    of control:

    - **Subcritical flow** (\\(Fr<1\\)): prescribe a downstream depth and
      integrate **upstream**.
    - **Supercritical flow** (\\(Fr>1\\)): prescribe an upstream depth and
      integrate **downstream**.

    For this introductory model, a depth specified at the non-controlling
    end is rejected. A critical control requires a separate treatment.

    ### 7. Numerical integration — Defina, §8.2.1

    The reference document recommends an **explicit spatial integration**
    for prismatic channels. Starting from section \\(i\\), the discrete
    governing equation is
    """)
    st.latex(r"\frac{y_{i+1}-y_i}{x_{i+1}-x_i}=\left(\frac{S_0-j}{1-Fr^2}\right)_i")
    st.markdown("**Subcritical flow — from downstream to upstream**, with \\(\\Delta x=x_i-x_{i+1}>0\\) (equation 100):")
    st.latex(r"\boxed{y_{i+1}=y_i-\left(\frac{S_0-j}{1-Fr^2}\right)_i\Delta x}")
    st.markdown("**Supercritical flow — from upstream to downstream**, with \\(\\Delta x=x_{i+1}-x_i>0\\) (equation 101):")
    st.latex(r"\boxed{y_{i+1}=y_i+\left(\frac{S_0-j}{1-Fr^2}\right)_i\Delta x}")
    st.markdown("""
    The text suggests steps of approximately **1–10 times the depth**
    for subcritical flow, and **0.5–2 times the depth** for supercritical
    flow, reduced near critical conditions. The app uses depth-dependent
    steps and additional numerical safeguards; these safeguards are
    implementation choices, not separate equations from the reference.

    ### 8. How to interpret the Toy

    The **blue curve** is the calculated water surface, the **green dashed
    line** represents uniform flow (normal depth), and the **red dotted
    line** represents critical depth. The **outlined circle** marks the
    prescribed boundary condition.

    The bed is always shown inclined. For legibility, depths above the
    inclined bed may be vertically exaggerated in the display. This does
    **not** alter the calculated hydraulic depths.

    **Reference:** Andrea Defina, *Profili di moto permanente* (2010),
    Section 8.2.1, equations (99)–(101), printed pages 129–130.

    **Scope:** This module models only gradually varied flow in a prismatic
    rectangular channel. It is not a solver for hydraulic jumps or local
    hydraulic structures.
    """)


with exercise_tab:
    st.header("Exercise 01 · Classify, identify, integrate")
    st.markdown("""
    A **prismatic rectangular channel** carries steady discharge.
    Assume hydrostatic pressure, gradually varied flow and Manning resistance.

    **Given data**
    """)
    st.table({
        "Quantity": ["Discharge Q", "Width b", "Bed slope S₀",
                     "Manning roughness n", "Downstream depth y(L)",
                     "Integration step Δx", "Reach length L"],
        "Value": ["3.00 m³/s", "3.00 m", "0.002 m/m",
                  "0.025 s/m¹ᐟ³", "1.20 m", "2.00 m", "100 m"]
    })
    eq_q, eq_b, eq_s, eq_n = 3.0, 3.0, 0.002, 0.025
    eq_yb, eq_dx, eq_L = 1.20, 2.0, 100.0
    eq_yc = (eq_q**2 / (G * eq_b**2))**(1/3)

    def ex_sf(y):
        A = eq_b*y
        R = A/(eq_b+2*y)
        return (eq_n*eq_q/(A*R**(2/3)))**2

    lo, hi = 0.001, 10.0
    for _ in range(90):
        mid = (lo+hi)/2
        if ex_sf(mid) > eq_s:
            lo = mid
        else:
            hi = mid
    eq_yn = (lo+hi)/2
    eq_fr2 = eq_q**2/(G*eq_b**2*eq_yb**3)
    eq_gradient = (eq_s-ex_sf(eq_yb))/(1-eq_fr2)
    eq_first = eq_yb-eq_gradient*eq_dx

    st.subheader("1 · Classify the bed slope")
    st.write("Determine the normal depth and critical depth, then classify the channel.")
    slope_answer = st.radio(
        "Slope classification", ["Choose an answer", "Mild (M)", "Steep (S)", "Critical (C)"],
        key="ex_slope"
    )
    yn_answer = st.number_input("Your normal depth yₙ [m]", min_value=0.0,
                                value=0.0, step=0.01, format="%.3f", key="ex_yn")
    yc_answer = st.number_input("Your critical depth y꜀ [m]", min_value=0.0,
                                value=0.0, step=0.01, format="%.3f", key="ex_yc")

    st.subheader("2 · Identify the water-surface profile")
    profile_answer = st.selectbox(
        "Profile type", ["Choose an answer", "M1", "M2", "M3", "S1", "S2", "S3"],
        key="ex_profile"
    )
    direction_answer = st.radio(
        "Correct direction of integration",
        ["Choose an answer", "From downstream to upstream", "From upstream to downstream"],
        key="ex_direction"
    )

    st.subheader("3 · Integrate the profile")
    st.write(
        "Use the **explicit method in Defina §8.2.1 (equation 100)**. "
        "Starting at x = 100 m with y = 1.20 m, compute the depth "
        "at x = 98 m using one step of Δx = 2 m."
    )
    first_answer = st.number_input(
        "Calculated depth y(98 m) [m]", min_value=0.0, value=0.0,
        step=0.001, format="%.4f", key="ex_first"
    )
    st.caption("Suggested tolerances: ±0.01 m for depths, ±0.002 m for the first integration step.")

    if st.button("Check my answers", type="primary", key="ex_check"):
        checks = [
            ("Slope classification", slope_answer == "Mild (M)"),
            ("Normal depth", abs(yn_answer-eq_yn) <= 0.01),
            ("Critical depth", abs(yc_answer-eq_yc) <= 0.01),
            ("Profile type", profile_answer == "M1"),
            ("Integration direction", direction_answer == "From downstream to upstream"),
            ("First integration step", abs(first_answer-eq_first) <= 0.002),
        ]
        st.session_state["exercise_checked"] = True
        st.session_state["exercise_checks"] = checks

    if st.session_state.get("exercise_checked", False):
        checks = st.session_state["exercise_checks"]
        st.metric("Correct answers", f"{sum(ok for _,ok in checks)} / {len(checks)}")
        for label, ok in checks:
            if ok:
                st.success(f"{label}: correct")
            else:
                st.error(f"{label}: check your calculation or selection")

        with st.expander("Show worked solution and integrated profile"):
            st.markdown("**Step 1 — Normal and critical depths**")
            st.latex(r"Q=\frac{1}{n}AR^{2/3}\sqrt{S_0},\qquad y_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}")
            st.write(f"yₙ = {eq_yn:.4f} m; y꜀ = {eq_yc:.4f} m. Since yₙ > y꜀, the slope is mild (M).")
            st.markdown("**Step 2 — Profile type**")
            st.write("The prescribed downstream depth exceeds both normal and critical depth: "
                     "y(L) > yₙ > y꜀. The profile is **M1**, and integration proceeds upstream.")
            st.markdown("**Step 3 — Explicit integration (equation 100)**")
            st.latex(r"y_{i+1}=y_i-\left(\frac{S_0-j}{1-Fr^2}\right)_i\Delta x")
            st.write(f"At y = 1.20 m: j = {ex_sf(eq_yb):.6f}, "
                     f"Fr² = {eq_fr2:.4f}, dy/dx = {eq_gradient:.6f}.")
            st.write(f"Therefore y(98 m) = {eq_first:.4f} m.")

            # Explicit Euler, upstream from the downstream control.
            ex_xs, ex_ys = [eq_L], [eq_yb]
            for _ in range(int(eq_L/eq_dx)):
                y = ex_ys[-1]
                denom = 1-eq_q**2/(G*eq_b**2*y**3)
                if abs(denom) < 0.002:
                    st.warning("Integration stopped near critical depth.")
                    break
                y_next = y-(eq_s-ex_sf(y))/denom*eq_dx
                if y_next <= 0 or not math.isfinite(y_next):
                    st.warning("Integration stopped at an invalid depth.")
                    break
                ex_xs.append(ex_xs[-1]-eq_dx)
                ex_ys.append(y_next)

            import plotly.graph_objects as go
            x_plot = list(reversed(ex_xs))
            y_plot = list(reversed(ex_ys))
            bed = [-eq_s*x for x in x_plot]
            fig_ex = go.Figure()
            fig_ex.add_trace(go.Scatter(x=x_plot, y=bed, mode="lines",
                                        name="Channel bed", line=dict(color="#555555",width=3)))
            fig_ex.add_trace(go.Scatter(x=x_plot, y=[z+eq_yn for z in bed],
                                        mode="lines", name="Normal depth",
                                        line=dict(color="#18a558",dash="dash")))
            fig_ex.add_trace(go.Scatter(x=x_plot, y=[z+eq_yc for z in bed],
                                        mode="lines", name="Critical depth",
                                        line=dict(color="#e53935",dash="dot")))
            fig_ex.add_trace(go.Scatter(x=x_plot, y=[z+y for z,y in zip(bed,y_plot)],
                                        mode="lines", name="Water surface",
                                        line=dict(color="#1684c5",width=4)))
            fig_ex.add_trace(go.Scatter(x=[eq_L], y=[-eq_s*eq_L+eq_yb],
                                        mode="markers", name="Boundary condition",
                                        marker=dict(symbol="circle-open",size=15,
                                                    color="#005b9f",line=dict(width=3))))
            fig_ex.update_layout(title="Integrated M1 profile · Explicit method",
                                 xaxis_title="Distance x [m]",
                                 yaxis_title="Relative elevation [m]",
                                 height=520, legend=dict(orientation="h",y=-0.25))
            st.plotly_chart(fig_ex, use_container_width=True)
            st.caption("The profile is computed with the explicit spatial scheme "
                       "and Δx = 2 m. The inclined bed and water-surface elevations "
                       "are plotted without vertical exaggeration.")

