"""Randomized, fully worked specific-force exercises for rectangular channels."""
import math
import random
import streamlit as st
import plotly.graph_objects as go

G=9.81


def m(h,q):
    return h*h/2+q*q/(G*h)


def hc(q):
    return (q*q/G)**(1/3)


def roots(q,target):
    c=hc(q)
    if target<=1.5*c*c:
        raise ValueError("No two distinct conjugate depths at or below the critical minimum.")
    a,b=1e-10,c
    for _ in range(110):
        mid=(a+b)/2
        if m(mid,q)>target: a=mid
        else: b=mid
    small=(a+b)/2
    a,b=c,max(2*math.sqrt(2*target),2*c)
    for _ in range(110):
        mid=(a+b)/2
        if m(mid,q)<target: a=mid
        else: b=mid
    return small,(a+b)/2


def make_case(kind):
    r=random.SystemRandom()
    B=round(r.uniform(3,9),1)
    Q=round(r.uniform(5,20),1)
    q=Q/B
    c=hc(q)
    if kind==1:
        h1=round(c*r.uniform(0.38,0.73),3)
        return dict(kind=kind,B=B,Q=Q,h=h1)
    if kind==2:
        h=round(c*r.choice([r.uniform(0.40,0.72),r.uniform(1.5,2.6)]),3)
        return dict(kind=kind,B=B,Q=Q,h=h)
    if kind==3:
        S=round(B*1.5*c*c*r.uniform(1.5,2.5),3)
        return dict(kind=kind,B=B,Q=Q,S=S)
    q2=round(q*r.uniform(0.6,1.25),3)
    S=round(B*1.5*max(c,hc(q2))**2*r.uniform(1.7,2.4),3)
    return dict(kind=kind,B=B,Q=Q,q2=q2,S=S,branch=r.choice(["subcritical","supercritical"]))


def _plot(B,q,depths,target,extra_q=None,final_depth=None):
    c=hc(q)
    xmax=max(3.5*c,*(v*1.3 for v in depths))
    hs=[0.035+xmax*i/650 for i in range(1,651)]
    fig=go.Figure()
    for qq,name,color,dash in [(q,"Initial discharge","#2563eb","solid")]+ ([(extra_q,"Changed discharge","#16a34a","dash")] if extra_q is not None else []):
        fig.add_scatter(x=hs,y=[B*m(h,qq) for h in hs],name=name,line=dict(color=color,width=3,dash=dash))
        cc=hc(qq)
        fig.add_scatter(x=[cc],y=[B*1.5*cc*cc],mode="markers",name="Critical state",marker=dict(color="#dc2626",size=10),showlegend=qq==q)
    fig.add_hline(y=target,line_dash="dot",line_color="#64748b")
    fig.add_scatter(x=depths,y=[target]*len(depths),mode="markers",name="Initial / conjugate depth(s)",marker=dict(color="#f59e0b",size=11))
    if final_depth is not None:
        fig.add_scatter(x=[final_depth],y=[target],mode="markers",name="Final depth (changed q)",marker=dict(color="#16a34a",size=13,symbol="diamond"))
    fig.update_layout(title="Specific-force curves and conjugate depths",xaxis_title="h [m]",yaxis_title="Σ [m³]",height=470,yaxis=dict(range=[0,target*2.3]),legend=dict(orientation="h",y=-0.3))
    st.plotly_chart(fig,use_container_width=True)


def _plot_q(B,S,selected_q=None):
    hstar=math.sqrt(2*S/B)
    hcrit=hstar/math.sqrt(3)
    qmax=math.sqrt(G*hcrit**3)
    hs=[hstar*i/550 for i in range(551)]
    qs=[math.sqrt(max(0,G*h/B*(S-B*h*h/2))) for h in hs]
    fig=go.Figure()
    fig.add_scatter(x=qs,y=hs,name="Constant Σ",line=dict(color="#2563eb",width=3))
    fig.add_scatter(x=[qmax],y=[hcrit],mode="markers",name="Maximum discharge",marker=dict(color="#dc2626",size=12))
    if selected_q is not None:
        fig.add_vline(x=selected_q,line_dash="dash",line_color="#64748b")
    fig.update_layout(title="Depth vs specific discharge at fixed Σ",xaxis_title="q = Q/B [m²/s]",yaxis_title="h [m]",height=470,legend=dict(orientation="h",y=-0.25))
    st.plotly_chart(fig,use_container_width=True)


def render():
    st.header("Exercise · Specific Force")
    st.caption("Randomized data · Complete worked solutions · Rectangular channel · β = 1")
    options={"Type 1 — Hydraulic-jump conjugate depth":1,"Type 2 — Regime and alternate depth":2,"Type 3 — Maximum discharge at fixed Σ":3,"Type 4 — Change q at fixed Σ":4}
    choice=st.radio("Choose exercise type",list(options),horizontal=True,key="sf_exercise_type")
    kind=options[choice]
    if "sf_case" not in st.session_state or st.session_state.sf_case["kind"]!=kind:
        st.session_state.sf_case=make_case(kind)
        st.session_state.sf_number=1
    if st.button("Generate another exercise",type="primary",key="sf_new"):
        st.session_state.sf_case=make_case(kind)
        st.session_state.sf_number+=1
    case=st.session_state.sf_case
    B,Q=case["B"],case["Q"]
    q=Q/B
    c=hc(q)
    st.caption(f"Exercise {st.session_state.sf_number} · Type {kind}")
    st.subheader("Problem statement")
    st.markdown("Consider steady flow in a **horizontal rectangular channel**, with hydrostatic pressure at both sections and momentum correction coefficient β = 1. Neglect external horizontal forces between the compared sections unless otherwise specified.")
    st.latex(rf"B={B:.1f}\ \mathrm{{m}},\qquad Q={Q:.1f}\ \mathrm{{m^3/s}},\qquad q=Q/B={q:.4f}\ \mathrm{{m^2/s}}")
    if kind in (1,2):
        h=case["h"]
        st.latex(rf"h_1={h:.3f}\ \mathrm{{m}}")
        st.markdown("**Required:** " + ("Find the downstream conjugate depth for a hydraulic jump and verify momentum conservation." if kind==1 else "Classify the flow regime and determine the alternate depth with equal specific force."))
    elif kind==3:
        st.latex(rf"\overline{{\Sigma}}={case['S']:.3f}\ \mathrm{{m^3}}")
        st.markdown("**Required:** Find the maximum discharge possible at the prescribed specific force and the corresponding critical depth. Compare with the given Q.")
    else:
        st.latex(rf"\overline{{\Sigma}}={case['S']:.3f}\ \mathrm{{m^3}},\qquad q_2={case['q2']:.3f}\ \mathrm{{m^2/s}}")
        st.markdown(f"**Required:** Find the new depth after changing the specific discharge from q₁ to q₂ at constant Σ, staying on the **{case['branch']}** branch.")
    st.divider()
    st.subheader("Complete worked solution")
    st.markdown("### 1. Governing momentum function and critical condition")
    st.latex(r"\Sigma=\frac{Bh^2}{2}+\frac{Q^2}{gBh}=B\left(\frac{h^2}{2}+\frac{q^2}{gh}\right)")
    st.latex(rf"h_c=\left(\frac{{q^2}}{{g}}\right)^{{1/3}}={c:.5f}\ \mathrm{{m}},\quad \Sigma_c=\frac32 Bh_c^2={1.5*B*c*c:.5f}\ \mathrm{{m^3}}")
    if kind in (1,2):
        h=case["h"]
        target=B*m(h,q)
        lo,hi=roots(q,target/B)
        other=hi if h<c else lo
        Fr=q/math.sqrt(G*h**3)
        st.markdown("### 2. Compute specific force and classify the regime")
        st.latex(rf"\Sigma_1=B\left(\frac{{h_1^2}}2+\frac{{q^2}}{{gh_1}}\right)={target:.5f}\ \mathrm{{m^3}}")
        st.latex(rf"Fr_1=\frac{{q}}{{\sqrt{{gh_1^3}}}}={Fr:.4f}")
        st.markdown(f"The initial flow is **{'supercritical' if Fr>1 else 'subcritical'}**.")
        st.markdown("### 3. Conjugate depth — algebraic derivation")
        st.latex(r"\frac{h_1^2}{2}+\frac{q^2}{gh_1}=\frac{h_2^2}{2}+\frac{q^2}{gh_2}")
        st.latex(r"\frac{h_2}{h_1}=\frac{\sqrt{1+8Fr_1^2}-1}{2}\quad\text{(the nontrivial conjugate root)}")
        ratio=(math.sqrt(1+8*Fr*Fr)-1)/2
        st.latex(rf"h_2=h_1\frac{{\sqrt{{1+8Fr_1^2}}-1}}2={h*ratio:.5f}\ \mathrm{{m}}")
        st.markdown("### 4. Numerical verification")
        st.latex(rf"\Sigma(h_2,Q)={B*m(other,q):.5f}\ \mathrm{{m^3}}\approx\Sigma_1")
        st.latex(rf"\boxed{{h_{{\mathrm{{alternate}}}}={other:.5f}\ \mathrm{{m}}}}")
        if kind==1:
            st.markdown("For a hydraulic jump, the upstream state must be supercritical and the downstream state subcritical. The generated initial state satisfies this requirement.")
        st.markdown("### 5. Graphical interpretation")
        _plot(B,q,[lo,hi],target)
        _plot_q(B,target,q)
    elif kind==3:
        S=case["S"]
        hstar=math.sqrt(2*S/B)
        cstar=hstar/math.sqrt(3)
        qmax=math.sqrt(G*cstar**3)
        Qmax=B*qmax
        st.markdown("### 2. Static limit and critical condition")
        st.latex(r"\overline\Sigma=\frac{Bh^2}{2}+\frac{Q^2}{gBh},\qquad Q^2=gBh\left(\overline\Sigma-\frac{Bh^2}{2}\right)")
        st.latex(r"\frac{dQ^2}{dh}=gB\left(\overline\Sigma-\frac{3Bh^2}{2}\right)=0")
        st.latex(rf"h_*=\sqrt{{\frac{{2\overline\Sigma}}{{B}}}}={hstar:.5f}\ \mathrm{{m}},\quad h_c=\sqrt{{\frac{{2\overline\Sigma}}{{3B}}}}={cstar:.5f}\ \mathrm{{m}}")
        st.markdown("### 3. Maximum discharge")
        st.latex(rf"q_{{\max}}=\sqrt{{gh_c^3}}={qmax:.5f}\ \mathrm{{m^2/s}},\qquad\boxed{{Q_{{\max}}=Bq_{{\max}}={Qmax:.5f}\ \mathrm{{m^3/s}}}}")
        st.markdown(f"The given discharge Q = {Q:.2f} m³/s is **{'admissible' if Q<Qmax else 'not admissible'}** at this specific force.")
        st.markdown("### 4. Graphical interpretation")
        _plot_q(B,S,q)
    else:
        S=case["S"]
        q2=case["q2"]
        branch=case["branch"]
        r1=roots(q,S/B)
        r2=roots(q2,S/B)
        index=1 if branch=="subcritical" else 0
        h1,h2=r1[index],r2[index]
        st.markdown("### 2. Initial and final critical depths")
        st.latex(rf"h_{{c,1}}={hc(q):.5f}\ \mathrm{{m}},\quad h_{{c,2}}={hc(q2):.5f}\ \mathrm{{m}}")
        st.latex(rf"\Sigma_{{c,2}}=\frac32 B h_{{c,2}}^2={1.5*B*hc(q2)**2:.5f}\ \mathrm{{m^3}}<\overline\Sigma={S:.5f}\ \mathrm{{m^3}}")
        st.markdown("### 3. Solve the momentum equation on the selected branch")
        st.latex(r"\frac{h^2}{2}+\frac{q^2}{gh}=\frac{\overline\Sigma}{B}")
        st.latex(r"h^3-\frac{2\overline\Sigma}{B}h+\frac{2q^2}{g}=0")
        st.markdown("Use bisection on the chosen side of the critical depth. The two positive roots correspond to supercritical and subcritical states.")
        st.latex(rf"h_1={h1:.5f}\ \mathrm{{m}},\qquad\boxed{{h_2={h2:.5f}\ \mathrm{{m}}}}")
        st.markdown("### 4. Verification")
        st.latex(rf"\Sigma(h_1,q_1)={B*m(h1,q):.5f}\ \mathrm{{m^3}},\qquad\Sigma(h_2,q_2)={B*m(h2,q2):.5f}\ \mathrm{{m^3}}")
        st.markdown("### 5. Graphical interpretation")
        _plot(B,q,[h1],S,extra_q=q2,final_depth=h2)
        _plot_q(B,S,q2)
