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
    L = st.number_input("Channel length L [m]", min_value=10.0, max_value=5000.0, value=200.0, step=10.0)
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

step = min(1.0, L / 200)
sign = -1 if side == "Downstream" else 1
x0 = L if side == "Downstream" else 0.0
xs, ys = [x0], [yb]
warning = None
for _ in range(int(np.ceil(L / step))):
    x, y = xs[-1], ys[-1]
    h = sign * min(step, abs((0 if sign < 0 else L) - x))
    if abs(h) < 1e-10:
        break
    try:
        k1 = rhs(y)
        k2 = rhs(y + h * k1 / 2)
        k3 = rhs(y + h * k2 / 2)
        k4 = rhs(y + h * k3)
        ynext = y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        if ynext <= 0 or not np.isfinite(ynext) or (y - yc) * (ynext - yc) <= 0:
            raise ValueError("The profile reaches or crosses critical depth")
        if abs(ynext - y) > max(0.2, 0.2 * y):
            raise ValueError("Excessive depth change within one step")
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        warning = str(exc)
        break
    xs.append(x + h)
    ys.append(ynext)

xs = np.array(xs)
ys = np.array(ys)
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

xline = np.linspace(0, L, 300)
zline = -S0 * xline
fig = go.Figure()
fig.add_trace(go.Scatter(x=xline, y=zline, name="Channel bed", line=dict(color="#555555", width=3)))
fig.add_trace(go.Scatter(x=xline, y=zline + yn, name="Normal depth", line=dict(color="#16a34a", dash="dash")))
fig.add_trace(go.Scatter(x=xline, y=zline + yc, name="Critical depth", line=dict(color="#dc2626", dash="dot")))
fig.add_trace(go.Scatter(x=xs, y=-S0 * xs + ys, name="Water surface", line=dict(color="#1789cf", width=4)))
# Mark the prescribed boundary condition with a clearly visible circle.
fig.add_trace(go.Scatter(
    x=[x0], y=[-S0 * x0 + yb], mode="markers", name="Boundary condition",
    marker=dict(symbol="circle", size=14, color="#ffffff", line=dict(color="#0b5394", width=3)),
    hovertemplate=f"Prescribed depth: {yb:.3f} m<extra></extra>",
))
fig.update_layout(title="Longitudinal water-surface profile", xaxis_title="Distance x [m]", yaxis_title="Relative elevation [m]", hovermode="x unified", legend=dict(orientation="h", y=-0.3), margin=dict(l=30, r=20, t=55, b=35))
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
    st.write("Assumptions: prismatic rectangular channel, steady flow, hydrostatic pressure, unit energy coefficient, and constant roughness. Numerical RK4 integration with a maximum step of 1 m.")
