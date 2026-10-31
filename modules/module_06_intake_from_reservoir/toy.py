"""Module 06 — reservoir intake toy with two in-figure SVG drag handles."""
from pathlib import Path
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from . import exercise as ex
from .theory import _euler_supercritical

_COMPONENT = components.declare_component(
    'm06_reservoir_channel_dragger',
    path=str(Path(__file__).parent / 'channel_dragger'),
)


def _visual_data(H0, slope, ks, b, result):
    selected = result[result['winner'].lower()]
    L = 90.0
    x = np.linspace(0, L, 451)
    if result['winner'] == 'Steep':
        d = dict(Q=selected['Q'], yc=selected['k'], y0=selected['h0'],
                 slope=slope, b=b, ks=ks)
        xx, yy = _euler_supercritical(d, length=L, dx_max=.10)
        water_x, water_y = xx, yy
    else:
        water_x, water_y = x, np.full_like(x, selected['h0'])
    return dict(H0=H0, slope=slope, b=b, ks=ks, L=L,
                winner=result['winner'], Q=selected['Q'],
                h0=selected['h0'], k=selected['k'], Sc=selected['Sc'],
                water_x=np.asarray(water_x).tolist(),
                water_y=np.asarray(water_y).tolist())



def _scientific_figure(data):
    """Reservoir and numerical channel, matching the Theory/Exercise style."""
    L = data['L']
    slope = data['slope']
    H0 = data['H0']
    x = np.linspace(0.0, L, 451)
    zb = -slope*x
    fig = go.Figure()

    # Reservoir wall and curved transition, as in Theory.
    reservoir_x = -30.0
    wall_x = -3.5
    t = np.linspace(0.0, 1.0, 80)
    # Cubic Bezier between the raised reservoir bottom and intake datum.
    p0 = np.array([wall_x, -0.28])
    p1 = np.array([wall_x + 0.55, -0.06])
    p2 = np.array([-1.2, 0.0])
    p3 = np.array([0.0, 0.0])
    curve = ((1-t)**3)[:,None]*p0 + (3*(1-t)**2*t)[:,None]*p1 + (3*(1-t)*t*t)[:,None]*p2 + (t**3)[:,None]*p3
    bx = np.r_[reservoir_x, wall_x, wall_x, curve[:,0], x[1:]]
    by = np.r_[-2.2, -2.2, -0.28, curve[:,1], zb[1:]]
    fig.add_scatter(x=bx, y=by, mode='lines',
                    name='Reservoir wall and channel bed',
                    line=dict(color='#98602e', width=5))

    approach_start = -13.0
    fig.add_shape(type='rect', xref='x', yref='paper',
                  x0=approach_start, x1=0, y0=0, y1=1,
                  fillcolor='rgba(8,126,194,0.13)',
                  line=dict(width=0), layer='below')
    fig.add_scatter(x=[reservoir_x, approach_start], y=[H0, H0],
                    name='Reservoir water level',
                    line=dict(color='#087ec2', width=4))
    intake_depth = data['k'] if data['winner'] == 'Steep' else data['h0']
    xa = np.linspace(approach_start, 0, 120)
    u = (xa-approach_start)/(-approach_start)
    ya = H0+(intake_depth-H0)*(3*u*u-2*u*u*u)
    fig.add_scatter(x=xa, y=ya, name='Intake approach (qualitative)',
                    line=dict(color='#087ec2', width=3, dash='dash'))

    fig.add_scatter(x=x, y=zb+data['k'], name='Critical depth k',
                    line=dict(color='#d62828', width=2, dash='dash'))
    fig.add_scatter(x=x, y=zb+data['h0'], name='Uniform depth h₀',
                    line=dict(color='#228b50', width=5, dash='dash'))
    xx = np.asarray(data['water_x'], dtype=float)
    yy = np.asarray(data['water_y'], dtype=float)
    fig.add_scatter(x=xx, y=-slope*xx+yy, name='Computed water surface',
                    line=dict(color='#087ec2', width=4))
    if data['winner'] == 'Steep':
        fig.add_scatter(x=[0], y=[data['k']], mode='markers',
                        name='Critical intake control',
                        marker=dict(color='#d62828', size=14,
                                    symbol='circle-open', line=dict(width=3)))
    else:
        fig.add_scatter(x=[L], y=[-slope*L+data['h0']], mode='markers',
                        name='Downstream uniform control',
                        marker=dict(color='#228b50', size=14,
                                    symbol='circle-open', line=dict(width=3)))

    # H₀ is referenced to the channel bed at x=0.
    head_x = -24.0
    fig.add_scatter(x=[head_x, head_x], y=[0, H0], mode='lines',
                    showlegend=False, hoverinfo='skip',
                    line=dict(color='#344054', width=2))
    for end, start in ((H0, 0), (0, H0)):
        fig.add_annotation(x=head_x, y=end, ax=head_x, ay=start,
                           xref='x', yref='y', axref='x', ayref='y',
                           text='', showarrow=True, arrowhead=2,
                           arrowsize=1.2, arrowwidth=2, arrowcolor='#344054')
    fig.add_annotation(x=head_x+1.2, y=H0/2,
                       text=f'H₀ = {H0:.2f} m', showarrow=False,
                       xanchor='left', bgcolor='rgba(255,255,255,.8)',
                       font=dict(size=13, color='#344054'))
    fig.add_annotation(x=-20, y=H0+.23, text='Reservoir: V ≈ 0',
                       showarrow=False)
    fig.add_annotation(x=(approach_start + 0.0)/2, y=0.91,
                       xref='x', yref='paper', text='Qualitative!',
                       showarrow=False, xanchor='center',
                       font=dict(color='#087ec2', size=11))
    fig.add_annotation(x=45, y=-slope*45-.65,
                       text=f'{data["winner"].upper()} SLOPE',
                       showarrow=False, font=dict(color='#875022', size=13))
    fig.update_layout(
        template='plotly_white', height=460,
        margin=dict(l=25, r=25, t=60, b=85),
        xaxis_title='Longitudinal coordinate x (m)',
        yaxis_title='Elevation (m)',
        legend=dict(orientation='h', y=-.27),
        hovermode='x unified',
    )
    fig.update_xaxes(range=[-31, L+3])
    fig.update_yaxes(range=[min(-2.5, -slope*L-1.1), H0+.8])
    return fig

def render():
    st.subheader('Channel experiment — Intake from Reservoir')
    st.caption('Drag H₀ and the channel slope directly in the diagram. The hydraulic profile updates automatically.')
    left, right = st.columns(2)
    with left:
        b = st.slider('Channel width B (m)', 2.0, 12.0, 4.0, .5, key='m06_toy_b')
    with right:
        ks = st.slider('Strickler coefficient Kₛ (m¹ᐟ³/s)', 25, 110, 65, 1, key='m06_toy_ks')

    if 'm06_toy_head' not in st.session_state:
        st.session_state['m06_toy_head'] = 2.4
    if 'm06_toy_slope' not in st.session_state:
        st.session_state['m06_toy_slope'] = 0.0015
    H0 = float(st.session_state['m06_toy_head'])
    slope = float(st.session_state['m06_toy_slope'])
    error = None
    data = None
    result = None
    try:
        result = ex.solve_hypotheses(H0, slope, ks, b)
        data = _visual_data(H0, slope, ks, b, result)
    except (ValueError, RuntimeError, OverflowError, ZeroDivisionError, FloatingPointError) as exc:
        error = str(exc)

    payload = _COMPONENT(
        H0=H0, slope=slope, ks=float(ks), b=float(b),
        solution=data, error=error or '',
        key='m06_reservoir_dragger_v1', default=None, height=560,
    )
    if isinstance(payload, dict) and 'H0' in payload and 'slope' in payload:
        revision = payload.get('revision')
        if revision != st.session_state.get('m06_toy_drag_revision'):
            st.session_state['m06_toy_drag_revision'] = revision
            new_head = max(.65, min(5.0, float(payload['H0'])))
            new_slope = max(.00005, min(.04, float(payload['slope'])))
            if abs(new_head-H0) > 1e-6 or abs(new_slope-slope) > 1e-8:
                st.session_state['m06_toy_head'] = new_head
                st.session_state['m06_toy_slope'] = new_slope
                st.rerun()

    if error:
        st.warning('Unable to resolve exactly one consistent hydraulic regime for these settings. Adjust a handle slightly.')
        st.caption(error)
    else:
        chosen = result[result['winner'].lower()]
        st.markdown(f'**Flow regime: {result["winner"].upper()}**')
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Discharge Q', f'{chosen["Q"]:.3f} m³/s')
        c2.metric('Normal depth h₀', f'{chosen["h0"]:.3f} m')
        c3.metric('Critical depth k', f'{chosen["k"]:.3f} m')
        c4.metric('Intake depth h(0)', f'{chosen["k"] if result["winner"] == "Steep" else chosen["h0"]:.3f} m')
        st.subheader('Longitudinal hydraulic profile')
        st.plotly_chart(
            _scientific_figure(data), use_container_width=True,
            key='m06_toy_scientific_profile',
        )
    if st.button('Reset channel', key='m06_toy_reset'):
        st.session_state['m06_toy_head'] = 2.4
        st.session_state['m06_toy_slope'] = 0.0015
        st.rerun()
