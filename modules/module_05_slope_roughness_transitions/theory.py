"""Module 05 Theory: manuscript text plus one Plotly schematic for each hydraulic case.

Figures use the full rectangular Gauckler–Strickler hydraulic radius and
integrate dy/dx=(S0-Sf)/(1-Fr²) away from singular/rapidly varied regions.
Hydraulic jumps are schematic (specific-force matching shown qualitatively).
"""
from pathlib import Path
import math
import re
import numpy as np
import plotly.graph_objects as go
import streamlit as st

G=9.81
Q=10.0
B=4.0
YC=(Q*Q/(G*B*B))**(1/3)

def area(y): return B*y
def radius(y): return B*y/(B+2*y)
def sf(y,ks): return (Q/(ks*area(y)*radius(y)**(2/3)))**2
def critical_slope(ks): return sf(YC,ks)
def normal_depth(s0,ks):
    lo,hi=1e-8,50.0
    for _ in range(85):
        m=(lo+hi)/2
        if sf(m,ks)>s0:lo=m
        else:hi=m
    return (lo+hi)/2

def ode(y,s0,ks):
    y=max(0.01,float(y))
    fr2=Q*Q/(G*B*B*y**3)
    den=1-fr2
    if abs(den)<0.03: return 0.0
    return (s0-sf(y,ks))/den

def profile(s0,ks,start,end,y_start,n=350):
    xx=np.linspace(start,end,n)
    yy=np.zeros(n);yy[0]=y_start
    for j in range(1,n):
        dx=xx[j]-xx[j-1];y=yy[j-1]
        k1=ode(y,s0,ks);k2=ode(y+dx*k1/2,s0,ks)
        k3=ode(y+dx*k2/2,s0,ks);k4=ode(y+dx*k3,s0,ks)
        yn=max(0.015,y+dx*(k1+2*k2+2*k3+k4)/6)
        yy[j]=min(8.0,yn)
    return xx,yy

def make_case(kind):
    ks1=ks2=75.0
    sc=critical_slope(75)
    if kind=='slope_mild_steep': s1,s2=sc*0.20,sc*3.0
    elif kind=='slope_mild_mild_decrease':s1,s2=sc*0.18,sc*0.45
    elif kind=='slope_mild_mild_increase':s1,s2=sc*0.45,sc*0.18
    elif kind=='slope_steep_steep_decrease':s1,s2=sc*3.5,sc*1.8
    elif kind=='slope_steep_steep_increase':s1,s2=sc*1.8,sc*3.5
    elif kind.startswith('rough_'):
        s1=s2=sc*(0.25 if 'mild' in kind else 3.0)
        if kind.endswith('decrease'):
            ks1,ks2=(55,95) # roughness decreases: Ks increases
        else:ks1,ks2=(95,55)
        # ensure both reaches are in desired regime with selected Ks
        if 'mild' in kind:s1=s2=min(critical_slope(ks1),critical_slope(ks2))*0.30
        else:s1=s2=max(critical_slope(ks1),critical_slope(ks2))*2.2
    else: s1,s2=sc*3.0,sc*0.2
    return s1,s2,ks1,ks2

def figure(kind,variant=0):
    s1,s2,ks1,ks2=make_case(kind)
    y01=normal_depth(s1,ks1);y02=normal_depth(s2,ks2)
    x=np.linspace(-100,100,600)
    # Keep bed levels continuous at transition; scale visually for pedagogical clarity.
    z=np.where(x<0,-s1*x,-s2*x)
    ycrit=z+YC
    ynormal=np.where(x<0,z+y01,z+y02)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=x,y=z,mode='lines',name='Channel bed',line=dict(color='#a16207',width=4)))
    fig.add_trace(go.Scatter(x=x,y=ycrit,mode='lines',name='Critical-depth reference',line=dict(color='#dc2626',width=2,dash='dash')))
    fig.add_trace(go.Scatter(x=x,y=ynormal,mode='lines',name='Normal-depth reference',line=dict(color='#16a34a',width=2,dash='dot')))
    # Upstream/downstream governing boundaries, using numerical GVF integrations.
    if kind=='slope_mild_steep':
        # near-critical profiles: integrate away from critical control in each reach
        xa,ya=profile(s1,ks1,-0.001,-100,YC*1.012)
        xb,yb=profile(s2,ks2,0.001,100,YC*0.988)
        px=np.r_[xa[::-1],xb];py=np.r_[ya[::-1],yb]
    elif y01>YC and y02>YC:
        # downstream normal depth fixes transition; integrate upstream
        xa,ya=profile(s1,ks1,0,-100,y02)
        px=np.r_[xa[::-1],np.linspace(0,100,200)]
        py=np.r_[ya[::-1],np.full(200,y02)]
    elif y01<YC and y02<YC:
        # upstream normal depth fixes transition; integrate downstream
        xb,yb=profile(s2,ks2,0,100,y01)
        px=np.r_[np.linspace(-100,0,200),xb]
        py=np.r_[np.full(200,y01),yb]
    else:
        # steep to mild: jump, schematic; variants locate it relative to break
        xjump=[0,42,-40][variant]
        xx1=np.linspace(-100,xjump,260);xx2=np.linspace(xjump,100,260)
        # Short jump drawn with separate left and right branches.
        # Conjugate relation used at break if variant=0; other positions illustrative.
        y_before=y01
        y_after=0.5*y_before*(math.sqrt(1+8*(Q/(B*y_before))**2/(G*y_before))-1)
        if variant==1: y_after=min(y02*0.92,y_after)
        if variant==2: y_after=max(y02*0.96,y_after)
        px=np.r_[xx1,xx2];py=np.r_[np.full(len(xx1),y_before),np.full(len(xx2),y_after)]
        # For downstream reach, blend gently to normal depth away from jump.
        py[len(xx1):]=y02+(y_after-y02)*np.exp(-(xx2-xjump)/28)
    zprofile=np.where(px<0,-s1*px,-s2*px)
    fig.add_trace(go.Scatter(x=px,y=zprofile+py,mode='lines',name='Water-surface profile',line=dict(color='#0284c7',width=4)))
    fig.add_vline(x=0,line_dash='dot',line_color='gray',opacity=0.6)
    fig.update_layout(height=380,margin=dict(l=10,r=10,t=32,b=30),xaxis_title='Longitudinal distance x (m)',yaxis_title='Elevation (m)',legend=dict(orientation='h',y=-0.24),hovermode='x unified')
    return fig

def specific_force_comparison(case_index):
    """One separate specific-force plot for each of the three manuscript cases."""
    ks = 75.0
    s1 = critical_slope(ks) * 3.0
    y01 = normal_depth(s1, ks)
    def sigma(y):
        return B * y * y / 2.0 + Q * Q / (G * B * y)

    froude_sq = Q * Q / (G * B * B * y01**3)
    yconj = y01 * (math.sqrt(1 + 8 * froude_sq) - 1) / 2
    cases = [
        ('Case 1 — Equal specific forces', yconj),
        ('Case 2 — Upstream specific force greater', (YC + yconj) / 2),
        ('Case 3 — Upstream specific force smaller', yconj * 1.28),
    ]
    label, y02 = cases[case_index]
    su, sd = sigma(y01), sigma(y02)
    yy = np.linspace(max(.07, YC * .16), max(yconj * 1.6, YC * 2.0), 700)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yy, y=[sigma(y) for y in yy], mode='lines',
                             name='Specific force Σ(y)', line=dict(color='#2563eb', width=3)))
    fig.add_vline(x=YC, line_dash='dash', line_color='#dc2626',
                  annotation_text='y꜀', annotation_position='top')
    fig.add_trace(go.Scatter(x=[y01], y=[su], mode='markers',
                             name='Upstream: Σ(y₀,₁)',
                             marker=dict(size=13, color='#0f766e', symbol='diamond')))
    fig.add_trace(go.Scatter(x=[y02], y=[sd], mode='markers',
                             name='Downstream: Σ(y₀,₂)',
                             marker=dict(size=13, color='#f59e0b', symbol='circle')))
    fig.add_hline(y=su, line_dash='dot', line_color='#0f766e', opacity=.8)
    fig.add_hline(y=sd, line_dash='dot', line_color='#f59e0b', opacity=.8)
    fig.update_layout(title=label, height=420,
                      margin=dict(l=15, r=15, t=50, b=65),
                      xaxis_title='Depth y (m)', yaxis_title='Specific force Σ (m³)',
                      legend=dict(orientation='h', y=-.30), hovermode='closest')
    return fig, y01, y02, su, sd

CAPTIONS={
'slope_mild_steep':'Mild → steep: critical control at the slope break; M2 upstream and S2 downstream.',
'slope_mild_mild_decrease':'Mild → mild, increasing bed slope: upstream M2 profile.',
'slope_mild_mild_increase':'Mild → mild, decreasing bed slope: upstream M1 profile.',
'slope_steep_steep_decrease':'Steep → steep, decreasing bed slope: downstream S3 profile.',
'slope_steep_steep_increase':'Steep → steep, increasing bed slope: downstream S2 profile.',
'rough_mild_decrease':'Mild reach, decreasing roughness (increasing Strickler coefficient): upstream M2 profile.',
'rough_mild_increase':'Mild reach, increasing roughness (decreasing Strickler coefficient): upstream M1 profile.',
'rough_steep_increase':'Steep reach, increasing roughness: downstream S3 profile.',
'rough_steep_decrease':'Steep reach, decreasing roughness: downstream S2 profile.',
}

def render():
    path=Path(__file__).with_name('theory.md')
    if not path.exists():
        st.error('Missing theory.md')
        return
    content=path.read_text(encoding='utf-8')
    parts=re.split(r'<!-- PROFILE_FIGURE:([a-z_]+) -->',content)
    for j,part in enumerate(parts):
        if j%2==0:
            if part.strip():st.markdown(part)
        elif part.startswith('specific_force_case_'):
            case_index = int(part.rsplit('_', 1)[1]) - 1
            chart, y01, y02, su, sd = specific_force_comparison(case_index)
            st.plotly_chart(chart, use_container_width=True,
                            key=f'm05_specific_force_case_{case_index+1}')
            symbol = '=' if abs(su-sd) < 1e-8 else '>' if su > sd else '<'
            st.markdown(
                f'**Comparison at the slope change:** '
                f'y₀,₁ = {y01:.3f} m; y₀,₂ = {y02:.3f} m. '
                f'**Σ(y₀,₁) = {su:.3f} m³ {symbol} '
                f'Σ(y₀,₂) = {sd:.3f} m³.**'
            )
            st.caption('Illustrative rectangular channel: Q = 10 m³/s, '
                       'b = 4 m, Kₛ = 75 m¹ᐟ³/s. The green diamond is the '
                       'upstream state, the orange circle the downstream state; '
                       'the red dashed line marks critical depth.')
        elif part=='jump_cases':
            st.markdown('**Schematic jump locations for the three specific-force cases**')
            for variant,title in enumerate(('Case 1 — jump at the transition','Case 2 — jump downstream','Case 3 — jump upstream')):
                st.markdown('**'+title+'**')
                st.plotly_chart(figure(part,variant),use_container_width=True,key=f'm05_jump_{variant}')
            st.caption('Hydraulic-jump sketches are qualitative: the discontinuity is not a gradually varied solution. Exact jump position requires momentum matching and compatible profiles.')
        else:
            st.plotly_chart(figure(part),use_container_width=True,key=f'm05_{part}')
            st.caption(CAPTIONS[part]+' Illustrative parameters; full rectangular hydraulic radius.')
