"""Module 07 — interactive outflow toy, with draggable slope and tailwater."""
from pathlib import Path
import math
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from . import exercise as ex

_COMPONENT = components.declare_component(
    'm07_outflow_channel_dragger', path=str(Path(__file__).parent / 'channel_dragger'))


def _solve_for_toy(d):
    """Extend exercise solver to display downstream-controlled S1 for high tailwater."""
    r = ex._solve(d)
    if r['kind'] != 'steep_upstream':
        return r
    xx, hh, _ = ex._euler(ex.L, 0, d['Hd'], d)
    full = len(xx) > 1 and xx[-1] <= 1e-5
    return dict(kind='steep_s1_full' if full else 'steep_unresolved',
                name='S1 — jump upstream of displayed reach' if full else 'Partial S1',
                bc='Downstream: h(L) = H_D; upstream normal supercritical flow cannot be imposed simultaneously within this reach',
                segments=[(xx[::-1], hh[::-1], 'S1')], jump=None, h2=r.get('h2'))


def _plot_for_toy(d):
    fig = ex._plot(d)
    if d['result']['kind'] in ('steep_s1_full', 'steep_unresolved'):
        fig.data = tuple(tr for tr in fig.data if not (
            tr.mode == 'markers' and tr.showlegend is False and
            tr.marker is not None and tr.marker.symbol == 'circle-open'))
        fig.layout.annotations = tuple(a for a in fig.layout.annotations
                                       if a.text != 'Upstream BC')
        outlet = -d['S0'] * ex.L
        fig.add_trace(go.Scatter(x=[ex.L], y=[outlet + d['Hd']],
                                 mode='markers', showlegend=False,
                                 marker=dict(symbol='circle-open', size=17,
                                             color='#dc2626', line=dict(width=3))))
        fig.add_annotation(x=ex.L, y=outlet+d['Hd'], text='Downstream BC',
                           showarrow=True, ax=-85, ay=-55, arrowhead=2,
                           arrowcolor='#344054',
                           font=dict(size=12, color='#344054'),
                           bgcolor='rgba(255,255,255,0.9)')
    return fig

def render():
    st.subheader('Channel experiment — Outflow into a Reservoir')
    st.caption('Drag H_D and S₀ in the diagram; the numerical water-surface profile updates after each drag.')
    a, b, c = st.columns(3)
    with a:
        q = st.slider('Discharge Q (m³/s)', 2.0, 30.0, 12.0, 0.5, key='m07_toy_q')
    with b:
        width = st.slider('Channel width B (m)', 2.0, 12.0, 5.0, 0.5, key='m07_toy_b')
    with c:
        ks = st.slider('Strickler Kₛ (m¹ᐟ³/s)', 25, 110, 65, 1, key='m07_toy_ks')
    st.session_state.setdefault('m07_toy_slope', 0.002)
    st.session_state.setdefault('m07_toy_hd', 1.6)
    slope = float(st.session_state['m07_toy_slope'])
    hd = float(st.session_state['m07_toy_hd'])
    hc = (q*q/(ex.G*width*width))**(1/3)
    h0 = ex._normal_depth(q, width, ks, slope)
    ac = width*hc
    rc = ac/(width+2*hc)
    sc = (q/(ks*ac*rc**(2/3)))**2
    d = dict(Q=q, B=width, Ks=ks, S0=slope, Hd=hd, hc=hc, h0=h0, Sc=sc)
    result = _solve_for_toy(d)
    d['result'] = result
    payload = dict(Hd=hd, slope=slope, hc=hc, h0=h0, result=result['kind'],
                   segments=[dict(x=xx.tolist(), h=hh.tolist(), label=label)
                             for xx, hh, label in result['segments']],
                   jump=list(result['jump']) if result['jump'] else None,
                   name=result['name'], ks=ks, length=ex.L)
    update = _COMPONENT(data=payload, key='m07_outflow_dragger_v1',
                        default=None, height=555)
    if isinstance(update, dict) and 'Hd' in update and 'slope' in update:
        rev = update.get('revision')
        if rev != st.session_state.get('m07_toy_revision'):
            st.session_state['m07_toy_revision'] = rev
            new_hd = max(0.15, min(5.0, float(update['Hd'])))
            new_slope = max(0.00005, min(0.04, float(update['slope'])))
            if math.isfinite(new_hd) and math.isfinite(new_slope) and (
                    abs(new_hd-hd)>1e-6 or abs(new_slope-slope)>1e-9):
                st.session_state['m07_toy_hd'] = new_hd
                st.session_state['m07_toy_slope'] = new_slope
                st.rerun()
    a, b, c, e = st.columns(4)
    a.metric('Critical depth h_c', f'{hc:.3f} m')
    b.metric('Normal depth h₀', f'{h0:.3f} m')
    c.metric('Critical slope S_c', f'{sc:.5f}')
    e.metric('Slope class', 'MILD' if h0 > hc else 'STEEP')
    st.markdown(f'**Boundary condition:** {result["bc"]}  \n**Profile:** {result["name"]}')
    if result['jump']:
        st.caption(f'Hydraulic jump at x = {result["jump"][0]:.2f} m (momentum matching).')
    elif result['kind'] == 'steep_s1_full':
        st.info('S1 occupies the entire displayed reach. The jump is upstream of the '
                '100 m window; the upstream supercritical uniform-flow condition '
                'cannot simultaneously be imposed at x = 0.')
    elif result['kind'] == 'steep_unresolved':
        st.warning('Only part of the downstream-controlled S1 could be integrated. '
                   'The upstream transition needs a more detailed model.')
    st.subheader('Computed longitudinal hydraulic profile')
    st.plotly_chart(_plot_for_toy(d), use_container_width=True, key='m07_toy_plot')
    st.caption('The channel profile uses adaptive-step explicit Euler GVF integration. '
               'The hydraulic jump is located by conjugate-depth matching; '
               'the local outflow region in the reservoir is not resolved.')
    if st.button('Reset channel', key='m07_toy_reset'):
        st.session_state['m07_toy_slope'] = 0.002
        st.session_state['m07_toy_hd'] = 1.6
        st.rerun()
