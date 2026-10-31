"""Module 09 — Downward Facing Step: 3-handle toy and integrated GVF profile.

The dragger is a view of the same numerical branches used by Theory.
The upstream and downstream beds have distinct elevations at x=0.
"""
from pathlib import Path
import math

import streamlit as st
import streamlit.components.v1 as components

from . import theory as th
from .hydraulics import critical, normal, sf

_DRAGGER = components.declare_component(
    "m09_downward_step_dragger_v5",
    path=str(Path(__file__).parent / "channel_dragger"),
)

LENGTH = 100.0


def _solve_dragged(case, q, b, n, su, sd, a, length, hc, nu, nd):
    """Use Theory's Euler GVF integrator, energy step, and jump matching."""
    from .hydraulics import energy, depth_at_energy, integrate

    branches, jumps, warnings = [], [], []

    def add(x0, h0, x1, slope, side):
        xx, hh = integrate(x0, h0, x1, slope, q, b, n, hc)
        branches.append((xx, hh, side))
        return xx, hh

    def downstream_depth(h_up, branch):
        return depth_at_energy(energy(h_up, q) + a, q, branch)

    if case == "steep_steep":
        _, hu = add(-length, nu, 0, su, "U")
        add(0, downstream_depth(hu[-1], "super"), length, sd, "D")
    elif case == "mild_mild_sufficient":
        _, hd = add(length, nd, 0, sd, "D")
        hu = depth_at_energy(energy(hd[-1], q) - a, q, "sub")
        add(0, hu, -length, su, "U")
    elif case == "mild_mild_insufficient":
        add(0, hc * 1.002, -length, su, "U")
        th.find_jump(
            0, downstream_depth(hc, "super"), length, nd, sd,
            q, b, n, hc, "D", branches, jumps, warnings,
        )
    elif case == "mild_steep":
        add(0, hc * 1.002, -length, su, "U")
        add(0, downstream_depth(hc, "super"), length, sd, "D")
    else:  # steep_mild
        _, hu = add(-length, nu, 0, su, "U")
        th.find_jump(
            0, downstream_depth(hu[-1], "super"), length, nd, sd,
            q, b, n, hc, "D", branches, jumps, warnings,
        )
    return {"branches": branches, "jumps": jumps, "warnings": warnings}


def _payload(solution, case, q, b, n, su, sd, a, hc, nu, nd):
    """Serialize depths, not absolute elevations; the SVG uses the local bed.

    In particular x=0 belongs to BOTH reaches: U uses z_b=0, while
    D uses z_b=-a. They must never be inferred from x alone.
    """
    lines = []
    jumps = []
    controls = []
    if solution is not None:
        for xx, hh, side in solution["branches"]:
            if len(xx) > 1:
                lines.append({
                    "x": [float(x) for x in xx],
                    "h": [float(h) for h in hh],
                    "side": side,
                })
        for xj, h1, h2 in solution["jumps"]:
            jumps.append({"x": float(xj), "h1": float(h1), "h2": float(h2)})
        if case in ("steep_steep", "steep_mild"):
            controls.append({"x": -LENGTH, "h": nu, "side": "U", "label": "Upstream BC"})
        if case in ("mild_mild_sufficient", "mild_mild_insufficient", "steep_mild"):
            controls.append({"x": LENGTH, "h": nd, "side": "D", "label": "Downstream BC"})
        if case in ("mild_steep", "mild_mild_insufficient"):
            controls.append({"x": 0.0, "h": hc, "side": "U", "label": "Critical control"})
    return {
        "su": su, "sd": sd, "a": a, "L": LENGTH,
        "q": q, "b": b, "n": n,
        "hc": hc, "nu": nu, "nd": nd,
        "lines": lines, "jumps": jumps, "controls": controls,
        "warnings": solution["warnings"] if solution else [],
    }


def render():
    st.subheader("Channel experiment")
    st.caption(
        "Drag the upstream endpoint to change S₀,U; the downstream endpoint to "
        "change S₀,D; or the centre handle to change only the step drop a. "
        "Each reach is 100 m long. Release a handle to recompute the hydraulic profile."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        Q = st.slider("Discharge Q (m³/s)", 0.5, 20.0, 8.0, 0.5, key="m09_toy_Q")
    with c2:
        B = st.slider("Channel width B (m)", 2.0, 12.0, 4.0, 0.5, key="m09_toy_B")
    with c3:
        ks = st.slider("Strickler Kₛ (m¹ᐟ³/s)", 25, 110, 65, 1, key="m09_toy_ks")

    q = Q / B
    n = 1.0 / ks
    hc = critical(q)
    sc = sf(hc, q, B, n)
    default_geom = [0.40 * sc, 2.20 * sc, 0.35]
    if "m09_toy_geometry" not in st.session_state:
        st.session_state["m09_toy_geometry"] = default_geom
    su, sd, a = map(float, st.session_state["m09_toy_geometry"])
    nu, nd = normal(q, B, n, su), normal(q, B, n, sd)
    mild_u, mild_d = nu > hc, nd > hc
    case = ("mild" if mild_u else "steep") + "_" + ("mild" if mild_d else "steep")
    if case == "mild_mild":
        from .hydraulics import energy
        case += "_sufficient" if energy(nd, q) - a >= 1.5 * hc else "_insufficient"

    solution = None
    error = None
    try:
        solution = _solve_dragged(case, q, B, n, su, sd, a, LENGTH, hc, nu, nd)
    except (ValueError, ArithmeticError, RuntimeError, OverflowError, ZeroDivisionError) as exc:
        error = str(exc)

    # New component key/name invalidates old cached iframe resources.
    update = _DRAGGER(
        data=_payload(solution, case, q, B, n, su, sd, a, hc, nu, nd),
        key="m09_independent_handles_v5",
        default=None,
        height=530,
    )
    if isinstance(update, dict) and all(k in update for k in ("su", "sd", "a")):
        revision = update.get("revision")
        if revision != st.session_state.get("m09_toy_last_revision"):
            st.session_state["m09_toy_last_revision"] = revision
            values = [float(update[k]) for k in ("su", "sd", "a")]
            values[0] = min(0.04, max(0.00002, values[0]))
            values[1] = min(0.04, max(0.00002, values[1]))
            values[2] = min(2.5, max(0.02, values[2]))
            if all(math.isfinite(v) for v in values) and any(
                abs(new - old) > 1e-9
                for new, old in zip(values, (su, sd, a))
            ):
                st.session_state["m09_toy_geometry"] = values
                st.rerun()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Upstream slope S₀,U", f"{su:.5f}")
    k2.metric("Downstream slope S₀,D", f"{sd:.5f}")
    k3.metric("Step drop a", f"{a:.3f} m")
    k4.metric("Critical depth h_c", f"{hc:.3f} m")
    st.caption(
        f"Upstream: {'MILD' if mild_u else 'STEEP'} · "
        f"downstream: {'MILD' if mild_d else 'STEEP'} · "
        f"hₙ,U = {nu:.3f} m · hₙ,D = {nd:.3f} m"
    )
    if error:
        st.warning("A complete steady solution could not be found: " + error)
    elif solution is not None:
        for warning in solution["warnings"]:
            st.warning(warning)
        for xj, h1, h2 in solution["jumps"]:
            st.caption(f"Hydraulic jump at x = {xj:.2f} m · h₁ = {h1:.3f} m · h₂ = {h2:.3f} m")

    st.subheader("Computed longitudinal hydraulic profile")
    if solution is not None:
        plot_data = {
            "case": case, "branches": solution["branches"],
            "jumps": solution["jumps"], "warnings": solution["warnings"],
            "k": hc, "nu": nu, "nd": nd, "su": su, "sd": sd,
            "q": q, "b": B, "n": n, "a": a, "length": LENGTH,
        }
        figure = th.profile_plot(plot_data)
        figure.update_layout(height=500)
        st.plotly_chart(figure, use_container_width=True, key="m09_toy_computed_profile")
    else:
        st.info("Change the slopes or the step height to obtain an admissible hydraulic profile.")
    st.caption(
        "Adaptive Euler GVF integration; energy balance at the step and "
        "momentum matching for hydraulic jumps. The upper drawing shares "
        "the same computed depths, but is not an additional numerical solution."
    )
    if st.button("Reset channel", key="m09_toy_reset"):
        st.session_state["m09_toy_geometry"] = default_geom
        st.rerun()
