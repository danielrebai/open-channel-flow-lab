"""Module 02 lecture notes with graphs inserted at the relevant derivations."""
from pathlib import Path
import math

import plotly.graph_objects as go
import streamlit as st

G = 9.81


def _energy_graph():
    st.markdown('#### Specific energy versus depth at constant specific discharge')
    q = 2.0  # m²/s; illustrative rectangular channel, alpha = 1
    hc = (q*q/G)**(1/3)
    emin = 1.5*hc
    depths = [0.12 + i*(3.0-0.12)/500 for i in range(501)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=depths, y=[h+q*q/(2*G*h*h) for h in depths],
                             mode='lines', name='E(h), q = 2.0 m²/s',
                             line=dict(color='#2563eb', width=3)))
    fig.add_trace(go.Scatter(x=[0, 3], y=[0, 3], mode='lines',
                             name='Hydrostatic term E = h',
                             line=dict(color='#64748b', dash='dash')))
    fig.add_trace(go.Scatter(x=[0, 3], y=[0, 4.5], mode='lines',
                             name='Critical locus E = 3h/2',
                             line=dict(color='#dc2626', dash='dot')))
    fig.add_trace(go.Scatter(x=[hc], y=[emin], mode='markers',
                             name=f'Critical state (h₍c₎ = {hc:.3f} m)',
                             marker=dict(color='#dc2626', size=12)))
    fig.update_layout(xaxis_title='Depth h [m]', yaxis_title='Specific energy E [m]',
                      xaxis=dict(range=[0, 3]), yaxis=dict(range=[0, 4.5]),
                      height=470, legend=dict(orientation='h', y=-0.27),
                      margin=dict(t=25, b=80))
    st.plotly_chart(fig, use_container_width=True, key='theory_eh')
    st.caption('Illustrative rectangular channel with α = 1 and q = Q/B = 2.0 m²/s. '
               'The curve has a minimum at the critical depth; E = h is its oblique asymptote.')


def _discharge_graph():
    st.markdown('#### Depth versus specific discharge at constant specific energy')
    E = 2.0  # m; illustrative rectangular channel, alpha = 1
    hc = 2*E/3
    qc = math.sqrt(G*hc**3)
    depths = [E*i/500 for i in range(501)]
    qs = [h*math.sqrt(max(0.0, 2*G*(E-h))) for h in depths]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qs, y=depths, mode='lines',
                             name='h(q), E = 2.0 m', line=dict(color='#2563eb', width=3)))
    locus_h = [2.2*i/400 for i in range(401)]
    fig.add_trace(go.Scatter(x=[math.sqrt(G*h**3) for h in locus_h], y=locus_h,
                             mode='lines', name='Critical locus q = √(gh³)',
                             line=dict(color='#dc2626', dash='dot')))
    fig.add_trace(go.Scatter(x=[qc], y=[hc], mode='markers',
                             name=f'Maximum q = {qc:.3f} m²/s',
                             marker=dict(color='#dc2626', size=12)))
    fig.update_layout(xaxis_title='Specific discharge q = Q/B [m²/s]',
                      yaxis_title='Depth h [m]',
                      xaxis=dict(range=[0, max(1.15*qc, 1.15*math.sqrt(G*2.2**3))]),
                      yaxis=dict(range=[0, 2.2]), height=470,
                      legend=dict(orientation='h', y=-0.27),
                      margin=dict(t=25, b=80))
    st.plotly_chart(fig, use_container_width=True, key='theory_hq')
    st.caption('Illustrative rectangular channel with α = 1 and E = 2.0 m. '
               'The maximum specific discharge occurs at critical flow.')


def render():
    st.header('Theory · Specific Energy')
    st.caption('Specific energy, critical flow, and maximum discharge')
    path = Path(__file__).with_name('theory.md')
    text = path.read_text(encoding='utf-8')
    first, sep, rest = text.partition('<!-- GRAPH_E_H -->')
    if not sep:
        st.markdown(text)
        return
    st.markdown(first)
    _energy_graph()
    middle, sep, last = rest.partition('<!-- GRAPH_H_Q -->')
    st.markdown(middle)
    if sep:
        _discharge_graph()
        st.markdown(last)
