import numpy as np
import plotly.graph_objects as go
import streamlit as st

G = 9.81

st.set_page_config(page_title="Open Channel Flow Lab", page_icon="🌊", layout="wide")
st.title("🌊 Open Channel Flow Lab")
st.caption("Modulo 01 · Canale rettangolare prismatico · Moto permanente gradualmente variato")

with st.sidebar:
    st.header("Parametri")
    Q = st.number_input("Portata Q [m³/s]", min_value=0.01, value=3.0, step=0.1)
    b = st.number_input("Larghezza b [m]", min_value=0.1, value=3.0, step=0.1)
    S0 = st.number_input("Pendenza del fondo S₀ [m/m]", min_value=0.00001, max_value=0.2, value=0.002, step=0.0005, format="%.5f")
    n = st.number_input("Manning n [s/m¹ᐟ³]", min_value=0.005, max_value=0.2, value=0.025, step=0.001, format="%.3f")
    L = st.number_input("Lunghezza canale L [m]", min_value=10.0, max_value=5000.0, value=200.0, step=10.0)
    side = st.radio("Condizione al contorno", ["Valle", "Monte"])
    yb = st.number_input("Tirante imposto y [m]", min_value=0.02, max_value=30.0, value=1.2, step=0.05)


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
        raise ValueError("Tirante non positivo")
    denominator = 1 - froude_squared(y)
    if abs(denominator) < 0.002:
        raise ValueError("Vicino al tirante critico")
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
regime = "M (pendenza dolce)" if yn > yc else "S (pendenza forte)" if yn < yc else "C (pendenza critica)"
subcritical = yb > yc
compatible = (subcritical and side == "Valle") or ((not subcritical) and side == "Monte")

step = min(1.0, L / 200)
sign = -1 if side == "Valle" else 1
x0 = L if side == "Valle" else 0.0
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
            raise ValueError("Il profilo raggiunge o attraversa la profondità critica")
        if abs(ynext - y) > max(0.2, 0.2 * y):
            raise ValueError("Variazione eccessiva del tirante in un passo")
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
c1.metric("Tirante normale", f"{yn:.3f} m")
c2.metric("Tirante critico", f"{yc:.3f} m")
c3.metric("Pendenza", regime)

if not compatible:
    st.warning("La condizione al contorno è sul lato normalmente non controllante per questo regime. Il profilo integrato è matematico e potrebbe non rappresentare una soluzione fisica realizzabile.")
if warning:
    st.warning(f"Integrazione interrotta: {warning}. Non viene forzato il passaggio attraverso la condizione critica.")

xline = np.linspace(0, L, 300)
zline = -S0 * xline
fig = go.Figure()
fig.add_trace(go.Scatter(x=xline, y=zline, name="Fondo", line=dict(color="#555555", width=3)))
fig.add_trace(go.Scatter(x=xline, y=zline + yn, name="Tirante normale", line=dict(color="#e59b2d", dash="dash")))
fig.add_trace(go.Scatter(x=xline, y=zline + yc, name="Tirante critico", line=dict(color="#a35fb7", dash="dot")))
fig.add_trace(go.Scatter(x=xs, y=-S0 * xs + ys, name="Pelo libero", line=dict(color="#1789cf", width=4)))
fig.update_layout(title="Profilo longitudinale", xaxis_title="Distanza x [m]", yaxis_title="Quota relativa [m]", hovermode="x unified", legend=dict(orientation="h", y=-0.3), margin=dict(l=30, r=20, t=55, b=35))
st.plotly_chart(fig, use_container_width=True)

st.subheader("Interpretazione")
zone = "1" if yb > max(yn, yc) else "3" if yb < min(yn, yc) else "2"
st.write(f"Il tirante imposto è **{'subcritico' if subcritical else 'supercritico' if yb < yc else 'critico'}**. Classificazione locale: **{regime[0]}{zone}** (se la pendenza non è critica).")
st.info("Il modello risolve solo tratti di moto gradualmente variato. Non calcola risalti, paratoie o transizioni rapidamente variate. Vicino alla profondità critica l'integrazione si arresta.")

with st.expander("Equazioni e ipotesi del modello"):
    st.latex(r"\frac{dy}{dx}=\frac{S_0-S_f}{1-Fr^2}")
    st.latex(r"A=by,\quad R=\frac{by}{b+2y}")
    st.latex(r"S_f=\left(\frac{nQ}{AR^{2/3}}\right)^2")
    st.latex(r"Fr^2=\frac{Q^2}{gb^2y^3}")
    st.latex(r"y_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}")
    st.write("Ipotesi: canale rettangolare prismatico, moto permanente, pressione idrostatica, coefficiente di energia assunto unitario e scabrezza costante. Integrazione numerica RK4 con passo massimo di 1 m.")
