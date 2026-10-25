import numpy as np
import plotly.graph_objects as go
import streamlit as st

G = 9.81

st.set_page_config(page_title="Open Channel Flow Lab", page_icon="🌊", layout="wide")
st.title("🌊 Open Channel Flow Lab · v9")
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
    st.header("Exercise · Gradually Varied Flow")

    # Each case is a complete, reproducible exercise. The button rotates
    # through cases without changing the Toy or Theory.
    cases = [
        dict(Q=3.0, b=3.0, S0=0.002, n=0.025, yb=1.20, L=20.0, dx=2.0, side="downstream"),
        dict(Q=3.0, b=3.0, S0=0.002, n=0.025, yb=0.70, L=20.0, dx=2.0, side="downstream"),
        dict(Q=3.0, b=3.0, S0=0.020, n=0.025, yb=0.25, L=20.0, dx=2.0, side="upstream"),
        dict(Q=3.0, b=3.0, S0=0.020, n=0.025, yb=0.43, L=20.0, dx=2.0, side="upstream"),
        dict(Q=5.0, b=4.0, S0=0.0008, n=0.025, yb=1.40, L=20.0, dx=2.0, side="downstream"),
    ]
    if "exercise_case_index" not in st.session_state:
        st.session_state.exercise_case_index = 0
    if st.button("Generate another exercise", type="primary", key="new_exercise"):
        st.session_state.exercise_case_index = (
            st.session_state.exercise_case_index + 1
        ) % len(cases)
    ex = cases[st.session_state.exercise_case_index]
    Qe, be, Se, ne = ex["Q"], ex["b"], ex["S0"], ex["n"]
    yb_e, Le, dxe = ex["yb"], ex["L"], ex["dx"]
    side_e = ex["side"]
    st.caption(f"Exercise {st.session_state.exercise_case_index + 1} of {len(cases)}")

    st.subheader("Problem statement")
    st.markdown(
        "Consider a **prismatic rectangular open channel** carrying a steady "
        "discharge. The channel has constant bed slope and Manning roughness. "
        "The following data are given:"
    )
    st.markdown(
        f"""
        - Discharge: **Q = {Qe:.2f} m³/s**
        - Channel width: **b = {be:.2f} m**
        - Bed slope: **S₀ = {Se:.4f} m/m**
        - Manning roughness: **n = {ne:.3f} s/m¹ᐟ³**
        - Prescribed **{side_e}** depth: **y = {yb_e:.3f} m**
        - Channel length: **L = {Le:.0f} m**
        - Spatial integration step: **Δx = {dxe:.1f} m**
        """
    )
    st.markdown(
        """
        **Required**

        1. Calculate normal and critical depths, then **classify the bed slope**.
        2. **Identify the water-surface profile** and the correct integration direction.
        3. **Integrate the profile** using the explicit method for prismatic
           channels in Defina, §8.2.1. Show the first step and tabulate the
           calculated water depths along the reach.
        """
    )

    def ex_sf(y):
        A = be * y
        R = A / (be + 2.0*y)
        return (ne*Qe / (A*R**(2.0/3.0)))**2

    def ex_fr2(y):
        return Qe**2 / (G*be**2*y**3)

    lo, hi = 0.0001, 50.0
    for _ in range(100):
        mid = (lo+hi)/2
        if ex_sf(mid) > Se:
            lo = mid
        else:
            hi = mid
    yn_e = (lo+hi)/2
    yc_e = (Qe**2/(G*be**2))**(1.0/3.0)
    slope_e = "Mild (M)" if yn_e > yc_e else "Steep (S)"
    if yb_e > max(yn_e,yc_e):
        zone_e = "1"
    elif yb_e < min(yn_e,yc_e):
        zone_e = "3"
    else:
        zone_e = "2"
    profile_e = ("M" if yn_e > yc_e else "S") + zone_e
    sub_e = yb_e > yc_e
    expected_side = "downstream" if sub_e else "upstream"

    # The exercise set deliberately uses only physically consistent controls.
    assert side_e == expected_side
    direction_sign = -1 if sub_e else 1
    x_start = Le if sub_e else 0.0
    values = [(x_start, yb_e)]
    stopped_reason = None
    for k in range(round(Le/dxe)):
        x_i, y_i = values[-1]
        f2_i = ex_fr2(y_i)
        if abs(1.0-f2_i) < 0.01:
            stopped_reason = "critical flow approached"
            break
        dydx_i = (Se-ex_sf(y_i))/(1.0-f2_i)
        y_next = y_i + direction_sign*dxe*dydx_i
        if (not math.isfinite(y_next) or y_next <= 0
                or (y_i-yc_e)*(y_next-yc_e) <= 0):
            stopped_reason = "critical depth reached or crossed"
            break
        values.append((x_i+direction_sign*dxe, y_next))

    st.divider()
    st.subheader("Complete worked solution")
    st.markdown("### 1. Bed-slope classification")
    st.markdown("For a rectangular channel:")
    st.latex(r"A=by,\qquad R=\frac{by}{b+2y}")
    st.markdown("The normal depth is the positive solution of Manning's equation:")
    st.latex(r"Q=\frac{1}{n}A(y_n)R(y_n)^{2/3}\sqrt{S_0}")
    st.markdown(
        f"Substituting **Q = {Qe:.2f} m³/s**, **b = {be:.2f} m**, "
        f"**n = {ne:.3f}** and **S₀ = {Se:.4f}**, "
        f"numerical solution gives **yₙ = {yn_e:.4f} m**."
    )
    st.latex(r"y_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}")
    st.markdown(
        f"Therefore **y꜀ = {yc_e:.4f} m**. Since "
        f"**yₙ {'>' if yn_e > yc_e else '<'} y꜀**, "
        f"the channel has a **{slope_e.lower()}**."
    )

    st.markdown("### 2. Water-surface profile")
    st.markdown(
        f"The prescribed depth is **{yb_e:.3f} m**, compared with "
        f"**yₙ = {yn_e:.4f} m** and **y꜀ = {yc_e:.4f} m**. "
        f"It lies in **zone {zone_e}**; the profile is **{profile_e}**."
    )
    st.markdown(
        f"At the control section, **Fr = {math.sqrt(ex_fr2(yb_e)):.3f}**. "
        f"The flow is **{'subcritical' if sub_e else 'supercritical'}**. "
        f"Therefore integration proceeds **{'upstream from the downstream boundary' if sub_e else 'downstream from the upstream boundary'}**."
    )

    st.markdown("### 3. Numerical integration")
    st.markdown(
        "For a prismatic channel, Defina §8.2.1 prescribes the explicit "
        "step-by-step form of the GVF equation:"
    )
    st.latex(r"\frac{dy}{dx}=\frac{S_0-j}{1-Fr^2}")
    if sub_e:
        st.latex(r"y_{i+1}=y_i-\left(\frac{S_0-j}{1-Fr^2}\right)_i\Delta x")
        st.caption("Equation (100): subcritical flow, integrating upstream.")
    else:
        st.latex(r"y_{i+1}=y_i+\left(\frac{S_0-j}{1-Fr^2}\right)_i\Delta x")
        st.caption("Equation (101): supercritical flow, integrating downstream.")
    j0 = ex_sf(yb_e)
    fr20 = ex_fr2(yb_e)
    slope0 = (Se-j0)/(1-fr20)
    st.markdown(
        f"**First step:** at the prescribed section, "
        f"\\(j_0 = {j0:.6f}\\), \\(Fr_0^2 = {fr20:.5f}\\), "
        f"and \\((dy/dx)_0 = {slope0:.6f}\\). "
        f"With \\(\\Delta x = {dxe:.1f}\\) m, "
        f"the next depth is **y₁ = {values[1][1]:.5f} m**."
        if len(values)>1 else
        "**Integration cannot start because the control is too close to critical flow.**"
    )
    st.markdown("**Step-by-step integration table**")
    rows = []
    for k,(x_i,y_i) in enumerate(values):
        rows.append({
            "Step": k,
            "x [m]": round(x_i, 2),
            "y [m]": round(y_i, 5),
            "j [-]": round(ex_sf(y_i), 6),
            "Fr [-]": round(math.sqrt(ex_fr2(y_i)), 4),
        })
    st.dataframe(rows, hide_index=True, use_container_width=True)
    if stopped_reason:
        st.warning(f"Integration stopped: {stopped_reason}.")
    st.markdown(
        f"**Result:** after {len(values)-1} integration steps, "
        f"the calculated depth at x = {values[-1][0]:.1f} m "
        f"is **y = {values[-1][1]:.5f} m**."
    )
    import plotly.graph_objects as go
    xy = sorted(values)
    xp_e = [p[0] for p in xy]
    bed_e = [-Se*x for x in xp_e]
    fig_e = go.Figure()
    fig_e.add_trace(go.Scatter(
        x=xp_e, y=bed_e, mode="lines", name="Channel bed",
        line=dict(color="#555555", width=3)))
    fig_e.add_trace(go.Scatter(
        x=xp_e, y=[z+yn_e for z in bed_e], mode="lines",
        name="Normal depth", line=dict(color="#16a34a", dash="dash")))
    fig_e.add_trace(go.Scatter(
        x=xp_e, y=[z+yc_e for z in bed_e], mode="lines",
        name="Critical depth", line=dict(color="#dc2626", dash="dot")))
    fig_e.add_trace(go.Scatter(
        x=xp_e, y=[z+y for z,(_,y) in zip(bed_e,xy)], mode="lines+markers",
        name="Water surface", line=dict(color="#1684c5", width=3),
        marker=dict(size=4)))
    fig_e.add_trace(go.Scatter(
        x=[x_start], y=[-Se*x_start+yb_e], mode="markers",
        name="Boundary condition",
        marker=dict(symbol="circle-open", size=15,
                    color="#005b9f", line=dict(width=3))))
    fig_e.update_layout(
        title=f"{profile_e} water-surface profile",
        xaxis_title="Distance x [m]",
        yaxis_title="Relative elevation [m]",
        height=480, legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig_e, use_container_width=True)
    st.caption(
        "Reference: Andrea Defina, §8.2.1, equations (99)–(101). "
        "Explicit spatial integration with the stated fixed step. "
        "The channel bed is always inclined."
    )
