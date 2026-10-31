"""Quantitative theory: Manning GVF integration, specific energy and momentum."""
from pathlib import Path
import re
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from .hydraulics import energy,force,critical,normal,depth_at_energy,conjugate,integrate
BLUE='#0284c7'; RED='#dc2626'; GREEN='#16a34a'; BROWN='#a16207'; GRAY='#64748b'
LABELS={'steep_steep':'Case 1 · Steep / Steep','mild_mild_sufficient':'Case 2a · Mild / Mild — sufficient energy','mild_mild_insufficient':'Case 2b · Mild / Mild — insufficient energy','mild_steep':'Case 3 · Mild / Steep','steep_mild':'Case 4 · Steep / Mild'}

def calculate(case,q,b,n,a,length):
    k=critical(q); su=.018 if case.startswith('steep') else .0005
    sd=.018 if case in ('steep_steep','mild_steep') else .0005
    nu=normal(q,b,n,su); nd=normal(q,b,n,sd)
    # Each branch is integrated from its physically appropriate controlling boundary.
    # Jump locations are determined by equal specific force and a prescribed tailwater.
    branches=[]; jumps=[]; warnings=[]
    def add(x0,h0,x1,s,side):
        xx,hh=integrate(x0,h0,x1,s,q,b,n,k)
        branches.append((xx,hh,side));return xx,hh
    def transition(hu,down_branch):
        return depth_at_energy(energy(hu,q)+a,q,down_branch)
    if case=='steep_steep':
        xu,hu=add(-length,nu,0,su,'U')
        hd=transition(hu[-1],'super')
        add(0,hd,length,sd,'D')
    elif case=='mild_mild_sufficient':
        xd,hd=add(length,nd,0,sd,'D')
        hu=depth_at_energy(energy(hd[-1],q)-a,q,'sub')
        add(0,hu,-length,su,'U')
    elif case=='mild_steep':
        hu=k*1.002
        add(0,hu,-length,su,'U')
        hd=transition(k,'super')
        add(0,hd,length,sd,'D')
    elif case=='mild_mild_insufficient':
        # Upstream edge critical; downstream supercritical branch must match the
        # prescribed subcritical tailwater via a momentum-conserving hydraulic jump.
        # Start just above critical depth to avoid the singular GVF denominator.
        # The exact lip is h_c; the integrated M2 branch begins at h_c(1+epsilon).
        add(0,k*1.002,-length,su,'U')
        hd=transition(k,'super')
        find_jump(0,hd,length,nd,sd,q,b,n,k,'D',branches,jumps,warnings)
    else:
        # Steep/Mild: prescribed upstream normal flow and downstream tailwater.
        # Search for a downstream hydraulic jump. If matching fails, the displayed
        # branches remain separate, rather than inventing a jump location.
        xu,hu=add(-length,nu,0,su,'U')
        hd=transition(hu[-1],'super')
        find_jump(0,hd,length,nd,sd,q,b,n,k,'D',branches,jumps,warnings)
    return dict(case=case,branches=branches,jumps=jumps,warnings=warnings,k=k,nu=nu,nd=nd,su=su,sd=sd,q=q,b=b,n=n,a=a,length=length)

def find_jump(x0,h0,xend,tail,s,q,b,n,k,side,branches,jumps,warnings):
    from scipy.optimize import brentq
    # Independent integration of the incoming supercritical and outgoing
    # subcritical branches; jump position solves h_after = conjugate(h_before).
    xx,hh=integrate(x0,h0,xend,s,q,b,n,k)
    xd,hd=integrate(xend,tail,x0,s,q,b,n,k)
    def sample(x,arrx,arrh):return np.interp(x,arrx if arrx[0]<arrx[-1] else arrx[::-1],arrh if arrx[0]<arrx[-1] else arrh[::-1])
    left=max(min(xx),min(xd));right=min(max(xx),max(xd))
    if right-left<1e-5:
        branches.extend([(xx,hh,side),(xd,hd,side)])
        warnings.append('No overlap between incoming and tailwater-controlled profiles: jump location not resolved.')
        return
    def mismatch(x):return conjugate(sample(x,xx,hh),q)-sample(x,xd,hd)
    grid=np.linspace(left+1e-5,right-1e-5,150)
    roots=[]
    for u,v in zip(grid[:-1],grid[1:]):
        if mismatch(u)*mismatch(v)<0:roots.append(brentq(mismatch,u,v))
    if not roots:
        branches.extend([(xx,hh,side),(xd,hd,side)])
        warnings.append('No momentum-compatible hydraulic jump for the specified tailwater; both candidate profiles are shown separately.')
        return
    xj=roots[0]; hbefore=sample(xj,xx,hh); hafter=conjugate(hbefore,q)
    branches.append((np.r_[xx[xx<xj],xj],np.r_[hh[xx<xj],hbefore],side))
    branches.append((np.r_[xj,xd[xd>xj][::-1]],np.r_[hafter,hd[xd>xj][::-1]],side))
    jumps.append((xj,hbefore,hafter))

def profile_plot(data):
    L=data['length'];a=data['a'];k=data['k'];su=data['su'];sd=data['sd']
    def bed(x):return np.where(np.asarray(x)<0,-su*np.asarray(x),-a-sd*np.asarray(x))
    x=np.r_[np.linspace(-L,-1e-6,180),np.linspace(0,L,180)]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=x,y=bed(x),name='Channel bed',line=dict(color=BROWN,width=4)))
    for side,mask,norm in [('U',x<0,data['nu']),('D',x>=0,data['nd'])]:
        xs=x[mask]
        fig.add_trace(go.Scatter(x=xs,y=bed(xs)+norm,name=f'Normal depth hₙ,{side}',line=dict(color=GREEN,dash='dot',width=2)))
        fig.add_trace(go.Scatter(x=xs,y=bed(xs)+k,name=f'Critical depth h_c,{side}',line=dict(color=RED,dash='dash',width=2)))
    for idx,(xx,hh,side) in enumerate(data['branches']):
        fig.add_trace(go.Scatter(x=xx,y=np.where((np.asarray(xx)==0)&(side=='U'),0,bed(xx))+hh,name=f'Integrated GVF {side} {idx+1}',line=dict(color=BLUE,width=4),customdata=hh,hovertemplate='x=%{x:.2f} m<br>h=%{customdata:.3f} m<extra></extra>'))
    # Profile naming follows Module 07: uniform reaches are not labelled M/S.
    def profile_name(xx, hh, side):
        h = np.asarray(hh, dtype=float)
        xvals = np.asarray(xx, dtype=float)
        if len(h) < 2:
            return None
        hn = data['nu'] if side == 'U' else data['nd']
        slope = data['su'] if side == 'U' else data['sd']
        family = 'MILD' if hn > k else 'STEEP'
        # The true uniform solution is constant h=hn, not merely a reach
        # whose initial depth happens to be close to hn.
        if np.max(np.abs(h - hn)) <= max(1e-4, 0.002*hn):
            return 'Uniform flow'
        hm = float(np.median(h))
        if family == 'MILD':
            return 'M1' if hm > hn else ('M2' if hm > k else 'M3')
        return 'S1' if hm > k else ('S2' if hm > hn else 'S3')

    for xx, hh, side in data['branches']:
        if len(xx) < 2:
            continue
        mid = len(xx)//2
        bx = float(xx[mid])
        by = float(bed(np.array([bx]))[0] + hh[mid])
        name = profile_name(xx, hh, side)
        if name:
            fig.add_annotation(x=bx, y=by, text=f'<b>{name}</b>',
                               showarrow=False, yshift=19,
                               font=dict(color=BLUE, size=14))
    for side, slope, xa in [('U', su, -0.55*L), ('D', sd, 0.55*L)]:
        family = 'MILD SLOPE' if (data['nu'] if side == 'U' else data['nd']) > k else 'STEEP SLOPE'
        fig.add_annotation(x=xa, y=float(bed(np.array([xa]))[0])-0.18,
                           text=f'<b>{family}</b>', showarrow=False,
                           font=dict(color=BROWN, size=12))
    # Use the red open-circle convention of Modules 06 and 07.
    # Mark the controlling condition, including the critical control at the step.
    boundary_points = []
    upstream = [br for br in data['branches'] if br[2] == 'U']
    downstream = [br for br in data['branches'] if br[2] == 'D']
    for side, candidates, target, cases, label in [
        ('U', upstream, -L, ('steep_steep', 'steep_mild'), 'Upstream BC — uniform flow'),
        ('D', downstream, L, ('mild_mild_sufficient', 'mild_mild_insufficient', 'steep_mild'), 'Downstream BC — uniform flow'),
    ]:
        if data['case'] not in cases or not candidates:
            continue
        xx, hh, _ = min(candidates, key=lambda br: min(abs(np.asarray(br[0])-target)))
        idx = int(np.argmin(abs(np.asarray(xx)-target)))
        bx = float(xx[idx])
        by = float(bed(np.array([bx]))[0] + hh[idx])
        boundary_points.append((bx, by, label))
    if data['case'] in ('mild_steep', 'mild_mild_insufficient'):
        # The upstream lip is a critical control, not an externally prescribed BC.
        boundary_points.append((0., float(k), 'Critical control: h = h_c'))
    for bx, by, label in boundary_points:
        fig.add_trace(go.Scatter(
            x=[bx], y=[by], mode='markers', name=label,
            marker=dict(symbol='circle-open', size=17, color=RED,
                        line=dict(color=RED, width=3)),
            hovertemplate=label + '<extra></extra>', showlegend=False))
        fig.add_annotation(x=bx, y=by, text=label, showarrow=True,
                           ax=-105 if bx > 0 else 105, ay=-48,
                           arrowhead=2, arrowcolor='#344054', arrowwidth=1.5,
                           bgcolor='rgba(255,255,255,0.85)')
    for xj,h1,h2 in data['jumps']:
        zbed = float(bed(np.array([xj]))[0])
        fig.add_trace(go.Scatter(x=[xj,xj], y=[zbed+h1,zbed+h2],
                                 mode='lines+markers', name='Hydraulic jump',
                                 line=dict(color=BLUE,width=5),
                                 marker=dict(size=7,color=BLUE),
                                 hovertemplate=f'Jump at x = {xj:.2f} m<br>h₁ = {h1:.3f} m<br>h₂ = {h2:.3f} m<extra></extra>'))
        fig.add_annotation(x=xj,y=zbed+h2,text=f'<b>HJ · x = {xj:.2f} m</b>',
                           showarrow=True,ax=80,ay=-52,arrowhead=2,
                           arrowcolor='#344054',bgcolor='rgba(255,255,255,0.88)',
                           font=dict(color=BLUE,size=12))
    fig.add_trace(go.Scatter(x=[0,0],y=[-a,0],name='Step',line=dict(color=BROWN,width=5)))
    fig.update_layout(height=440,xaxis_title='Longitudinal coordinate x [m]',yaxis_title='Elevation z [m]',margin=dict(l=10,r=10,t=25,b=75),legend=dict(orientation='h',y=-.27),hovermode='closest')
    return fig

def _clean_plot(fig, xmax, ymax, height=510):
    """Shared uncluttered quantitative chart styling."""
    fig.update_layout(
        height=height, template='plotly_white',
        xaxis=dict(title='Depth h [m]', range=[0, xmax], zeroline=False),
        yaxis=dict(title='Specific energy E [m]', range=[0, ymax], zeroline=False),
        margin=dict(l=75, r=65, t=45, b=100),
        legend=dict(orientation='h', y=-0.24, x=0, font=dict(size=11)),
        font=dict(size=12), hovermode='closest')
    return fig


def _depth_label(fig, h, value, color, offset):
    # Labels are placed below the axis in paper coordinates so they cannot
    # collide with the energy curve or the vertical input/output arrows.
    fig.add_annotation(x=h, y=0, xref='x', yref='y',
                       text=f'h<sub>{value}</sub> = {h:.3f} m',
                       showarrow=False, yshift=-28 + offset,
                       xanchor='center', font=dict(color=color, size=12),
                       bgcolor='rgba(255,255,255,.94)')


def _energy_dimension(fig, x, lo, hi, a, ymax):
    color='#344054'
    fig.add_shape(type='line', x0=x, x1=x, y0=lo, y1=hi,
                  line=dict(color=color, width=1.6))
    tick=x*.015
    for y in (lo, hi):
        fig.add_shape(type='line', x0=x-tick, x1=x+tick, y0=y, y1=y,
                      line=dict(color=color, width=1.6))
    # Only the dimension line is drawn for short distances: arrowheads
    # would overlap one another at small energy differences.
    if hi-lo > .13*ymax:
        for target, origin in ((hi,lo+.28*(hi-lo)),(lo,hi-.28*(hi-lo))):
            fig.add_annotation(x=x,y=target,ax=x,ay=origin,
                               xref='x',yref='y',axref='x',ayref='y',
                               text='',showarrow=True,arrowhead=2,
                               arrowwidth=1.5,arrowsize=1,arrowcolor=color)
    fig.add_annotation(x=x,y=(lo+hi)/2,text=f'a = {a:.3f} m',
                       xanchor='left',xshift=16,showarrow=False,
                       bgcolor='rgba(255,255,255,.96)',
                       font=dict(color=color,size=12))


def energy_plot(data):
    q=data['q']; hc=data['k']; a=data['a']
    states={}
    for xx,hh,side in data['branches']:
        if side not in states and len(xx):
            idx=int(np.argmin(np.abs(xx)))
            h=float(hh[idx]); states[side]=(h,float(energy(h,q)))
    all_h=[hc,data['nu'],data['nd']]+[v[0] for v in states.values()]
    xmax=max(all_h)*1.9
    hs=np.linspace(max(hc*.32,1e-5),xmax*.88,600)
    energies=np.asarray(energy(hs,q))
    point_es=[v[1] for v in states.values()]
    ymax=max(max(point_es,default=0)*1.65,float(energy(hc,q))*2.0,
             float(np.percentile(energies,83))*1.08)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=hs,y=energies,name='E(h)',
                             line=dict(color=BLUE,width=3)))
    ec=float(energy(hc,q))
    fig.add_trace(go.Scatter(x=[hc],y=[ec],mode='markers',
                             name='Critical minimum',marker=dict(color=RED,size=10)))
    fig.add_annotation(x=hc,y=ec,text='E<sub>min</sub>',showarrow=False,
                       yshift=-20,xshift=22,font=dict(color=GRAY,size=12),
                       bgcolor='rgba(255,255,255,.92)')
    colors={'U':'#ef4444','D':'#16a34a'}
    # Keep energy labels in a left-hand gutter; each is attached to its own
    # horizontal level. Depth labels get staggered if the states are close.
    for side in ('U','D'):
        if side not in states: continue
        h,e=states[side];color=colors[side]
        fig.add_trace(go.Scatter(x=[h],y=[e],mode='markers',
                                 name=f'{side}: h={h:.3f} m, E={e:.3f} m',
                                 marker=dict(size=12,color=color)))
        fig.add_shape(type='line',x0=0,x1=h,y0=e,y1=e,
                      line=dict(color=color,width=1.3,dash='dash'))
        fig.add_annotation(x=0,y=e,text=f'E<sub>{side}</sub> = {e:.3f} m',
                           xanchor='left',yshift=15,showarrow=False,
                           bgcolor='rgba(255,255,255,.95)',
                           font=dict(color=color,size=12))
        # A single continuous arrow is clearer than a guide plus an arrow.
        if side=='U':
            target,origin=e,0
        else:
            target,origin=0,e
        fig.add_annotation(x=h,y=target,ax=h,ay=origin,
                           xref='x',yref='y',axref='x',ayref='y',
                           text='',showarrow=True,arrowhead=3,
                           arrowsize=1.2,arrowwidth=2,arrowcolor=color)
        fig.add_annotation(x=h,y=e*.58,text='Input' if side=='U' else 'Output',
                           showarrow=False,textangle=-90,
                           xshift=-22 if side=='U' else 22,
                           font=dict(color=color,size=12),
                           bgcolor='rgba(255,255,255,.9)')
    if 'U' in states and 'D' in states:
        hu=states['U'][0];hd=states['D'][0]
        close=abs(hu-hd)<.13*xmax
        _depth_label(fig,hu,'U',colors['U'],0)
        _depth_label(fig,hd,'D',colors['D'],-24 if close else 0)
        lo,hi=sorted((states['U'][1],states['D'][1]))
        _energy_dimension(fig,xmax*.78,lo,hi,a,ymax)
    else:
        for side,(h,_) in states.items(): _depth_label(fig,h,side,colors[side],0)
    return _clean_plot(fig,xmax,ymax)


def insufficient_energy_precheck_plot(data):
    q=data['q'];hc=data['k'];a=data['a'];hd=data['nd']
    ed=float(energy(hd,q));eu=ed-a;emin=float(energy(hc,q))
    xmax=max(2.2*hd,2.6*hc)
    hs=np.linspace(max(hc*.34,1e-5),xmax*.86,600)
    es=np.asarray(energy(hs,q))
    ymax=max(ed*1.55,emin*2.0,float(np.percentile(es,85))*1.08)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=hs,y=es,name='E(h)',line=dict(color=BLUE,width=3)))
    fig.add_trace(go.Scatter(x=[hc],y=[emin],mode='markers',
                             name='Critical minimum',marker=dict(color=RED,size=11)))
    fig.add_trace(go.Scatter(x=[hd],y=[ed],mode='markers',
                             name='Downstream input',marker=dict(color=GREEN,size=12)))
    for value,color,label in ((ed,GREEN,'E<sub>D</sub>'),
                              (eu,RED,'E<sub>U,required</sub>'),
                              (emin,GRAY,'E<sub>min</sub>')):
        if value>=0:
            fig.add_shape(type='line',x0=0,x1=xmax*.92,y0=value,y1=value,
                          line=dict(color=color,width=1.3,dash='dash'))
        fig.add_annotation(x=xmax*.68,y=max(0,value),
                           text=f'{label} = {value:.3f} m',
                           xanchor='left',yshift=16 if label!='E<sub>min</sub>' else -16,
                           showarrow=False,bgcolor='rgba(255,255,255,.96)',
                           font=dict(color=color,size=12))
    fig.add_annotation(x=hd,y=ed,ax=hd,ay=0,
                       xref='x',yref='y',axref='x',ayref='y',
                       text='',showarrow=True,arrowhead=3,arrowwidth=2,
                       arrowcolor=GREEN)
    fig.add_annotation(x=hd,y=ed*.56,text='Input',textangle=-90,
                       xshift=-22,showarrow=False,
                       font=dict(color=GREEN,size=12))
    _depth_label(fig,hd,'D',GREEN,0)
    fig.add_annotation(x=xmax*.48,y=emin*.65,
                       text='No admissible upstream depth',showarrow=False,
                       bgcolor='rgba(255,255,255,.96)',
                       font=dict(color=RED,size=12))
    if eu>=0: _energy_dimension(fig,xmax*.91,eu,ed,a,ymax)
    else:
        fig.add_annotation(x=xmax*.91,y=ed*.55,
                           text=f'a = {a:.3f} m',showarrow=False,
                           bgcolor='rgba(255,255,255,.96)',
                           font=dict(color='#344054',size=12))
    return _clean_plot(fig,xmax,ymax)


def momentum_plot(data):
    q=data['q'];hc=data['k']
    depths=[hc,data['nu'],data['nd']]
    for _,h1,h2 in data['jumps']:depths.extend((h1,h2))
    xmax=max(depths)*1.8
    hs=np.linspace(max(hc*.30,1e-5),xmax*.88,500)
    ms=np.asarray(force(hs,q))
    ymax=max(float(np.percentile(ms,85))*1.1,
             max((float(force(h1,q)) for _,h1,_ in data['jumps']),default=0)*1.5)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=hs,y=ms,name='M(h)',line=dict(color=BLUE,width=3)))
    mc=float(force(hc,q))
    fig.add_trace(go.Scatter(x=[hc],y=[mc],name='Minimum momentum',
                             mode='markers',marker=dict(color=RED,size=10)))
    fig.add_annotation(x=hc,y=mc,text='M<sub>min</sub>',showarrow=False,
                       yshift=-22,xshift=25,font=dict(color=GRAY,size=12),
                       bgcolor='rgba(255,255,255,.95)')
    for xj,h1,h2 in data['jumps']:
        m=float(force(h1,q))
        fig.add_trace(go.Scatter(x=[h1,h2],y=[m,m],
                                 name=f'HJ at x={xj:.2f} m',
                                 mode='markers+lines',marker=dict(size=11,color=GREEN),
                                 line=dict(dash='dash',color=GREEN,width=2)))
        for h,label,shift in ((h1,'h₁',-20),(h2,'h₂',20)):
            fig.add_annotation(x=h,y=m,text=f'{label} = {h:.3f} m',
                               showarrow=False,yshift=shift,
                               bgcolor='rgba(255,255,255,.96)',
                               font=dict(color=GREEN,size=12))
    fig.update_layout(height=450,template='plotly_white',
                      xaxis=dict(title='Depth h [m]',range=[0,xmax]),
                      yaxis=dict(title='Specific force M [m²]',range=[0,ymax]),
                      margin=dict(l=75,r=65,t=45,b=100),
                      legend=dict(orientation='h',y=-.24,x=0,font=dict(size=11)))
    return fig

# Fixed, reproducible examples: no user-facing numerical controls.
# Values are illustrative and are not taken from the handwritten notes.
EXAMPLES = {
    'steep_steep': dict(q=2.0, b=4.0, n=.025, a=.35, length=25.),
    'mild_mild_sufficient': dict(q=2.0, b=4.0, n=.025, a=.20, length=25.),
    'mild_mild_insufficient': dict(q=0.4, b=4.0, n=.025, a=3.00, length=25.),
    'mild_steep': dict(q=2.0, b=4.0, n=.025, a=.35, length=25.),
    'steep_mild': dict(q=0.6, b=4.0, n=.012, a=.35, length=25.),
}

def render():
    st.subheader('Five fixed numerical cases — no parameter controls')
    st.caption('Fixed numerical examples · rectangular channel · Manning GVF. '
               'Parameters are selected for illustration; the manuscript provides no numerical values.')
    source=Path(__file__).with_name('theory.md').read_text(encoding='utf-8')
    parts=re.split(r'<!-- CASE:([a-z_]+) -->',source)
    for i,part in enumerate(parts):
        if i%2==0:
            st.markdown(part)
        else:
            params=EXAMPLES[part]
            st.markdown('**Assigned numerical data (fixed):** '
                        f"q = {params['q']:.2f} m²/s · b = {params['b']:.2f} m · "
                        f"n = {params['n']:.3f} · a = {params['a']:.2f} m · "
                        f"L = {params['length']:.0f} m · "
                        'S_steep = 0.018 · S_mild = 0.0005')
            try:
                data=calculate(part,**params)
                st.caption({'steep_steep':'Boundary condition: upstream uniform supercritical flow.', 'mild_mild_sufficient':'Boundary condition: downstream uniform subcritical flow.', 'mild_mild_insufficient':'Boundary condition: downstream uniform subcritical flow; upstream step edge is critical.', 'mild_steep':'Control at the step: upstream edge h = h_c (no externally imposed boundary at the step).', 'steep_mild':'Two boundary conditions: upstream uniform supercritical flow and downstream uniform subcritical flow.'}[part])
                if part == 'mild_mild_insufficient':
                    st.markdown('**Preliminary energy check — insufficient energy**')
                    st.caption('Before upstream adjustment: assuming downstream uniform flow, '
                               'E_U,required = E_D − a < E_min. No real upstream depth '
                               'satisfies the energy equation; critical control and backwater '
                               'must therefore be considered.')
                    st.plotly_chart(insufficient_energy_precheck_plot(data),
                                    use_container_width=True, key='precheck_'+part)
                st.plotly_chart(profile_plot(data),use_container_width=True,key='profile_'+part)
                st.plotly_chart(energy_plot(data),use_container_width=True,key='energy_'+part)
                if part in ('mild_mild_insufficient','steep_mild'):
                    st.plotly_chart(momentum_plot(data),use_container_width=True,key='momentum_'+part)
                st.caption(f"h_c = {data['k']:.3f} m · hₙ,U = {data['nu']:.3f} m · "
                           f"hₙ,D = {data['nd']:.3f} m · resolved hydraulic jumps: {len(data['jumps'])}")
                for xj,h1,h2 in data['jumps']:
                    st.caption(f'Hydraulic jump: x = {xj:.2f} m downstream of the step · h₁ = {h1:.3f} m · h₂ = {h2:.3f} m (equal specific force).')
                for msg in data['warnings']:
                    st.warning(msg)
            except (ValueError,ArithmeticError) as exc:
                st.warning(f'No admissible steady profile for this fixed example: {exc}')
