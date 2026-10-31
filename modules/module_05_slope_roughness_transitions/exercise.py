"""Module 05 — transition exercises using explicit spatial Euler integration."""



import math



import random



import numpy as np



import plotly.graph_objects as go



import streamlit as st



from types import SimpleNamespace



from scipy.optimize import brentq







G = 9.81



CASES = [



    ('mild_steep', 'Mild → Steep'),



    ('mild_mild_up', 'Mild → Mild · M1'),



    ('mild_mild_down', 'Mild → Mild · M2'),



    ('steep_steep_up', 'Steep → Steep · S2'),



    ('steep_steep_down', 'Steep → Steep · S3'),



    ('rough_mild_up', 'Mild · increased roughness'),



    ('rough_mild_down', 'Mild · decreased roughness'),



    ('rough_steep_up', 'Steep · increased roughness'),



    ('rough_steep_down', 'Steep · decreased roughness'),



    ('jump_upstream', 'Steep → Mild · jump upstream'),



    ('jump_at', 'Steep → Mild · jump at transition'),



    ('jump_downstream', 'Steep → Mild · jump downstream'),



]











def yc_of(q, b):



    return (q*q/(G*b*b))**(1/3)











def sf(y, q, b, ks):



    y = np.asarray(y)



    a = b*y



    r = a/(b+2*y)



    return (q/(ks*a*r**(2/3)))**2











def yn_of(q, b, ks, slope):

    """Module 04 uniform-flow algorithm: full-radius Strickler, 90 bisections."""

    if min(q, b, ks, slope) <= 0:

        raise ValueError("Q, b, Ks and S0 must be strictly positive.")



    def discharge_at_depth(y):

        if y <= 0:

            return 0.0

        area = b * y

        radius = area / (b + 2 * y)

        return ks * area * radius ** (2.0 / 3.0) * math.sqrt(slope)



    lo = 0.0

    hi = max(1.0, (q / (ks * b * math.sqrt(slope))) ** 0.6 * 2)

    while discharge_at_depth(hi) < q:

        hi *= 2

    for _ in range(90):

        mid = (lo + hi) / 2

        if discharge_at_depth(mid) < q:

            lo = mid

        else:

            hi = mid

    return (lo + hi) / 2







def slope_type(y0, yc, slope, sc):
    """Same classification rule as Module 04 Uniform Flow."""
    if math.isclose(slope, sc, rel_tol=1e-9):
        return 'Critical'
    return 'Mild' if y0 > yc else 'Steep'


def sigma(y, q, b):



    return b*y*y/2 + q*q/(G*b*y)











def energy(y, q, b):



    return y + q*q/(2*G*b*b*y*y)











def conjugate(y, q, b):



    fr2 = q*q/(G*b*b*y**3)



    return y*(math.sqrt(1+8*fr2)-1)/2











def ode(x, z, q, b, ks, s0):



    y = float(z[0])



    if y <= 0:



        return [0.0]



    fr2 = q*q/(G*b*b*y**3)



    return [(s0-float(sf(y,q,b,ks)))/(1-fr2)]











EULER_DX = 0.10  # Maximum spatial step [m], as in Module 05 Toy v5.

EULER_MIN_DX = 1e-7





def integrate(x0, y0, x1, q, b, ks, s0, yc):

    """Defina §8.2.1: explicit spatial Euler with critical-flow safeguards.



    All accepted steps use y_next = y + dx * (S0 - Sf)/(1 - Fr²).

    The spatial step is subdivided near critical flow, never RK45.

    Return a solve_ivp-compatible interface for existing plots/jump matching.

    """

    if not math.isfinite(y0) or y0 <= 0 or abs(y0-yc) < 1e-6*yc:

        raise ValueError('Cannot start Euler integration at invalid/critical depth')

    direction = 1 if x1 >= x0 else -1

    x, y = float(x0), float(y0)

    xs, ys = [x], [y]

    side = 1 if y > yc else -1

    while direction*(x1-x) > 1e-9:

        step = min(EULER_DX, abs(x1-x))

        fr2 = q*q/(G*b*b*y**3)

        denominator = 1.0-fr2

        if abs(denominator) < 1e-8:

            break

        dydx = (s0-float(sf(y,q,b,ks)))/denominator

        if not math.isfinite(dydx):

            break

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

        x, y = x+dx, y_next

        xs.append(x)

        ys.append(y)

    xx, yy = np.asarray(xs, dtype=float), np.asarray(ys, dtype=float)



    def dense(x_query):

        v = np.asarray(x_query, dtype=float)

        if (np.any(v < min(xx[0],xx[-1])-1e-7)

                or np.any(v > max(xx[0],xx[-1])+1e-7)):

            raise ValueError('Euler profile requested outside integrated interval')

        if direction < 0:

            values = np.interp(v, xx[::-1], yy[::-1])

        else:

            values = np.interp(v, xx, yy)

        return np.asarray([values])



    return SimpleNamespace(t=xx, y=np.asarray([yy]), sol=dense, success=True)





def make_data(kind):



    q = round(random.uniform(7,18),2)



    b = round(random.uniform(3.5,8),2)



    k1 = round(random.uniform(45,85),1)



    k2 = k1



    yc = yc_of(q,b)



    sc1 = float(sf(yc,q,b,k1))



    a = random.uniform(.23,.52)



    z = random.uniform(2.0,4.5)



    if kind == 'mild_steep':



        s1,s2 = sc1*a,sc1*z



    elif kind.startswith('mild_mild'):



        s1 = sc1*a



        s2 = s1*(random.uniform(1.4,2.1) if kind.endswith('up') else random.uniform(.48,.75))



    elif kind.startswith('steep_steep'):



        s1 = sc1*z



        s2 = s1*(random.uniform(1.3,1.9) if kind.endswith('up') else random.uniform(.52,.75))



    elif kind.startswith('rough_'):



        s1=s2=sc1*(a if 'mild' in kind else z)



        # Higher roughness = lower Ks = higher normal depth.



        k2 = round(k1*random.uniform(.60,.78) if kind.endswith('up') else k1*random.uniform(1.3,1.6),1)



        # Preserve the same slope class in both reaches.



        sc2 = float(sf(yc,q,b,k2))



        if ('mild' in kind and s1>=sc2) or ('steep' in kind and s1<=sc2):



            raise ValueError('Roughness change altered slope classification')



    else:



        s1,s2=sc1*z,sc1*a



    return dict(kind=kind,q=q,b=b,k1=k1,k2=k2,s1=s1,s2=s2,L1=60.,L2=65.)











def jump_branches(d,yL):



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











def solve_case(d):



    q,b=d['q'],d['b']



    yc=yc_of(q,b)



    d=dict(d)



    d['yc']=yc



    d['yn1']=yn_of(q,b,d['k1'],d['s1'])



    d['yn2']=yn_of(q,b,d['k2'],d['s2'])



    d['sc1']=float(sf(yc,q,b,d['k1']))



    d['sc2']=float(sf(yc,q,b,d['k2']))



    d['class1'] = slope_type(d['yn1'], yc, d['s1'], d['sc1'])
    d['class2'] = slope_type(d['yn2'], yc, d['s2'], d['sc2'])
    kind=d['kind']



    L1,L2=d['L1'],d['L2']



    if kind.startswith('jump_'):



        # Select a downstream boundary depth, then locate the jump by force matching.



        # For 'at transition', construct the boundary condition by shooting from



        # the conjugate state at x=0; the solver still determines xJ independently.



        if kind=='jump_at':



            y0=conjugate(d['yn1'],q,b)



            s=integrate(0,y0,L2,q,b,d['k2'],d['s2'],yc)



            if s.t[-1]<L2-1e-6: raise ValueError('Downstream branch stopped')



            yL=float(s.sol(L2)[0])



        else:



            yL=d['yn2']*random.uniform(.65,1.65)



            if yL<=yc*1.02: raise ValueError('Downstream depth not subcritical')



        j=jump_branches(d,yL)



        if kind=='jump_upstream' and j['xj']>=-2: raise ValueError('Jump not upstream')



        if kind=='jump_downstream' and j['xj']<=2: raise ValueError('Jump not downstream')



        if kind=='jump_at' and abs(j['xj'])>0.05: raise ValueError('Jump not at break')



        if abs(j['xj'])>min(L1,L2)*.92: raise ValueError('Jump too close to boundary')



        d['jump']=j



        d['boundary']=f"y({L2:.0f} m) = {yL:.3f} m (downstream control)"



    elif kind=='mild_steep':



        # Critical control at the transition. Avoid integrating at singular yc.



        eps=0.002*yc



        left=integrate(0,yc+eps,-L1,q,b,d['k1'],d['s1'],yc)



        right=integrate(0,yc-eps,L2,q,b,d['k2'],d['s2'],yc)



        d['left'],d['right']=left,right



        d['boundary']='Critical control y(0) = yc (profiles start just off critical)'



    elif kind.startswith('mild_mild') or kind.startswith('rough_mild'):



        # Subcritical control from reach 2 normal depth.



        left=integrate(0,d['yn2'],-L1,q,b,d['k1'],d['s1'],yc)



        d['left']=left



        d['boundary']='Downstream uniform-flow control y(0) = y0,2'



    else:



        # Supercritical control from reach 1 normal depth.



        right=integrate(0,d['yn1'],L2,q,b,d['k2'],d['s2'],yc)



        d['right']=right



        d['boundary']='Upstream uniform-flow control y(0) = y0,1'



    return d











def generate_case():



    # Cycle through the scenario list before repeating any category.



    if 'm05_remaining' not in st.session_state or not st.session_state.m05_remaining:



        pool=[k for k,_ in CASES]



        random.shuffle(pool)



        st.session_state.m05_remaining=pool



    for _ in range(len(st.session_state.m05_remaining)):



        kind=st.session_state.m05_remaining.pop()



        for _ in range(65 if kind.startswith('jump_') else 12):



            try:



                d=solve_case(make_data(kind))



                return d



            except (ValueError,OverflowError,ZeroDivisionError,FloatingPointError):



                continue



    raise RuntimeError('Could not generate a valid case. Click Generate again.')











def bed(x,d):



    x=np.asarray(x)



    return np.where(x<0,-d['s1']*x,-d['s2']*x)











def plot_profile(d):



    L1,L2=d['L1'],d['L2']



    x=np.linspace(-L1,L2,650)



    zb=bed(x,d)



    f=go.Figure()



    def trace(x,y,name,color,dash=None,width=3):



        f.add_trace(go.Scatter(x=x,y=y,mode='lines',name=name,



                               line=dict(color=color,width=width,dash=dash)))



    trace(x,zb,'Channel bed','#99602d',width=5)



    trace(x,zb+d['yc'],'Critical depth yc','red','dash',2)



    trace(x,zb+np.where(x<0,d['yn1'],d['yn2']),



          'Normal depth y0','green','dot',2)



    kind=d['kind']



    if kind.startswith('jump_'):



        j=d['jump']; xj=j['xj']



        xa=np.linspace(-L1,xj,280)



        xb=np.linspace(xj,L2,280)



        trace(xa,bed(xa,d)+np.array([j['depth_up'](v) for v in xa]),



              'Supercritical profile','#087ec2',width=4)



        trace(xb,bed(xb,d)+np.array([j['depth_dn'](v) for v in xb]),



              'Subcritical profile','#087ec2',width=4)



        trace([xj,xj],[float(bed(xj,d))+j['yu'],float(bed(xj,d))+j['yd']],



              f'Hydraulic jump xJ={xj:.2f} m','#003c91',width=7)



        f.add_vline(x=xj,line_dash='dash',line_color='gray')



    elif kind=='mild_steep':



        a=np.linspace(float(d['left'].t[-1]),0,260)



        c=np.linspace(0,float(d['right'].t[-1]),260)



        trace(a,bed(a,d)+d['left'].sol(a)[0],'M2 profile','#087ec2',width=4)



        trace(c,bed(c,d)+d['right'].sol(c)[0],'S2 profile','#087ec2',width=4)



        f.add_annotation(x=0,y=d['yc'],text='Critical control',showarrow=True,ay=-50)



    elif 'left' in d:



        a=np.linspace(float(d['left'].t[-1]),0,300)



        c=np.linspace(0,L2,200)



        trace(a,bed(a,d)+d['left'].sol(a)[0],'GVF profile · reach 1','#087ec2',width=4)



        trace(c,bed(c,d)+d['yn2'],'Uniform flow · reach 2','#087ec2',width=4)



    else:



        a=np.linspace(-L1,0,200)



        c=np.linspace(0,float(d['right'].t[-1]),300)



        trace(a,bed(a,d)+d['yn1'],'Uniform flow · reach 1','#087ec2',width=4)



        trace(c,bed(c,d)+d['right'].sol(c)[0],'GVF profile · reach 2','#087ec2',width=4)



    # Hydraulic boundary control, shown on the graph rather than supplied

    # in the exercise statement. Use the exact depth employed by the solver.

    if kind.startswith('jump_'):

        control_x = float(L2)

        control_y = float(d['jump']['yL'])

        control_name = 'Downstream boundary control'

    elif kind == 'mild_steep':

        control_x = 0.0

        control_y = float(d['yc'])

        control_name = 'Critical control'

    elif 'left' in d:

        control_x = 0.0

        control_y = float(d['yn2'])

        control_name = 'Downstream control'

    else:

        control_x = 0.0

        control_y = float(d['yn1'])

        control_name = 'Upstream control'



    f.add_trace(go.Scatter(

        x=[control_x],

        y=[float(bed(control_x, d)) + control_y],

        mode='markers',

        name='Boundary control',

        marker=dict(symbol='circle-open', size=16, color='#dc2626',

                    line=dict(color='#dc2626', width=3)),

        hovertemplate=(control_name + '<br>x=%{x:.2f} m'

                       + '<br>y=' + f'{control_y:.4f} m<extra></extra>'),

    ))



    # Labels centered on the actual visible profile segments. A jump may

    # split one reach into two differently classified water-surface branches.

    def profile_label(depth, yn):

        yc = d['yc']

        if abs(depth - yn) <= 1e-5 * max(1.0, yn):

            return 'UNIFORM'

        if depth > max(yn, yc):

            zone = '1'

        elif depth < min(yn, yc):

            zone = '3'

        else:

            zone = '2'

        return ('M' if yn > yc else 'S') + zone + ' PROFILE'



    segments = []

    if kind.startswith('jump_'):

        xj = d['jump']['xj']

        # Each side of the jump is a distinct hydraulic profile.

        for xa, xb, yn, depth_fn in (

            (-L1, min(0.0, xj), d['yn1'], d['jump']['depth_up']),

            (max(-L1, xj), 0.0, d['yn1'], d['jump']['depth_dn']),

            (0.0, min(L2, xj), d['yn2'], d['jump']['depth_up']),

            (max(0.0, xj), L2, d['yn2'], d['jump']['depth_dn']),

        ):

            if xb - xa > 1e-6:

                segments.append((xa, xb, yn, depth_fn))

    elif kind == 'mild_steep':

        segments = [

            (-L1, 0.0, d['yn1'], lambda x: float(d['left'].sol(x)[0])),

            (0.0, L2, d['yn2'], lambda x: float(d['right'].sol(x)[0])),

        ]

    elif 'left' in d:

        segments = [

            (-L1, 0.0, d['yn1'], lambda x: float(d['left'].sol(x)[0])),

            (0.0, L2, d['yn2'], lambda x: d['yn2']),

        ]

    else:

        segments = [

            (-L1, 0.0, d['yn1'], lambda x: d['yn1']),

            (0.0, L2, d['yn2'], lambda x: float(d['right'].sol(x)[0])),

        ]



    for xa, xb, yn, depth_fn in segments:

        xm = 0.5 * (xa + xb)

        ym = float(depth_fn(xm))

        f.add_annotation(

            x=xm, y=float(bed(xm, d)) + ym,

            text=f'<b>{profile_label(ym, yn)}</b>',

            showarrow=False, yshift=24, xanchor='center',

            font=dict(size=12, color='#174b78'),

            bgcolor='rgba(255,255,255,0.85)', borderpad=3,

        )



    # Slope names appear BELOW the bed, centered on each physical reach.

    for xm, yn in ((-0.5 * L1, d['yn1']), (0.5 * L2, d['yn2'])):

        slope_name = d['class1'].upper() + ' SLOPE' if xm < 0 else d['class2'].upper() + ' SLOPE'

        f.add_annotation(

            x=xm, y=float(bed(xm, d)),

            text=f'<b>{slope_name}</b>',

            showarrow=False, yshift=-24, xanchor='center',

            font=dict(size=12, color='#875022'),

            bgcolor='rgba(255,255,255,0.88)', borderpad=3,

        )



    f.update_yaxes(autorange=True)

    f.add_vline(x=0,line_dash='dot',line_color='black')



    f.update_layout(title='Integrated longitudinal water-surface profile',



                    xaxis_title='x (m)',yaxis_title='Elevation (m)',



                    template='plotly_white',height=530,margin=dict(t=65,b=100),



                    legend=dict(orientation='h',y=-.28))



    return f











def plot_forces(d):



    j=d['jump']; q,b=d['q'],d['b']



    x=np.linspace(j['lo'],j['hi'],450)



    su=np.array([sigma(j['depth_up'](v),q,b) for v in x])



    sd=np.array([sigma(j['depth_dn'](v),q,b) for v in x])



    f=go.Figure()



    f.add_scatter(x=x,y=su,name='ΣU(x) · supercritical',line=dict(color='#087ec2',width=3))



    f.add_scatter(x=x,y=sd,name='ΣD(x) · subcritical',line=dict(color='#e77728',width=3))



    f.add_scatter(x=[j['xj']],y=[j['force']],mode='markers',



                  marker=dict(color='black',size=12),name='ΣU = ΣD')



    f.add_vline(x=j['xj'],line_dash='dash',line_color='gray')



    f.update_layout(title='Specific-force matching: numerical intersection',



                    xaxis_title='x (m)',yaxis_title='Σ (m³)',



                    template='plotly_white',height=420)



    return f











def plot_conjugate(d):



    j=d['jump']; q,b=d['q'],d['b']



    yy=np.linspace(max(.01,j['yu']*.45),j['yd']*1.5,450)



    f=go.Figure()



    f.add_scatter(x=yy,y=sigma(yy,q,b),name='Σ(y)',line=dict(color='#555555',width=3))



    f.add_scatter(x=[j['yu'],j['yd']],y=[j['force']]*2,



                  mode='lines+markers',name='Equal specific force',



                  line=dict(color='purple',dash='dash'),marker=dict(size=11))



    f.add_vline(x=d['yc'],line_color='red',line_dash='dot')



    f.update_layout(title='Conjugate depths at the jump',



                    xaxis_title='Depth y (m)',yaxis_title='Σ (m³)',



                    template='plotly_white',height=390)



    return f











def render():



    st.header('Exercise — Changes in Bed Slope and Roughness')



    st.caption('One exercise at a time · all transition families · numerical GVF')



    key='m05_all_scenarios_exercise_v1'



    if key not in st.session_state:



        try: st.session_state[key]=generate_case()



        except RuntimeError as exc:



            st.error(str(exc)); return



    if st.button('Generate new exercise',type='primary',key='m05_all_generate'):



        try:



            with st.spinner('Generating and solving a new hydraulic scenario...'):



                st.session_state[key]=generate_case()



        except RuntimeError as exc: st.warning(str(exc))



    d=st.session_state[key]



    kind=d['kind']



    title=dict(CASES)[kind]



    st.subheader('Problem · '+title)



    st.markdown(

        'Consider a prismatic rectangular open channel consisting of two '

        'reaches connected at $x=0$. The channel carries a steady discharge '

        'and has the following geometric and hydraulic properties.'

    )

    st.markdown('**Given data**')

    st.latex(rf"Q={d['q']:.2f}\ \mathrm{{m^3/s}},\qquad b={d['b']:.2f}\ \mathrm{{m}}")

    st.latex(rf"K_{{s,1}}={d['k1']:.1f},\qquad K_{{s,2}}={d['k2']:.1f}\ \mathrm{{m^{{1/3}}/s}}")

    st.latex(rf"S_{{0,1}}={d['s1']:.6f},\qquad S_{{0,2}}={d['s2']:.6f}")

    st.latex(rf"L_1={d['L1']:.0f}\ \mathrm{{m}},\qquad L_2={d['L2']:.0f}\ \mathrm{{m}}")

    st.markdown(

        '**Required**\n'

        '1. Calculate the normal depths in both reaches using the '

        'Gauckler–Strickler equation and determine the critical depth.\n'

        '2. Classify each bed slope as mild or steep.\n'

        '3. Identify the expected water-surface profile in each reach '

        'and determine the appropriate hydraulic control.\n'

        '4. Integrate the gradually varied flow profiles using the '

        'explicit spatial Euler method.\n'

        '5. Determine whether a hydraulic jump occurs. If it does, '

        'find its position and the conjugate depths.'

    )



    with st.expander('Show complete solution',expanded=True):



        st.markdown('### 1. Uniform and critical depths')



        st.latex(r'Q=K_s A(y_0)R(y_0)^{2/3}\sqrt{S_0},\qquad y_c=(Q^2/(gb^2))^{1/3}')



        st.write(f"y₀,₁ = {d['yn1']:.4f} m · y₀,₂ = {d['yn2']:.4f} m · yc = {d['yc']:.4f} m")



        st.markdown('### 2. Slope classification')



        st.write(f"Sc,1 = {d['sc1']:.6f} · Sc,2 = {d['sc2']:.6f}")



        c1=d['class1']



        c2=d['class2']



        st.write(f'Reach 1: **{c1}** · Reach 2: **{c2}**')
        st.markdown('**Method A — Compare normal and critical depths**')
        st.write(f"Reach 1: y₀ = {d['yn1']:.4f} m; yc = {d['yc']:.4f} m → {c1}")
        st.write(f"Reach 2: y₀ = {d['yn2']:.4f} m; yc = {d['yc']:.4f} m → {c2}")
        st.markdown('**Method B — Compare bed and critical slopes**')
        st.latex(r'S_c=\left[\frac{Q}{K_s A_c R_c^{2/3}}\right]^2')
        st.write(f"Reach 1: S₀ = {d['s1']:.6g}; Sc = {d['sc1']:.6g} → {c1}")
        st.write(f"Reach 2: S₀ = {d['s2']:.6g}; Sc = {d['sc2']:.6g} → {c2}")




        st.markdown('### 3. Controlling boundary condition')



        st.write(d['boundary'])



        st.markdown('### 4. Integrated water-surface profiles')



        st.latex(r'\frac{dy}{dx}=\frac{S_0-S_f(y)}{1-\mathrm{Fr}^2(y)}')



        st.plotly_chart(plot_profile(d),use_container_width=True)



        st.markdown('### 5. Hydraulic-jump assessment')



        if kind.startswith('jump_'):



            j=d['jump']



            st.latex(r'\Sigma(y)=\frac{by^2}{2}+\frac{Q^2}{gby}')



            st.latex(r'\Sigma_U(x_J)=\Sigma_D(x_J)')



            st.plotly_chart(plot_forces(d),use_container_width=True)



            st.success(f"Hydraulic jump: xJ = {j['xj']:.4f} m; "



                       f"yU = {j['yu']:.4f} m; yD = {j['yd']:.4f} m")



            st.write(f"Equal force Σ = {j['force']:.6f} m³; "



                     f"residual = {abs(j['residual']):.2e} m³")



            st.plotly_chart(plot_conjugate(d),use_container_width=True)



            loss=energy(j['yu'],d['q'],d['b'])-energy(j['yd'],d['q'],d['b'])



            st.latex(r'\Delta E=\frac{(y_D-y_U)^3}{4y_Dy_U}')



            st.write(f'Energy loss ΔE = {loss:.5f} m')



        else:



            st.info('No hydraulic jump is required by the selected controls. '



                    'The displayed GVF branch connects continuously to its controlling state.')



        st.caption('Rectangular channel; hydrostatic pressure; full hydraulic-radius '



                   'Strickler friction; local momentum balance across a short jump. '



                   'Critical controls are integrated with a small offset to avoid '



                   'the GVF singularity. The plotted jump is an idealized discontinuity.')
