import math
import random
import plotly.graph_objects as go
import streamlit as st
from .hydraulics import G


def render():
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
