import numpy as np
import plotly.graph_objects as go
import streamlit as st

G = 9.81

st.set_page_config(page_title="Open Channel Flow Lab", page_icon="🌊", layout="wide")
st.title("🌊 Open Channel Flow Lab")
st.caption("Module 01 · Prismatic rectangular channel · Steady gradually varied flow")

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

for _ in range(12000):
    t, y = t_values[-1], depth_values[-1]
    if t >= limit - 1e-9:
        stop_reason = "Maximum channel length reached"
        break
    if auto_length and t >= min_display_length:
        if initial_departure > normal_tolerance and abs(y - yn) <= normal_tolerance:
            stop_reason = "Profile approached normal depth"
            break
        if abs(y - yc) <= critical_tolerance:
            stop_reason = "Profile approached critical depth"
            break
    try:
        gradient = rhs(y)
        # Adaptive spatial step: limit depth variation to ~2% per step,
        # while avoiding unnecessarily dense output in near-uniform reaches.
        h = min(5.0, max(0.02, 0.02 * max(y, 0.1) / max(abs(gradient), 1e-10)))
        h = min(h, limit - t)
        signed_h = sign * h
        k1 = rhs(y)
        k2 = rhs(y + signed_h * k1 / 2)
        k3 = rhs(y + signed_h * k2 / 2)
        k4 = rhs(y + signed_h * k3)
        next_y = y + signed_h * (k1 + 2*k2 + 2*k3 + k4) / 6
        if (not np.isfinite(next_y) or next_y <= 0
                or (y - yc) * (next_y - yc) <= 0):
            raise ValueError("Profile reached critical depth")
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        warning = str(exc)
        stop_reason = "Integration stopped near a singularity"
        break
    t_values.append(t + h)
    depth_values.append(next_y)

extent = max(t_values[-1], 0.01)
# Add a small amount of horizontal breathing room, but do not distort
# the numerical results or extend the water-surface curve artificially.
L = max(min_display_length, extent * 1.04) if auto_length else manual_length
x0 = L if side == "Downstream" else 0.0
xs = np.array([L - t if side == "Downstream" else t for t in t_values])
ys = np.array(depth_values)
order = np.argsort(xs)
xs, ys = xs[order], ys[order]
c1, c2, c3 = st.columns(3)
c1.metric("Normal depth", f"{yn:.3f} m")
c2.metric("Critical depth", f"{yc:.3f} m")
c3.metric("Slope type", regime)

if critical_boundary:
    st.warning("The prescribed depth is critical; the GVF equation is singular at Fr = 1.")
elif not compatible:
    st.warning("The boundary condition is on the normally non-controlling side for this flow regime. The integrated profile is a mathematical solution and may not be physically realizable.")
if warning:
    st.warning(f"Integration stopped: {warning}. Crossing critical depth is not forced.")

# For steep channels, plotting absolute elevations compresses the hydraulic depths.
# The default bed-relative view removes the large bed drop from the vertical axis.
st.subheader("Water-surface profile")
if auto_length:
    st.caption(f"Automatically selected channel length: **{L:,.1f} m** · {stop_reason or 'Profile computed'}."
               + (" The profile has not reached its asymptotic depth within the allowed length." if stop_reason == "Maximum channel length reached" else ""))
view = st.radio(
    "Vertical reference",
    ["Depth above channel bed (recommended)", "Absolute elevation"],
    horizontal=True,
    help="The bed-relative view makes depth variations visible even for steep slopes.",
)

xline = np.linspace(0, L, 300)
zline = -S0 * xline
bed_relative = view.startswith("Depth")
fig = go.Figure()
if bed_relative:
    # Fill below the water surface to make the actual flow depth easy to read.
    fig.add_trace(go.Scatter(
        x=xs, y=np.zeros_like(xs), mode="lines", name="Channel bed (reference)",
        line=dict(color="#64748b", width=2), hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="lines", name="Water surface",
        line=dict(color="#0284c7", width=3.5),
        fill="tonexty", fillcolor="rgba(56, 189, 248, 0.20)",
        hovertemplate="x = %{x:.1f} m<br>Depth = %{y:.3f} m<extra></extra>",
    ))
    fig.add_hline(y=yn, line=dict(color="#16a34a", width=2.5, dash="dash"),
                  annotation_text=f"Normal depth {yn:.3f} m", annotation_position="top right")
    fig.add_hline(y=yc, line=dict(color="#dc2626", width=2.5, dash="dot"),
                  annotation_text=f"Critical depth {yc:.3f} m", annotation_position="bottom right")
    fig.add_trace(go.Scatter(
        x=[x0], y=[yb], mode="markers", name="Boundary condition",
        marker=dict(symbol="circle", size=15, color="white", line=dict(color="#075985", width=3)),
        hovertemplate=f"Boundary at x = {x0:.1f} m<br>Prescribed depth = {yb:.3f} m<extra></extra>",
    ))
    fig.update_yaxes(title_text="Flow depth above bed [m]", rangemode="tozero")
    st.caption("Bed-relative view: the bed is displayed horizontally at y = 0. The actual bed slope is unchanged in the hydraulic calculation.")
else:
    fig.add_trace(go.Scatter(
        x=xline, y=zline, name="Channel bed", line=dict(color="#64748b", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=xline, y=zline + yn, name="Normal depth", line=dict(color="#16a34a", width=2.5, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=xline, y=zline + yc, name="Critical depth", line=dict(color="#dc2626", width=2.5, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=xs, y=-S0 * xs + ys, name="Water surface",
        line=dict(color="#0284c7", width=3.5),
    ))
    fig.add_trace(go.Scatter(
        x=[x0], y=[-S0 * x0 + yb], mode="markers", name="Boundary condition",
        marker=dict(symbol="circle", size=15, color="white", line=dict(color="#075985", width=3)),
        hovertemplate=f"Boundary at x = {x0:.1f} m<br>Prescribed depth = {yb:.3f} m<extra></extra>",
    ))
    fig.update_yaxes(title_text="Relative elevation [m]")
    st.caption("Absolute-elevation view: the large bed drop on steep slopes can visually compress the flow depths.")

fig.update_layout(
    height=510,
    xaxis=dict(title="Distance x [m]", range=[0, L], showgrid=True, gridcolor="rgba(148,163,184,.18)"),
    hovermode="closest",
    legend=dict(orientation="h", y=-0.22, x=0),
    margin=dict(l=30, r=35, t=25, b=65),
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Hydraulic interpretation")
zone = "1" if yb > max(yn, yc) else "3" if yb < min(yn, yc) else "2"
boundary_regime = "critical" if critical_boundary else "subcritical" if subcritical else "supercritical"
profile_class = f"{regime[0]}{zone}" if regime[0] != "C" else "critical-slope case"
st.write(f"The prescribed depth is **{boundary_regime}**. Local profile classification: **{profile_class}**.")
st.info("This model solves gradually varied flow only. It does not simulate hydraulic jumps, sluice gates, or rapidly varied transitions. Integration stops near critical depth.")

with st.expander("Equations and model assumptions"):
    st.latex(r"\frac{dy}{dx}=\frac{S_0-S_f}{1-Fr^2}")
    st.latex(r"A=by,\quad R=\frac{by}{b+2y}")
    st.latex(r"S_f=\left(\frac{nQ}{AR^{2/3}}\right)^2")
    st.latex(r"Fr^2=\frac{Q^2}{gb^2y^3}")
    st.latex(r"y_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}")
    st.write("Assumptions: prismatic rectangular channel, steady flow, hydrostatic pressure, unit energy coefficient, and constant roughness. Adaptive-step RK4 integration; automatic length stops near normal or critical depth or at the maximum permitted length.")
