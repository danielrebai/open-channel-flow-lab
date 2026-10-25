"""Interactive rectangular-channel specific-force laboratory."""
import math
import streamlit as st
import plotly.graph_objects as go

G = 9.81


def _m(h,q):
    return h*h/2 + q*q/(G*h)


def _alternate(q, target, hc, branch):
    if branch == "supercritical":
        lo, hi = 1e-8, hc
        for _ in range(100):
            mid = (lo+hi)/2
            if _m(mid,q)>target: lo=mid
            else: hi=mid
    else:
        lo, hi = hc, max(2*math.sqrt(2*target),2*hc)
        for _ in range(100):
            mid = (lo+hi)/2
            if _m(mid,q)<target: lo=mid
            else: hi=mid
    return (lo+hi)/2


def render():
    st.header("Toy · Specific Force")
    st.markdown("Explore the **momentum function** in a rectangular channel. The two diagrams have independent inputs, just as in the Specific Energy Toy. Assume β = 1.")
    left,right=st.columns(2)
    with left:
        st.subheader("Σ(h) at fixed q")
        B=st.slider("Channel width B [m]",2.0,12.0,4.0,0.5,key="sf_toy_b")
        q=st.slider("Specific discharge q [m²/s]",0.4,8.0,2.0,0.1,key="sf_toy_q")
        h=st.slider("Selected depth h [m]",0.15,5.0,1.2,0.05,key="sf_toy_h")
        hc=(q*q/G)**(1/3)
        mc=1.5*hc*hc
        current=_m(h,q)
        other=_alternate(q,current,hc,"subcritical" if h<hc else "supercritical") if abs(h-hc)>1e-7 else hc
        maxh=max(5.0,2.1*hc,h*1.25,other*1.25)
        hs=[0.04+(maxh-0.04)*i/600 for i in range(601)]
        fig=go.Figure()
        fig.add_scatter(x=hs,y=[B*_m(v,q) for v in hs],name="Specific force Σ",line=dict(color="#2563eb",width=3))
        fig.add_scatter(x=hs,y=[B*v*v/2 for v in hs],name="Static contribution",line=dict(dash="dash",color="#94a3b8"))
        fig.add_scatter(x=[hc],y=[B*mc],mode="markers",name="Critical minimum",marker=dict(color="#dc2626",size=12))
        fig.add_scatter(x=[h,other],y=[B*current,B*current],mode="markers",name="Conjugate depths",marker=dict(color="#16a34a",size=10))
        fig.add_hline(y=B*current,line_dash="dot",line_color="#64748b")
        fig.update_layout(xaxis_title="Depth h [m]",yaxis_title="Σ [m³]",height=460,yaxis=dict(range=[0,max(B*current*1.6,B*mc*3)]),legend=dict(orientation="h",y=-0.3))
        st.plotly_chart(fig,use_container_width=True,key="sf_toy_curve")
        st.metric("Critical depth h_c",f"{hc:.3f} m")
        st.metric("Specific force Σ",f"{B*current:.3f} m³")
        st.write(f"**Regime:** {'supercritical' if h<hc else 'subcritical' if h>hc else 'critical'} · **Conjugate depth:** {other:.3f} m")
    with right:
        st.subheader("h(q) at fixed Σ")
        B2=st.slider("Channel width B [m] · second graph",2.0,12.0,4.0,0.5,key="sf_toy_b2")
        S=st.slider("Specific force Σ [m³]",1.0,40.0,8.0,0.5,key="sf_toy_s")
        hstar=math.sqrt(2*S/B2)
        hcrit=hstar/math.sqrt(3)
        qmax=math.sqrt(G*hcrit**3)
        qchosen=st.slider("Selected q [m²/s]",0.0,float(qmax),float(qmax*0.65),key="sf_toy_q2")
        hs2=[hstar*i/600 for i in range(601)]
        qs2=[math.sqrt(max(0,(S-B2*v*v/2)*G*v/B2)) for v in hs2]
        fig2=go.Figure()
        fig2.add_scatter(x=qs2,y=hs2,name="Fixed Σ",line=dict(color="#2563eb",width=3))
        fig2.add_scatter(x=[qmax],y=[hcrit],mode="markers",name="Maximum q",marker=dict(color="#dc2626",size=12))
        fig2.add_vline(x=qchosen,line_dash="dash",line_color="#64748b")
        if qchosen>0 and qchosen<qmax:
            mval=S/B2
            depths=[_alternate(qchosen,mval,(qchosen*qchosen/G)**(1/3),branch) for branch in ("supercritical","subcritical")]
            fig2.add_scatter(x=[qchosen,qchosen],y=depths,mode="markers",name="Two depths",marker=dict(color="#16a34a",size=10))
        fig2.update_layout(xaxis_title="q = Q/B [m²/s]",yaxis_title="Depth h [m]",height=460,legend=dict(orientation="h",y=-0.3))
        st.plotly_chart(fig2,use_container_width=True,key="sf_toy_discharge")
        st.metric("Maximum specific discharge",f"{qmax:.3f} m²/s")
        st.metric("Critical depth at fixed Σ",f"{hcrit:.3f} m")
        st.caption("The static endpoint at q = 0 occurs at h* = √(2Σ/B).")
