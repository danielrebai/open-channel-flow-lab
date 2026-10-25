import math
import random
import numpy as np
import plotly.graph_objects as go
import streamlit as st

G = 9.81

st.set_page_config(page_title="Open Channel Flow Lab", page_icon="🌊", layout="wide")
st.title("🌊 Open Channel Flow Lab · v13")
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
    st.caption(
        "Adapted from the uploaded handwritten notes, pp. 1–12 "
        "(manuscript pages 20–31). Numerical integration: Defina, §8.2.1."
    )

    st.markdown("""
    ### 1. Governing equation and physical meaning

    Consider steady, gradually varied flow in a prismatic channel.
    Let **s increase downstream**, let **i** denote the bed slope,
    and let **j** denote the friction slope (energy loss per unit length).
    The notes begin with the energy equation:
    """)
    st.latex(r"\frac{dE}{ds}=i-j")
    st.markdown(
        "For a fixed discharge, the specific energy is a function of depth. "
        "Applying the chain rule gives the fundamental profile equation:"
    )
    st.latex(
        r"\frac{dE}{ds}=\frac{dE}{dh}\frac{dh}{ds}=i-j"
    )
    st.latex(
        r"\boxed{\frac{dh}{ds}=\frac{i-j}{dE/dh}}"
    )
    st.markdown(
        "This is the central reasoning in the handwritten notes: "
        "**the sign of the depth gradient follows from the signs of "
        "the energy gradient and of the friction imbalance**. "
        "For a rectangular channel, the specific energy and its derivative are:"
    )
    st.latex(
        r"E(h)=h+\frac{Q^2}{2gb^2h^2},\qquad "
        r"\frac{dE}{dh}=1-Fr^2"
    )
    st.latex(
        r"\boxed{\frac{dh}{ds}=\frac{i-j}{1-Fr^2}},\qquad "
        r"Fr^2=\frac{Q^2}{gb^2h^3}"
    )
    st.markdown("""
    The manuscript uses **h** for water depth, **k** for critical depth,
    and **h₀** for normal depth. The Toy uses the equivalent symbols
    **y**, **y꜀** and **yₙ**.
    """)

    st.markdown("""
    ### 2. Critical and normal depths

    At critical flow, the specific energy reaches its minimum:
    """)
    st.latex(r"\left.\frac{dE}{dh}\right|_{h=k}=0,\qquad Fr=1")
    st.latex(r"k=\left(\frac{Q^2}{gb^2}\right)^{1/3}")
    st.markdown(
        "For a rectangular channel, Manning's law gives the friction slope:"
    )
    st.latex(
        r"A=bh,\quad R=\frac{bh}{b+2h},\quad "
        r"j(h)=\left(\frac{nQ}{AR^{2/3}}\right)^2"
    )
    st.markdown(
        "In a channel with positive bed slope, normal depth h₀ is "
        "defined by the uniform-flow condition:"
    )
    st.latex(r"j(h_0)=i")
    st.markdown(
        "The notes emphasize two characteristic depths. At **h = k**, "
        "the denominator of the GVF equation vanishes; at **h = h₀**, "
        "the numerator vanishes. These have different physical meanings."
    )

    st.markdown("### 3. Signs and asymptotic behavior")
    st.markdown(
        "The sign chart below follows the handwritten analysis "
        "(especially manuscript pp. 20–21):"
    )
    st.table({
        "Condition": ["h < k", "h = k", "h > k",
                      "h = h₀ (positive slope)"],
        "Sign / consequence": [
            "dE/dh < 0: supercritical",
            "dE/dh = 0: critical-flow singularity",
            "dE/dh > 0: subcritical",
            "i − j = 0: uniform-flow equilibrium"
        ]
    })
    st.markdown("""
    As **h approaches h₀**, the depth gradient tends to zero and the
    profile approaches uniform flow asymptotically.

    At **h = k**, the denominator vanishes. A regular gradually varied
    profile cannot generally be continued through this point using the
    ordinary GVF equation. The notes identify the resulting limiting
    behavior as a **vertical tangent** in the depth profile, except
    for special cases requiring separate analysis.
    """)

    st.markdown("### 4. Mild-slope channels")
    st.latex(r"\boxed{h_0>k}")
    st.markdown(
        "The manuscript discusses the three mild-slope profiles "
        "(pp. 22–23). Their classification follows directly from "
        "the relative position of the water depth:"
    )
    st.table({
        "Profile": ["M1", "M2", "M3"],
        "Depth range": ["h > h₀ > k", "k < h < h₀", "h < k < h₀"],
        "dh/ds": ["Positive", "Negative", "Positive"],
        "Regime": ["Subcritical", "Subcritical", "Supercritical"]
    })
    st.markdown("""
    - **M1:** a backwater curve above normal depth; it approaches
      uniform flow in the upstream direction.
    - **M2:** a drawdown curve between normal and critical depths.
    - **M3:** a supercritical profile below critical depth.

    The critical depth and normal depth are not interchangeable:
    one is determined by specific energy, the other by friction balance.
    """)

    st.markdown("### 5. Steep-slope channels")
    st.latex(r"\boxed{h_0<k}")
    st.markdown(
        "For steep channels, the notes classify the profiles "
        "as follows (pp. 24–25):"
    )
    st.table({
        "Profile": ["S1", "S2", "S3"],
        "Depth range": ["h > k > h₀", "h₀ < h < k", "h < h₀ < k"],
        "dh/ds": ["Positive", "Negative", "Positive"],
        "Regime": ["Subcritical", "Supercritical", "Supercritical"]
    })
    st.markdown("""
    The signs result from combining **i − j** with **dE/dh**.
    In particular, **S1** is subcritical even though the channel
    is steep: the channel classification and the *local* flow regime
    are distinct concepts.
    """)

    st.markdown("### 6. Horizontal and adverse slopes")
    st.markdown(
        "The manuscript also considers **horizontal channels** "
        "(page 26) and introduces **negative/adverse slopes** "
        "(page 27). These are part of the theory, but the current "
        "Toy and Exercise solvers are restricted to **i > 0**."
    )
    st.latex(r"i=0\quad\Longrightarrow\quad i-j=-j<0")
    st.markdown(
        "For a horizontal channel, the sign of dh/ds is therefore "
        "opposite to the sign of dE/dh. In an adverse channel "
        "(i < 0), the numerator i − j is likewise negative for "
        "positive friction losses. Neither case has a finite normal "
        "depth defined by j = i with j > 0."
    )

    st.markdown("### 7. Disturbances and boundary conditions")
    st.markdown("""
    The handwritten notes then shift from profile classification
    to **perturbation propagation** and **boundary conditions**
    (pp. 28–31).

    The physical principle is that small disturbances can propagate
    in both directions relative to the channel in **subcritical flow**,
    but only downstream in **supercritical flow**.
    """)
    st.table({
        "Flow regime": ["Subcritical (Fr < 1)", "Supercritical (Fr > 1)"],
        "Prescribed depth": ["Downstream boundary", "Upstream boundary"],
        "Integrate": ["Upstream", "Downstream"]
    })
    st.markdown(
        "The manuscript illustrates these rules with water-surface "
        "sketches and sign checks for dh/ds. They are the physical "
        "reason why the Toy rejects a prescribed depth at the "
        "wrong end of the reach."
    )

    st.markdown("### 8. Numerical integration of a profile")
    st.markdown(
        "To turn the qualitative classification into a computed "
        "profile, the app uses the **explicit spatial Euler method** "
        "given in Defina, §8.2.1. This numerical step is taken "
        "from the Defina reference rather than from the handwritten "
        "classification sketches."
    )
    st.latex(
        r"\left(\frac{dh}{ds}\right)_i"
        r"=\left(\frac{i-j}{1-Fr^2}\right)_i"
    )
    st.markdown("**Subcritical — integrate upstream:**")
    st.latex(
        r"\boxed{h_{i+1}=h_i-"
        r"\left(\frac{i-j}{1-Fr^2}\right)_i\Delta s}"
    )
    st.markdown("**Supercritical — integrate downstream:**")
    st.latex(
        r"\boxed{h_{i+1}=h_i+"
        r"\left(\frac{i-j}{1-Fr^2}\right)_i\Delta s}"
    )
    st.markdown(
        "The numerical step is reduced near critical conditions; "
        "the app does not force the profile across critical depth. "
        "The same hydraulic calculations appear in the Toy and "
        "in the fully worked exercises."
    )

    st.caption(
        "Primary source: uploaded handwritten notes, manuscript pages "
        "20–31 (PDF pages 1–12). The notes' diagrams and sign analysis "
        "inform the explanations above. Supplementary numerical source: "
        "Andrea Defina, Profili di moto permanente (2010), §8.2.1."
    )

with exercise_tab:
    st.header("Exercise · Gradually Varied Flow")

    # Generate hydraulically admissible, numerically verified exercises.
    # A dedicated random generator avoids changing other app controls.
    def make_exercise():
        rng = random.SystemRandom()
        for _ in range(3000):
            Q = round(rng.uniform(1.5, 8.0), 2)
            b = round(rng.uniform(2.5, 7.0), 2)
            n = round(rng.uniform(0.018, 0.035), 3)
            yc = (Q**2 / (G*b**2))**(1/3)
            target = rng.choice(["M1", "M2", "M3", "S1", "S2", "S3"])
            # Specify normal depth first; derive the bed slope from Manning.
            yn = yc*rng.uniform(1.35, 2.2) if target[0] == "M" else yc*rng.uniform(0.55, 0.77)
            A, R = b*yn, b*yn/(b+2*yn)
            S0 = (n*Q/(A*R**(2/3)))**2
            S0 = round(S0, 6)
            if not 0.0001 <= S0 <= 0.08:
                continue
            # Recompute the normal depth for the displayed, rounded slope.
            lo, hi = 0.0001, 50.0
            for _ in range(90):
                mid = (lo+hi)/2
                am, rm = b*mid, b*mid/(b+2*mid)
                if (n*Q/(am*rm**(2/3)))**2 > S0:
                    lo = mid
                else:
                    hi = mid
            yn = (lo+hi)/2
            if (yn > yc) != (target[0] == "M"):
                continue
            if target[1] == "1":
                yb = max(yn,yc)*rng.uniform(1.12,1.45)
            elif target[1] == "2":
                yb = min(yn,yc) + rng.uniform(0.32,0.68)*abs(yn-yc)
            else:
                yb = min(yn,yc)*rng.uniform(0.63,0.82)
            yb = round(yb,4)
            if abs(yb-yc)/yc < 0.06:
                continue
            sub = yb > yc
            side = "downstream" if sub else "upstream"
            dx = round(min(1.0, (0.55 if sub else 0.25)*yb), 2)
            if dx < 0.05:
                continue
            N = 12
            L = round(N*dx, 2)
            sign = -1 if sub else 1
            y = yb
            valid = True
            for _ in range(N):
                A, R = b*y, b*y/(b+2*y)
                j = (n*Q/(A*R**(2/3)))**2
                fr2 = Q**2/(G*b**2*y**3)
                if abs(1-fr2) < 0.08:
                    valid = False
                    break
                ynext = y + sign*dx*(S0-j)/(1-fr2)
                if (not math.isfinite(ynext) or ynext <= 0 or
                    (ynext-yc)*(y-yc) <= 0 or
                    abs(ynext-y)/y > 0.08):
                    valid = False
                    break
                y = ynext
            if valid and abs(y-yb)>0.0005:
                return dict(Q=Q,b=b,S0=S0,n=n,yb=yb,L=L,dx=dx,side=side)
        raise RuntimeError("Could not generate a valid exercise; please retry.")

    if "exercise_case" not in st.session_state:
        st.session_state.exercise_case = make_exercise()
        st.session_state.exercise_number = 1
    if st.button("Generate another exercise", type="primary", key="new_exercise"):
        st.session_state.exercise_case = make_exercise()
        st.session_state.exercise_number += 1
    ex = st.session_state.exercise_case
    Qe, be, Se, ne = ex["Q"], ex["b"], ex["S0"], ex["n"]
    yb_e, Le, dxe = ex["yb"], ex["L"], ex["dx"]
    side_e = ex["side"]
    st.caption(f"Exercise {st.session_state.exercise_number} · Randomly generated and numerically checked")


    st.subheader("Problem statement")
    st.markdown(
        "Consider steady, gradually varied flow in a **prismatic rectangular "
        "channel**. Assume constant discharge, bed slope and Manning roughness."
    )
    st.markdown("#### Given data")
    st.latex(
        rf"\begin{{aligned}}"
        rf"Q &= {Qe:.2f}\ \mathrm{{m^3/s}} &"
        rf"b &= {be:.2f}\ \mathrm{{m}}\\"
        rf"S_0 &= {Se:.6f} &"
        rf"n &= {ne:.3f}\ \mathrm{{s/m^{{1/3}}}}\\"
        rf"y_{{\mathrm{{{side_e}}}}} &= {yb_e:.4f}\ \mathrm{{m}} &"
        rf"L &= {Le:.2f}\ \mathrm{{m}}\\"
        rf"\Delta x &= {dxe:.2f}\ \mathrm{{m}}"
        rf"\end{{aligned}}"
    )
    st.markdown(
        """
        #### Required
        1. **Classify the bed slope.** Compute the normal depth and critical depth.
        2. **Identify the profile.** Determine the profile family and the correct integration direction.
        3. **Integrate the profile.** Apply the explicit spatial method in
           Defina, §8.2.1; show the first step and tabulate the result.
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
    st.markdown("For a rectangular channel, the area and hydraulic radius are")
    st.latex(r"A(y)=by,\qquad R(y)=\frac{by}{b+2y}.")
    st.markdown("The normal depth satisfies Manning's uniform-flow equation:")
    st.latex(r"Q=\frac{1}{n}A(y_n)R(y_n)^{2/3}\sqrt{S_0}.")
    st.latex(
        rf"{Qe:.2f}=\frac{{1}}{{{ne:.3f}}}"
        rf"({be:.2f}\,y_n)"
        rf"\left(\frac{{{be:.2f}\,y_n}}{{{be:.2f}+2y_n}}\right)^{{2/3}}"
        rf"\sqrt{{{Se:.6f}}}"
    )
    st.latex(rf"\boxed{{y_n={yn_e:.4f}\ \mathrm{{m}}}}")
    st.markdown("The critical depth follows from the critical-flow condition:")
    st.latex(r"Fr=1,\qquad y_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}.")
    st.latex(
        rf"y_c=\left(\frac{{{Qe:.2f}^2}}{{{G:.2f}\cdot {be:.2f}^2}}\right)^{{1/3}}"
        rf"=\boxed{{{yc_e:.4f}\ \mathrm{{m}}}}"
    )
    comparison = ">" if yn_e > yc_e else "<"
    st.latex(rf"y_n\;{comparison}\;y_c\quad\Longrightarrow\quad"
             rf"\boxed{{\text{{{slope_e}}}}}")

    st.markdown("### 2. Water-surface profile")
    if zone_e == "1":
        relation = rf"{yb_e:.4f}>\max({yn_e:.4f},\,{yc_e:.4f})"
    elif zone_e == "3":
        relation = rf"{yb_e:.4f}<\min({yn_e:.4f},\,{yc_e:.4f})"
    else:
        relation = (rf"{min(yn_e,yc_e):.4f}<{yb_e:.4f}"
                    rf"<{max(yn_e,yc_e):.4f}")
    st.latex(relation)
    st.latex(rf"\boxed{{\text{{Profile {profile_e}}}}}")
    st.markdown("At the prescribed boundary, the Froude number is")
    st.latex(
        rf"Fr=\sqrt{{\frac{{Q^2}}{{g\,b^2\,y^3}}}}"
        rf"=\boxed{{{math.sqrt(ex_fr2(yb_e)):.4f}}}"
    )
    st.markdown(
        f"The flow is **{'subcritical' if sub_e else 'supercritical'}**; "
        f"the depth must be prescribed **{side_e}**, and integration proceeds "
        f"**{'upstream' if sub_e else 'downstream'}**."
    )

    st.markdown("### 3. Numerical integration")
    st.markdown("The gradually varied flow equation is")
    st.latex(r"\frac{dy}{dx}=\frac{S_0-j}{1-Fr^2},\qquad"
             r"j=\left(\frac{nQ}{AR^{2/3}}\right)^2.")
    st.markdown("The explicit spatial discretization is")
    if sub_e:
        st.latex(r"\boxed{y_{i+1}=y_i-\left(\frac{S_0-j}{1-Fr^2}\right)_i\Delta x}")
        st.caption("Defina, equation (100): integrate from downstream to upstream.")
    else:
        st.latex(r"\boxed{y_{i+1}=y_i+\left(\frac{S_0-j}{1-Fr^2}\right)_i\Delta x}")
        st.caption("Defina, equation (101): integrate from upstream to downstream.")
    j0 = ex_sf(yb_e)
    fr20 = ex_fr2(yb_e)
    slope0 = (Se-j0)/(1-fr20)
    st.markdown("#### First integration step")
    st.latex(
        rf"\begin{{aligned}}"
        rf"j_0 &= {j0:.7f}\\"
        rf"Fr_0^2 &= {fr20:.6f}\\"
        rf"\left(\frac{{dy}}{{dx}}\right)_0"
        rf"&=\frac{{{Se:.6f}-{j0:.7f}}}{{1-{fr20:.6f}}}"
        rf"={slope0:.7f}"
        rf"\end{{aligned}}"
    )
    if len(values)>1:
        op = "-" if sub_e else "+"
        st.latex(
            rf"y_1={yb_e:.4f}\;{op}\;({dxe:.2f})({slope0:.7f})"
            rf"=\boxed{{{values[1][1]:.5f}\ \mathrm{{m}}}}"
        )
    else:
        st.warning("Integration cannot start sufficiently far from critical flow.")

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
    st.markdown(f"After **{len(values)-1} steps**, the final calculated depth is")
    st.latex(rf"\\boxed{{y(x={values[-1][0]:.2f}\\,\\mathrm{{m}})"
             rf"={values[-1][1]:.5f}\\,\\mathrm{{m}}}}")
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
