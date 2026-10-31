"""Module 05: free, graph-driven channel toy (no scenario selector).
Requires exercise.py in the same module and the channel_dragger folder.
"""
from pathlib import Path
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from scipy.optimize import brentq
from . import exercise as ex

_COMPONENT = components.declare_component(
    "m05_channel_dragger", path=str(Path(__file__).parent / "channel_dragger")
)



import math
from types import SimpleNamespace

# Explicit spatial Euler integration (Defina §8.2.1), used ONLY by this Toy.
# Exercise.py remains unchanged and continues using its original solver.
EULER_DX = 0.10  # maximum spatial step in metres
EULER_MIN_DX = 1e-7

def integrate(x0, y0, x1, q, b, ks, s0, yc):
    """Explicit spatial Euler (Defina), with step subdivision near critical flow.

    Every accepted step is y[i+1] = y[i] + dx * f(y[i]).  The step
    subdivision prevents a finite Euler step from jumping across y_c.
    """
    if not math.isfinite(y0) or y0 <= 0 or abs(y0-yc) < 1e-6*yc:
        raise ValueError('Cannot start Euler integration at invalid/critical depth')
    direction = 1 if x1 >= x0 else -1
    x, y = float(x0), float(y0)
    xs, ys = [x], [y]
    side = 1 if y > yc else -1
    while direction*(x1-x) > 1e-9:
        remaining = abs(x1-x)
        step = min(EULER_DX, remaining)
        fr2 = q*q/(ex.G*b*b*y**3)
        denominator = 1.0-fr2
        if abs(denominator) < 1e-8:
            break
        dydx = (s0-float(ex.sf(y,q,b,ks)))/denominator
        if not math.isfinite(dydx):
            break
        # Limit depth change to 5% of y and 40% of distance to critical.
        # This is still forward Euler, not RK45 or solve_ivp.
        if abs(dydx) > 0:
            step = min(step, 0.05*y/abs(dydx))
            if direction*dydx*side < 0:
                step = min(step, 0.40*abs(y-yc)/abs(dydx))
        if step < EULER_MIN_DX:
            break
        dx = direction*step
        y_next = y + dx*dydx
        if (not math.isfinite(y_next) or y_next <= 0
                or side*(y_next-yc) <= 1e-6*yc):
            break
        x = x + dx
        y = y_next
        xs.append(x)
        ys.append(y)
    xx = np.asarray(xs, dtype=float)
    yy = np.asarray(ys, dtype=float)
    def dense(x_query):
        v = np.asarray(x_query, dtype=float)
        if np.any(v < min(xx[0],xx[-1])-1e-7) or np.any(v > max(xx[0],xx[-1])+1e-7):
            raise ValueError('Euler profile requested outside integrated interval')
        if direction < 0:
            values = np.interp(v, xx[::-1], yy[::-1])
        else:
            values = np.interp(v, xx, yy)
        return np.asarray([values])
    return SimpleNamespace(t=xx, y=np.asarray([yy]), sol=dense, success=True)

# Reuse the existing specific-force matching logic, with the local Euler integrator.
sigma = ex.sigma

def _jump_branches_euler(d,yL):

    q,b,yc=d['q'],d['b'],d['yc']

    L1,L2=d['L1'],d['L2']

    # Supercritical approach: uniform on reach 1, then GVF on reach 2.

    up2=integrate(0,d['yn1'],L2,q,b,d['k2'],d['s2'],yc)

    # Subcritical branch: integrate from the downstream control through both reaches.

    dn2=integrate(L2,yL,0,q,b,d['k2'],d['s2'],yc)

    dn1=None

    if dn2.t[-1] <= 1e-7:

        dn1=integrate(0,float(dn2.sol(0)[0]),-L1,q,b,d['k1'],d['s1'],yc)

    def depth_up(x):

        return d['yn1'] if x<0 else float(up2.sol(x)[0])

    def depth_dn(x):

        if x<0:

            if dn1 is None: raise ValueError('No subcritical upstream branch')

            return float(dn1.sol(x)[0])

        return float(dn2.sol(x)[0])

    lo=max(-L1,float(dn1.t[-1]) if dn1 is not None else float(dn2.t[-1]))

    hi=min(L2,float(up2.t[-1]))

    if lo>=hi: raise ValueError('No overlapping branches')

    def mismatch(x): return sigma(depth_up(x),q,b)-sigma(depth_dn(x),q,b)

    xx=np.linspace(lo,hi,350)

    ff=[mismatch(float(x)) for x in xx]

    roots=[]

    for i in range(len(xx)-1):

        if ff[i]*ff[i+1]<0:

            xj=brentq(mismatch,float(xx[i]),float(xx[i+1]))

            yu,yd=depth_up(xj),depth_dn(xj)

            if yu<yc<yd: roots.append((xj,yu,yd))

    if len(roots)!=1: raise ValueError('No unique admissible jump')

    xj,yu,yd=roots[0]

    return dict(up2=up2,dn2=dn2,dn1=dn1,depth_up=depth_up,

                depth_dn=depth_dn,lo=lo,hi=hi,xj=xj,yu=yu,yd=yd,

                force=sigma(yu,q,b),residual=mismatch(xj),yL=yL)

def _clip(v, lo, hi):
    return max(lo, min(hi, float(v)))


def _build(q, b, k1, k2, s1, s2, L1, L2):
    L1 = L2 = 300  # Fixed reach lengths (m)

    yc = ex.yc_of(q, b)
    d = dict(q=q, b=b, k1=k1, k2=k2, s1=s1, s2=s2,
             L1=L1, L2=L2, yc=yc,
             yn1=ex.yn_of(q, b, k1, s1),
             yn2=ex.yn_of(q, b, k2, s2))
    mild1, mild2 = d['yn1'] > yc, d['yn2'] > yc
    d['mode'] = ('mild' if mild1 else 'steep') + '_' + ('mild' if mild2 else 'steep')
    if mild1 and not mild2:
        d['controls'] = [(0.0, float(yc))]
        eps = .002 * yc
        d['left'] = integrate(0, yc + eps, -L1, q, b, k1, s1, yc)
        d['right'] = integrate(0, yc - eps, L2, q, b, k2, s2, yc)
    elif mild1 and mild2:
        d['controls'] = [(float(L2), float(d['yn2']))]
        # Downstream uniform flow fixes the subcritical branch at the transition.
        d['left'] = integrate(0, d['yn2'], -L1, q, b, k1, s1, yc)
    elif not mild1 and not mild2:
        d['controls'] = [(-float(L1), float(d['yn1']))]
        # Upstream uniform flow fixes the supercritical branch.
        d['right'] = integrate(0, d['yn1'], L2, q, b, k2, s2, yc)
    else:
        d['controls'] = [(-float(L1), float(d['yn1'])), (float(L2), float(d['yn2']))]
        # Steep -> mild: both far-field uniform states are known.
        # Match independently integrated branches using specific force.
        d['jump'] = _jump_branches_euler(d, d['yn2'])
    return d


def _profile(d):
    L1, L2 = d['L1'], d['L2']
    xx = np.linspace(-L1, L2, 440)
    zb = ex.bed(xx, d)
    lines = []
    def append(x, y):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        lines.append((x, ex.bed(x, d) + y))
    if 'jump' in d:
        j = d['jump']
        xj = j['xj']
        a = np.linspace(-L1, xj, 210)
        c = np.linspace(xj, L2, 210)
        append(a, [j['depth_up'](float(v)) for v in a])
        append(c, [j['depth_dn'](float(v)) for v in c])
        append([xj, xj], [j['yu'], j['yd']])
    elif d['mode'] == 'mild_steep':
        a = np.linspace(float(d['left'].t[-1]), 0, 180)
        c = np.linspace(0, float(d['right'].t[-1]), 180)
        append(a, d['left'].sol(a)[0])
        append(c, d['right'].sol(c)[0])
    elif 'left' in d:
        a = np.linspace(float(d['left'].t[-1]), 0, 220)
        c = np.linspace(0, L2, 160)
        append(a, d['left'].sol(a)[0])
        append(c, np.full_like(c, d['yn2']))
    else:
        a = np.linspace(-L1, 0, 160)
        c = np.linspace(0, float(d['right'].t[-1]), 220)
        append(a, np.full_like(a, d['yn1']))
        append(c, d['right'].sol(c)[0])
    return xx, zb, lines


def _figure(d):
    xx, zb, lines = _profile(d)
    fig = go.Figure()
    fig.add_scatter(x=xx, y=zb, name='Channel bed',
                    line=dict(color='#98602e', width=5))
    fig.add_scatter(x=xx, y=zb+d['yc'], name='Critical depth',
                    line=dict(color='#dc4444', width=2, dash='dash'))
    fig.add_scatter(x=xx,
                    y=zb+np.where(xx < 0, d['yn1'], d['yn2']),
                    name='Normal depth', line=dict(color='#24904e', width=2, dash='dot'))
    for i, (x, z) in enumerate(lines):
        fig.add_scatter(x=x, y=z, name='Water surface' if i == 0 else None,
                        showlegend=(i == 0), line=dict(color='#087fcb', width=4))
    if 'jump' in d:
        fig.add_vline(x=d['jump']['xj'], line_dash='dot', line_color='#164f92')
    fig.add_vline(x=0, line_dash='dot', line_color='#888888')
    fig.update_layout(template='plotly_white', height=425,
                      margin=dict(l=15, r=15, t=12, b=10),
                      xaxis_title='Distance x (m)', yaxis_title='Elevation (m)',
                      legend=dict(orientation='h', y=-.27))
    return fig, xx, zb, lines


def render():
    st.subheader('Channel experiment')
    st.caption('Drag the two brown endpoints to reshape the channel. Red dots indicate hydraulic boundary controls; quantitative solution below.')
    # Always-visible flow controls above the qualitative channel.
    c1, c2 = st.columns(2)
    with c1:
        q = st.slider('Discharge Q (m³/s)', 1.0, 35.0, 12.0, .5, key='m05_free_q')
    with c2:
        b = st.slider('Channel width b (m)', 2.0, 12.0, 5.0, .5, key='m05_free_b')
    # Keep both roughness controls visible above the flume alongside Q and b.
    # The sliders are instantiated before their values are used in the solver.
    rleft, rright = st.columns(2)
    with rleft:
        k1 = st.slider('Upstream bed roughness · Kₛ,₁ (m¹ᐟ³/s)',
                       25, 110, 70, key='m05_free_k1',
                       help='Lower Kₛ = rougher bed = larger stones.')
    with rright:
        k2 = st.slider('Downstream bed roughness · Kₛ,₂ (m¹ᐟ³/s)',
                       25, 110, 70, key='m05_free_k2',
                       help='Lower Kₛ = rougher bed = larger stones.')

    L1 = L2 = 300  # Fixed reach lengths (m)

    yc = ex.yc_of(q, b)
    sc1 = float(ex.sf(yc, q, b, k1))
    sc2 = float(ex.sf(yc, q, b, k2))
    # Store PHYSICAL bed slopes, not multiples of critical slopes.
    # Critical slopes depend on K_s; tying geometry to them made the bed move
    # whenever roughness was adjusted, even though the handles were untouched.
    if 'm05_free_slopes' not in st.session_state:
        st.session_state['m05_free_slopes'] = [0.4 * sc1, 2.2 * sc2]
    s1, s2 = [float(v) for v in st.session_state['m05_free_slopes']]
    # Absolute bed slopes are the only source of truth for geometry.
    ratios = [s1 / sc1, s2 / sc2]
    error = None
    d = None
    try:
        d = _build(q, b, k1, k2, s1, s2, L1, L2)
        fig, xx, zb, lines = _figure(d)
        line_data = [dict(x=x.tolist(), z=z.tolist()) for x, z in lines]
    except (ValueError, RuntimeError, OverflowError, ZeroDivisionError, FloatingPointError) as exc:
        error = str(exc)
        xx = np.linspace(-L1, L2, 240)
        zb = np.where(xx < 0, -s1*xx, -s2*xx)
        line_data = []

    # SVG is a real bidirectional Streamlit component. Its two handles are draggable.
    result = _COMPONENT(
        left=float(ratios[0]), right=float(ratios[1]),
        s1=float(s1), s2=float(s2),
        sc1=float(sc1), sc2=float(sc2), L1=L1, L2=L2,
        yc=float(yc), yn1=float(d['yn1']) if d else 0,
        yn2=float(d['yn2']) if d else 0,
        lines=line_data, mode=d['mode'] if d else '',
        k1=float(k1), k2=float(k2),
        controls=[{'x': x, 'depth': depth} for x, depth in d['controls']] if d else [],
        key='m05_free_dragger_stable_v4', default=None,
        height=540,
    )
    if (isinstance(result, dict) and 's1' in result and 's2' in result
            and result.get('revision') != st.session_state.get('m05_last_drag_revision')):
        st.session_state['m05_last_drag_revision'] = result.get('revision')
        # The browser returns PHYSICAL slopes at the instant of the drag.
        # Never reinterpret an old ratio using newly changed roughness/critical slope.
        if 's1' not in result or 's2' not in result:
            new_slopes = [s1, s2]  # Ignore cached events from the old component.
        else:
            new_slopes = [float(result['s1']), float(result['s2'])]
        if any(abs(new_slopes[i] - [s1, s2][i]) > 1e-9 for i in (0, 1)):
            st.session_state['m05_free_slopes'] = new_slopes
            st.rerun()

    c1, c2, c3 = st.columns([1, 1, 1])
    c1.metric('Upstream slope', f'{s1:.5f}')
    c2.metric('Downstream slope', f'{s2:.5f}')
    if d and 'jump' in d:
        c3.metric('Jump location', f"{d['jump']['xj']:.1f} m")
    else:
        c3.metric('Critical depth', f'{yc:.3f} m')

    if error:
        st.info('The current geometry does not yield a complete admissible profile within the displayed reaches. '
                'Try dragging an endpoint or changing the flow parameters.')
    else:
        st.plotly_chart(fig, use_container_width=True)

    if st.button('Reset channel', key='m05_free_reset'):
        st.session_state['m05_free_slopes'] = [0.4 * sc1, 2.2 * sc2]
        st.rerun()
