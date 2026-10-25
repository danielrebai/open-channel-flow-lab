import numpy as np
import plotly.graph_objects as go
import streamlit as st
from ..hydraulics import G


def plot_energy():
    # Specific-energy diagram: E(h) at fixed discharge.
    hcrit_demo = (3.0**2/(G*3.0**2))**(1/3)
    hh = np.linspace(0.22*hcrit_demo, 3.2*hcrit_demo, 240)
    ee = hh + 3.0**2/(2*G*3.0**2*hh**2)
    emin = 1.5*hcrit_demo
    fig_energy = go.Figure()
    fig_energy.add_trace(go.Scatter(
        x=hh, y=ee, mode="lines", name="Specific energy E(h)",
        line=dict(color="#2563eb",width=3)))
    fig_energy.add_trace(go.Scatter(
        x=[hcrit_demo], y=[emin], mode="markers+text",
        text=["Critical depth k"], textposition="top right",
        marker=dict(size=11,color="#dc2626"), name="Minimum energy"))
    fig_energy.add_vline(x=hcrit_demo, line_dash="dot",line_color="#dc2626")
    fig_energy.update_layout(
        title="Specific energy at fixed discharge (illustrative)",
        xaxis_title="Water depth h [m]", yaxis_title="Specific energy E [m]",
        height=370, margin=dict(t=55,b=45,l=50,r=30))
    st.plotly_chart(fig_energy, use_container_width=True)
    st.caption(
        "The minimum of the specific-energy curve identifies the critical depth "
        "k, where dE/dh = 0 (handwritten notes, PDF p. 2)."
    )



def plot_signs():
    # Sign diagram: denominator and numerator for an illustrative mild channel.
    demo_Q, demo_b, demo_n, demo_S = 3.0, 3.0, 0.025, 0.002
    def theory_j(h, q=demo_Q, width=demo_b, rough=demo_n):
        a=width*h
        r=a/(width+2*h)
        return (rough*q/(a*r**(2/3)))**2
    lo_t, hi_t = 0.01, 10.0
    for _ in range(75):
        mid_t=(lo_t+hi_t)/2
        if theory_j(mid_t)>demo_S:
            lo_t=mid_t
        else:
            hi_t=mid_t
    demo_h0=(lo_t+hi_t)/2
    demo_k=(demo_Q**2/(G*demo_b**2))**(1/3)
    hsign=np.linspace(0.3*demo_k,2.0*demo_h0,350)
    numerator=[demo_S-theory_j(h) for h in hsign]
    denominator=[1-demo_Q**2/(G*demo_b**2*h**3) for h in hsign]
    from plotly.subplots import make_subplots
    fig_sign=make_subplots(rows=2,cols=1,shared_xaxes=True,
                           subplot_titles=("Numerator: i − j(h)","Denominator: 1 − Fr²"))
    fig_sign.add_trace(go.Scatter(x=hsign,y=numerator,mode="lines",
        line=dict(color="#0d9488",width=3),name="i − j"),row=1,col=1)
    fig_sign.add_trace(go.Scatter(x=hsign,y=denominator,mode="lines",
        line=dict(color="#7c3aed",width=3),name="1 − Fr²"),row=2,col=1)
    for r in (1,2):
        fig_sign.add_hline(y=0,line_color="#888888",line_width=1,row=r,col=1)
        fig_sign.add_vline(x=demo_k,line_dash="dot",line_color="#dc2626",row=r,col=1)
        fig_sign.add_vline(x=demo_h0,line_dash="dash",line_color="#16a34a",row=r,col=1)
    fig_sign.update_layout(height=460,showlegend=False,
        margin=dict(t=70,b=45,l=50,r=25))
    fig_sign.update_xaxes(title_text="Water depth h [m]",row=2,col=1)
    st.plotly_chart(fig_sign,use_container_width=True)
    st.caption(
        f"Illustrative mild channel: k = {demo_k:.3f} m (red dotted), "
        f"h₀ = {demo_h0:.3f} m (green dashed). "
        "The sign of dh/ds is the sign of the ratio of these two functions."
    )



def plot_profiles():
    st.markdown("### 5a. Six profile diagrams")
    st.markdown(
        "The six diagrams below recreate the **qualitative geometry** "
        "of the handwritten sketches for mild and steep channels. "
        "They are schematic, not the output of the numerical solver."
    )
    from plotly.subplots import make_subplots
    fig_profiles=make_subplots(rows=2,cols=3,
        subplot_titles=("M1 · Backwater","M2 · Drawdown","M3 · Supercritical",
                        "S1 · Backwater","S2 · Supercritical","S3 · Supercritical"),
        horizontal_spacing=0.055,vertical_spacing=0.17)
    xprof=np.linspace(0,1,160)
    # Depths are in schematic display units; green/red are h0/k above bed.
    sketches={
        "M1": (1.0,0.42, 1.10+0.65*xprof**2),
        "M2": (1.0,0.42, 0.97-0.50*xprof**2),
        "M3": (1.0,0.42, 0.16+0.23*np.sqrt(xprof)),
        "S1": (0.40,1.0, 1.07+0.50*xprof**2),
        "S2": (0.40,1.0, 0.95-0.47*xprof**2),
        "S3": (0.40,1.0, 0.12+0.25*(1-np.exp(-4*xprof))),
    }
    for ix,(kind,(normal,critical,depth)) in enumerate(sketches.items()):
        row=ix//3+1
        col=ix%3+1
        bed=-0.20*xprof
        fig_profiles.add_trace(go.Scatter(x=xprof,y=bed,mode="lines",
            line=dict(color="#64748b",width=3),name="Bed",
            showlegend=ix==0),row=row,col=col)
        fig_profiles.add_trace(go.Scatter(x=xprof,y=bed+normal,mode="lines",
            line=dict(color="#16a34a",dash="dash",width=2),name="Normal depth h₀",
            showlegend=ix==0),row=row,col=col)
        fig_profiles.add_trace(go.Scatter(x=xprof,y=bed+critical,mode="lines",
            line=dict(color="#dc2626",dash="dot",width=2),name="Critical depth k",
            showlegend=ix==0),row=row,col=col)
        fig_profiles.add_trace(go.Scatter(x=xprof,y=bed+depth,mode="lines",
            line=dict(color="#0284c7",width=3),name="Water surface",
            showlegend=ix==0),row=row,col=col)
        fig_profiles.update_xaxes(showticklabels=False,title_text="Downstream →",
                                  row=row,col=col)
        fig_profiles.update_yaxes(showticklabels=False,range=[-0.32,1.95],
                                  row=row,col=col)
    fig_profiles.update_layout(height=690,legend=dict(orientation="h",y=-0.08),
        margin=dict(t=70,b=85,l=20,r=20))
    st.plotly_chart(fig_profiles,use_container_width=True)
    st.caption(
        "Schematic reconstruction of the M1–M3 and S1–S3 sketches "
        "(handwritten notes, PDF pp. 3–6). "
        "Green dashed: h₀; red dotted: k; blue: water surface; gray: bed. "
        "Curves are illustrative and not to scale."
    )



def plot_waves():
    # Disturbance propagation: the flow velocity relative to wave celerity.
    fig_waves=go.Figure()
    for row_y,label,U,c in [(1.0,"Subcritical",0.6,1.0),
                            (0.0,"Supercritical",1.4,1.0)]:
        fig_waves.add_annotation(x=0.03,y=row_y+0.20,
            text=label,showarrow=False,xanchor="left",font=dict(size=15))
        fig_waves.add_trace(go.Scatter(x=[0.48],y=[row_y],
            mode="markers",marker=dict(size=12,color="#0284c7"),
            showlegend=False))
        for speed,color,name in [(U-c,"#dc2626","U − c"),(U+c,"#16a34a","U + c")]:
            direction=1 if speed>0 else -1
            fig_waves.add_annotation(x=0.48+0.20*direction,y=row_y,
                ax=0.48,ay=row_y,xref="x",yref="y",axref="x",ayref="y",
                text="",showarrow=True,arrowhead=3,arrowsize=1.5,
                arrowwidth=3,arrowcolor=color)
        fig_waves.add_annotation(x=0.88,y=row_y+0.14,
            text=f"U/c = {U/c:.1f}",showarrow=False)
    fig_waves.update_layout(title="Propagation of small disturbances",
        xaxis=dict(range=[0,1],visible=False),yaxis=dict(range=[-0.4,1.5],visible=False),
        height=290,showlegend=False,margin=dict(t=50,b=10,l=15,r=15))
    st.plotly_chart(fig_waves,use_container_width=True)
    st.caption(
        "Schematic characteristic directions: in subcritical flow "
        "U − c < 0 and U + c > 0; in supercritical flow both are positive. "
        "Adapted from the perturbation sketches (handwritten notes, PDF pp. 9–10)."
    )

def plot_specific_energy_denominator():
    """Specific energy curve showing the sign of dE/dh."""

    # Illustrative rectangular channel
    Q = 3.0       # m³/s
    b = 3.0       # m
    q = Q / b     # m²/s

    hc = (q**2 / G)**(1 / 3)
    Emin = 1.5 * hc

    def E(h):
        return h + q**2 / (2 * G * h**2)

    h_super = np.linspace(0.35 * hc, hc, 200)
    h_sub = np.linspace(hc, 3.0 * hc, 200)

    fig = go.Figure()

    # Supercritical branch: negative derivative
    fig.add_trace(go.Scatter(
        x=h_super,
        y=E(h_super),
        mode="lines",
        name="Supercritical: dE/dh < 0",
        line=dict(color="#dc2626", width=3)
    ))

    # Subcritical branch: positive derivative
    fig.add_trace(go.Scatter(
        x=h_sub,
        y=E(h_sub),
        mode="lines",
        name="Subcritical: dE/dh > 0",
        line=dict(color="#2563eb", width=3)
    ))

    # Critical point
    fig.add_trace(go.Scatter(
        x=[hc],
        y=[Emin],
        mode="markers",
        name="Critical: dE/dh = 0",
        marker=dict(color="#111827", size=11)
    ))

    fig.add_vline(
        x=hc,
        line_dash="dot",
        line_color="#64748b"
    )

    fig.add_annotation(
        x=hc,
        y=Emin,
        text="Critical depth",
        showarrow=True,
        arrowhead=2,
        ax=65,
        ay=-35
    )

    fig.update_layout(
        title="Specific energy: sign of the denominator",
        xaxis_title="Water depth h [m]",
        yaxis_title="Specific energy E [m]",
        height=440,
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0
        ),
        margin=dict(t=60, b=100, l=55, r=25)
    )

    st.plotly_chart(fig, width="stretch")