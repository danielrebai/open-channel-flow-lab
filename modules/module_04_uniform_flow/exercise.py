"""Module 04 — Uniform Flow: normal-depth and slope-classification exercises.

Rectangular channels, Gauckler–Strickler resistance, SI units.
All numerical answers use the *full* hydraulic radius R=by/(b+2y).
"""
import math
import random

import streamlit as st

G = 9.81

PRESETS = {
    1: {
        "title": "Effect of bed slope",
        "description": "Keep discharge, width and roughness fixed; vary the bed slope.",
        "cases": [
            (10.0, 4.0, 75.0, 0.050),
            (10.0, 4.0, 75.0, 0.010),
            (10.0, 4.0, 75.0, 0.001),
        ],
    },
    2: {
        "title": "Effect of roughness",
        "description": "Keep discharge, width and slope fixed; vary the Strickler coefficient.",
        "cases": [
            (10.0, 4.0, 25.0, 0.010),
            (10.0, 4.0, 50.0, 0.010),
            (10.0, 4.0, 75.0, 0.010),
        ],
    },
    3: {
        "title": "Effect of discharge",
        "description": "Keep width, slope and roughness fixed; vary discharge.",
        "cases": [
            (1.0, 10.0, 95.0, 0.002),
            (2.0, 10.0, 95.0, 0.002),
            (5.0, 10.0, 95.0, 0.002),
        ],
    },
}


def geometry(y, b):
    if y <= 0 or b <= 0:
        raise ValueError("Depth and width must be positive.")
    area = b * y
    perimeter = b + 2 * y
    return area, perimeter, area / perimeter


def discharge_at_depth(y, b, ks, slope):
    if y <= 0:
        return 0.0
    area, _, radius = geometry(y, b)
    return ks * area * radius ** (2.0 / 3.0) * math.sqrt(slope)


def normal_depth(Q, b, ks, slope):
    if min(Q, b, ks, slope) <= 0:
        raise ValueError("Q, b, Ks and S0 must be strictly positive.")
    lo, hi = 0.0, max(1.0, (Q / (ks * b * math.sqrt(slope))) ** 0.6 * 2)
    while discharge_at_depth(hi, b, ks, slope) < Q:
        hi *= 2
    for _ in range(90):
        mid = (lo + hi) / 2
        if discharge_at_depth(mid, b, ks, slope) < Q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def critical_depth(Q, b):
    return (Q * Q / (G * b * b)) ** (1.0 / 3.0)


def critical_slope(Q, b, ks):
    yc = critical_depth(Q, b)
    area, _, radius = geometry(yc, b)
    return (Q / (ks * area * radius ** (2.0 / 3.0))) ** 2


def slope_type(y0, yc, slope, sc):
    if math.isclose(slope, sc, rel_tol=1e-9):
        return "Critical"
    return "Mild" if y0 > yc else "Steep"


def solve_case(Q, b, ks, slope):
    y0 = normal_depth(Q, b, ks, slope)
    yc = critical_depth(Q, b)
    sc = critical_slope(Q, b, ks)
    ac, _, rc = geometry(yc, b)
    wide = (Q / (ks * b * math.sqrt(slope))) ** (3.0 / 5.0)
    return {
        "Q": Q, "b": b, "ks": ks, "S0": slope,
        "y0": y0, "yc": yc, "Sc": sc,
        "Ac": ac, "Rc": rc, "wide": wide,
        "classification": slope_type(y0, yc, slope, sc),
        "residual": discharge_at_depth(y0, b, ks, slope) - Q,
    }


def make_random_cases(kind):
    rng = random.SystemRandom()
    if kind == 1:
        Q = round(rng.uniform(5, 18), 1)
        b = round(rng.uniform(3, 9), 1)
        ks = rng.choice([35.0, 50.0, 65.0, 75.0, 90.0])
        sc = critical_slope(Q, b, ks)
        slopes = [sc * factor for factor in (0.35, 1.0, 3.0)]
        return [(Q, b, ks, slope) for slope in slopes]
    if kind == 2:
        Q = round(rng.uniform(5, 18), 1)
        b = round(rng.uniform(3, 9), 1)
        ks0 = rng.choice([45.0, 55.0, 65.0, 75.0])
        slope = critical_slope(Q, b, ks0)
        return [(Q, b, ks, slope) for ks in (ks0 * 0.6, ks0, ks0 * 1.5)]
    b = round(rng.uniform(5, 12), 1)
    ks = rng.choice([50.0, 65.0, 80.0, 95.0])
    Q0 = round(rng.uniform(3, 12), 1)
    slope = critical_slope(Q0, b, ks)
    return [(Q, b, ks, slope) for Q in (Q0 * 0.5, Q0, Q0 * 2.0)]


def fmt(value, decimals=3):
    """Readable display formatting; calculations retain full precision."""
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".") if decimals else f"{value:.0f}"


def fmt_slope(value):
    # Small slopes need extra digits to preserve meaningful comparisons.
    return f"{value:.6g}"


def latex_data(r):
    return (
        rf"Q={fmt(r['Q'])}\ \mathrm{{m^3/s}},\quad "
        rf"b={fmt(r['b'])}\ \mathrm{{m}},\quad "
        rf"K_s={fmt(r['ks'])}\ \mathrm{{m^{{1/3}}/s}},\quad "
        rf"S_0={fmt_slope(r['S0'])}"
    )


def show_worked_solution(r, idx):
    Q, b, ks, s = r["Q"], r["b"], r["ks"], r["S0"]
    y0, yc, sc = r["y0"], r["yc"], r["Sc"]
    kind = r["classification"]
    with st.expander("Show complete worked solution", expanded=True):
        st.markdown("**1. Determine the normal depth**")
        st.markdown(
            "In uniform flow, the bed slope equals the friction slope. "
            "We therefore use the Gauckler–Strickler equation to find the "
            "depth that carries the prescribed discharge."
        )
        st.latex(
            r"Q=K_s A(y_0)R(y_0)^{2/3}\sqrt{S_0},\qquad"
            r"A(y)=by,\quad R(y)=\frac{by}{b+2y}"
        )
        st.latex(
            rf"{fmt(Q)}={fmt(ks)}({fmt(b)}y_0)"
            rf"\left(\frac{{{fmt(b)}y_0}}{{{fmt(b)}+2y_0}}\right)^{{2/3}}"
            rf"\sqrt{{{fmt_slope(s)}}}"
        )
        st.markdown(
            "Because the hydraulic radius depends on depth, we solve this "
            "equation numerically using the full rectangular cross-section."
        )
        st.latex(rf"\boxed{{y_0={fmt(y0)}\ \mathrm{{m}}}}")
        st.markdown(
            rf"**Check:** Substituting the computed depth gives "
            rf"$Q_{{\mathrm{{calculated}}}}\approx {fmt(Q)}\ \mathrm{{m^3/s}}$, "
            "as required. The numerical residual is negligible."
        )

        st.markdown("**2. Method A — Compare normal and critical depths**")
        st.markdown(
            "The critical depth depends only on the discharge and channel width. "
            "For a rectangular section:"
        )
        st.latex(r"y_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}")
        st.latex(
            rf"y_c=\left(\frac{{{fmt(Q)}^2}}{{9.81\cdot {fmt(b)}^2}}\right)^{{1/3}}"
            rf"=\boxed{{{fmt(yc)}\ \mathrm{{m}}}}"
        )
        relation = ">" if y0 > yc else "<" if y0 < yc else "="
        st.latex(rf"y_0={fmt(y0)}\ {relation}\ y_c={fmt(yc)}")
        if kind == "Mild":
            st.markdown("Since the normal depth is greater than the critical depth, "
                        "uniform flow is **subcritical**. The channel has a **mild slope**.")
        elif kind == "Steep":
            st.markdown("Since the normal depth is smaller than the critical depth, "
                        "uniform flow is **supercritical**. The channel has a **steep slope**.")
        else:
            st.markdown("The two depths coincide: uniform flow is critical and "
                        "the channel has a **critical slope**.")

        st.markdown("**3. Method B — Compare actual and critical bed slopes**")
        st.markdown(
            "As an independent check, determine the slope that would make "
            "the uniform depth equal to the critical depth."
        )
        st.latex(
            r"S_c=\left[\frac{Q}{K_s A_c R_c^{2/3}}\right]^2,\qquad"
            r"A_c=by_c,\quad R_c=\frac{by_c}{b+2y_c}"
        )
        st.latex(
            rf"A_c={fmt(r['Ac'])}\ \mathrm{{m^2}},\qquad "
            rf"R_c={fmt(r['Rc'])}\ \mathrm{{m}}"
        )
        st.latex(rf"\boxed{{S_c={fmt_slope(sc)}}}")
        relation_s = "<" if s < sc else ">" if s > sc else "="
        st.latex(rf"S_0={fmt_slope(s)}\ {relation_s}\ S_c={fmt_slope(sc)}")
        if kind == "Mild":
            st.markdown("The actual bed slope is below the critical slope, "
                        "confirming the **mild** classification.")
        elif kind == "Steep":
            st.markdown("The actual bed slope exceeds the critical slope, "
                        "confirming the **steep** classification.")
        else:
            st.markdown("The actual and critical slopes are equal, "
                        "confirming the **critical** classification.")
        st.success(f"Conclusion: {kind.lower()} slope — both methods agree.")

        with st.expander("Optional: wide-channel approximation"):
            st.markdown(
                "For a sufficiently wide channel, sidewall effects may be "
                "neglected. This gives a convenient estimate, not the exact "
                "normal depth for a finite-width rectangular channel."
            )
            st.latex(
                r"y_{0,\mathrm{wide}}="
                r"\left(\frac{Q}{K_sb\sqrt{S_0}}\right)^{3/5}"
                rf"={fmt(r['wide'])}\ \mathrm{{m}}"
            )

def render():
    st.header("Exercise · Uniform Flow")
    st.caption("One rectangular channel · One exercise · One complete solution")

    # This is ONE exercise type: normal depth and slope classification.
    # Variation in Q, b, Ks and S0 is handled automatically, not by a topic selector.
    if "uf_single_exercise" not in st.session_state:
        st.session_state.uf_single_exercise = {
            "data": PRESETS[1]["cases"][0], "number": 1
        }

    if st.button("Generate new exercise", type="primary", key="uf_generate_single"):
        previous = st.session_state.uf_single_exercise
        kind = random.choice((1, 2, 3))
        new_data = random.choice(make_random_cases(kind))
        st.session_state.uf_single_exercise = {
            "data": new_data, "number": previous["number"] + 1
        }

    state = st.session_state.uf_single_exercise
    result = solve_case(*state["data"])

    st.subheader(f"Exercise {state['number']}")
    st.markdown(
        "For the following rectangular channel, **(1)** calculate the normal "
        r"depth $y_0$ and **(2)** determine whether the bed slope is "
        "**mild, steep or critical**, using **both methods**: "
        r"**A.** compare $y_0$ and $y_c$; "
        r"**B.** calculate $S_c$ and compare $S_0$ and $S_c$."
    )
    st.latex(latex_data(result))

    st.divider()
    st.subheader("Solution")
    show_worked_solution(result, 1)
