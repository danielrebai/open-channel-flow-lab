"""Specific-force lecture with contextual Plotly graphs."""
from pathlib import Path
import math
import streamlit as st
import plotly.graph_objects as go

G = 9.81


def _sigma(h, Q, B):
    return B*h*h/2 + Q*Q/(G*B*h)


def _graph_sigma_h():
    B, q = 4.0, 2.0
    Q = B*q
    hc = (q*q/G)**(1/3)
    hs = [0.07 + 0.007*i for i in range(500)]
    fig = go.Figure()
    fig.add_scatter(x=hs, y=[_sigma(h,Q,B) for h in hs], name="Σ(h), fixed Q", line=dict(color="#2563eb",width=3))
    fig.add_scatter(x=hs, y=[B*h*h/2 for h in hs], name="Hydrostatic contribution", line=dict(dash="dash",color="#64748b"))
    fig.add_scatter(x=[hc],y=[1.5*B*hc*hc],mode="markers",name="Critical minimum",marker=dict(size=12,color="#dc2626"))
    fig.update_layout(title="Specific force versus depth — fixed discharge",xaxis_title="Depth h [m]",yaxis_title="Specific force Σ [m³]",height=460,yaxis=dict(range=[0,45]),legend=dict(orientation="h",y=-0.3))
    st.plotly_chart(fig,use_container_width=True)
    st.caption("Illustration: rectangular channel, B = 4 m, q = 2 m²/s, β = 1.")


def _graph_h_q():
    B, sigma_bar = 4.0, 8.0
    h_star = math.sqrt(2*sigma_bar/B)
    hs = [h_star*i/500 for i in range(501)]
    qs = [math.sqrt(max(0, (sigma_bar-B*h*h/2)*G*h/B)) for h in hs]
    hc = math.sqrt(2*sigma_bar/(3*B))
    qc = math.sqrt(G*hc**3)
    fig = go.Figure()
    fig.add_scatter(x=qs,y=hs,name="h(q), fixed Σ",line=dict(color="#2563eb",width=3))
    fig.add_scatter(x=[qc],y=[hc],mode="markers",name="Maximum discharge",marker=dict(size=12,color="#dc2626"))
    fig.update_layout(title="Depth versus specific discharge — fixed specific force",xaxis_title="q = Q/B [m²/s]",yaxis_title="Depth h [m]",height=460,legend=dict(orientation="h",y=-0.25))
    st.plotly_chart(fig,use_container_width=True)
    st.caption("Illustration: rectangular channel, B = 4 m, Σ = 8 m³, β = 1.")


def render():
    st.header("Theory · Specific Force")
    text = Path(__file__).with_name("theory.md").read_text(encoding="utf-8")
    parts = text.split("<!-- GRAPH:SIGMA_H -->")
    st.markdown(parts[0])
    if len(parts) > 1:
        _graph_sigma_h()
        tail = parts[1].split("<!-- GRAPH:H_Q -->")
        st.markdown(tail[0])
        if len(tail) > 1:
            _graph_h_q()
            st.markdown(tail[1])
