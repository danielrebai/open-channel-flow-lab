"""Module 07 — Outflow into a Reservoir: generated worked exercise.

Rectangular channel; explicit Euler GVF and momentum-based hydraulic-jump matching.
The free jet and the jump outside the channel are not resolved by 1-D GVF.
"""
import math
import random

import numpy as np
import plotly.graph_objects as go
import streamlit as st

G = 9.81
L = 100.0


def _normal_depth(q, b, ks, slope):
    def discharge(h):
        a = b*h
        r = a/(b+2*h)
        return ks*a*r**(2/3)*math.sqrt(slope)
    lo, hi = 1e-9, 1.0
    while discharge(hi) < q:
        hi *= 2
    for _ in range(85):
        mid = (lo+hi)/2
        if discharge(mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def _fr2(h, q, b):
    return q*q/(G*b*b*h**3)


def _sf(h, q, b, ks):
    a = b*h
    r = a/(b+2*h)
    return (q/(ks*a*r**(2/3)))**2


def _euler(x0, x1, h0, d, target=None):
    """First-order explicit Euler, with adaptive spatial steps (Module 04)."""
    direction = 1 if x1 > x0 else -1
    x, h = float(x0), float(h0)
    xs, hs = [x], [h]
    hc = d['hc']
    for _ in range(30000):
        remaining = abs(x1-x)
        if remaining < 1e-9:
            break
        denom = 1-_fr2(h, d['Q'], d['B'])
        if h <= 0 or abs(denom) < 1e-10:
            break
        f = (d['S0']-_sf(h, d['Q'], d['B'], d['Ks']))/denom
        dx = min(remaining, (1.0 if h > hc else 0.5)*h)
        if abs(f) > 1e-12:
            dx = min(dx, 0.025*max(h, 0.05)/abs(f))
            if abs(h-hc) > 0.005:
                dx = min(dx, 0.25*abs(h-hc)/abs(f))
        if dx < 1e-8:
            break
        for _attempt in range(35):
            hnew = h + direction*f*dx
            if (math.isfinite(hnew) and hnew > 0 and
                (hnew-hc)*(h-hc) > 0 and
                abs(hnew-h) <= 0.05*max(h, 0.05)):
                break
            dx *= 0.5
        else:
            break
        xnew = x+direction*dx
        if target is not None and (h-target)*(hnew-target) <= 0:
            frac = (target-h)/(hnew-h)
            xs.append(x+frac*(xnew-x))
            hs.append(target)
            return np.array(xs), np.array(hs), True
        x, h = xnew, hnew
        xs.append(x)
        hs.append(h)
    return np.array(xs), np.array(hs), False


def _conjugate(h, d):
    return h/2*(math.sqrt(1+8*_fr2(h, d['Q'], d['B']))-1)


def _solve(d):
    hn, hc, hd = d['h0'], d['hc'], d['Hd']
    x = np.linspace(0, L, 501)
    if hn > hc:
        if hd > hn + 1e-7:
            kind, name, bc = 'mild_m1', 'M1', 'Downstream: h(L) = H_D'
        elif hd > hc + 1e-7 and hd < hn - 1e-7:
            kind, name, bc = 'mild_m2', 'M2', 'Downstream: h(L) = H_D'
        elif abs(hd-hn) <= 1e-7:
            kind, name, bc = 'mild_uniform', 'Uniform flow', 'Downstream: h(L) = h_0'
        else:
            kind, name, bc = 'mild_free', 'M2', 'Idealized outlet critical control: h(L) ≈ h_c'
        if kind == 'mild_uniform':
            segments = [(x, np.full_like(x, hn), 'Uniform flow')]
        else:
            start = hd if kind != 'mild_free' else hc+0.001
            xx, hh, _ = _euler(L, 0, start, d)
            segments = [(xx[::-1], hh[::-1], name)]
        return dict(kind=kind, name=name, bc=bc, segments=segments, jump=None)

    # For steep flow, the conjugate depth of upstream normal flow is the
    # reference tailwater level for a jump at the outlet. This is a simplified
    # rectangular-channel control criterion; the reservoir jet is not solved.
    h2 = _conjugate(hn, d)
    if hd <= h2 + 1e-7:
        name = 'Uniform flow; jump outside channel or free discharge'
        return dict(kind='steep_outside', name=name,
                    bc='Upstream: h(0) = h_0',
                    segments=[(x, np.full_like(x, hn), 'Uniform flow')], jump=None,
                    h2=h2)
    xx, hh, found = _euler(L, 0, hd, d, target=h2)
    if found:
        xj = float(xx[-1])
        return dict(kind='steep_inside', name='Uniform flow → hydraulic jump → S1',
                    bc='Upstream: h(0) = h_0; downstream: h(L) = H_D',
                    segments=[(np.linspace(0, xj, 251), np.full(251, hn), 'Uniform flow'),
                              (xx[::-1], hh[::-1], 'S1')],
                    jump=(xj, hn, h2), h2=h2)
    return dict(kind='steep_upstream', name='Tailwater influence reaches upstream boundary',
                bc='Upstream supercritical boundary incompatible with an internal jump in this 100 m reach',
                segments=[(x, np.full_like(x, hn), 'Uniform flow')],
                jump=None, h2=h2)


def _make_case():
    rng = random.SystemRandom()
    for _ in range(500):
        b = round(rng.uniform(3.5, 7), 1)
        ks = float(rng.choice([40, 50, 60, 70, 80]))
        hc_target = rng.uniform(0.75, 1.25)
        q = round(b*math.sqrt(G*hc_target**3), 2)
        hc = (q*q/(G*b*b))**(1/3)
        ac = b*hc
        rc = ac/(b+2*hc)
        sc = (q/(ks*ac*rc**(2/3)))**2
        steep = rng.choice([False, True])
        slope = round(sc*rng.uniform(1.7, 2.7) if steep else sc*rng.uniform(0.30, 0.65), 6)
        if slope <= 0:
            continue
        hn = _normal_depth(q, b, ks, slope)
        d = dict(Q=q, B=b, Ks=ks, S0=slope, Hd=0, hc=hc, h0=hn, Sc=sc)
        if steep:
            h2 = _conjugate(hn, d)
            scenario = rng.choice(['free', 'outside', 'inside'])
            if scenario == 'free':
                hd = rng.uniform(0.35, 0.7)*hc
            elif scenario == 'outside':
                hd = rng.uniform(0.85, 0.97)*h2
            else:
                # Choose a valid jump position then derive its downstream level
                # by forward integration from the conjugate depth.
                xj = rng.uniform(25, 70)
                xx, hh, _ = _euler(xj, L, h2, d)
                if xx[-1] < L-1e-6:
                    continue
                hd = hh[-1]
        else:
            scenario = rng.choice(['m1', 'm2', 'uniform', 'free'])
            if scenario == 'm1':
                hd = hn*rng.uniform(1.12, 1.32)
            elif scenario == 'm2':
                hd = hc + rng.uniform(0.35, 0.65)*(hn-hc)
            elif scenario == 'uniform':
                hd = hn
            else:
                hd = 0.65*hc
        d['Hd'] = float(hd) if scenario == 'uniform' else round(float(hd), 4)
        # Uniform case requires exact equality after rounding.
        try:
            result = _solve(d)
        except (ValueError, ArithmeticError):
            continue
        if result['kind'] == 'steep_upstream':
            continue
        d['result'] = result
        return d
    raise RuntimeError('Could not generate a valid exercise')


def _plot(d):
    r = d['result']
    s0, hn, hc, hd = d['S0'], d['h0'], d['hc'], d['Hd']
    bed = lambda x: -s0*np.asarray(x)
    x = np.linspace(0, L, 501)
    fig = go.Figure()
    for label, y, color, dash, width in [
        ('Channel bed', bed(x), '#9a6737', 'solid', 4),
        ('Critical depth h_c', bed(x)+hc, '#dc2626', 'dash', 2),
        ('Normal depth h₀', bed(x)+hn, '#16a34a', 'dot', 2),
    ]:
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=label,
                                 line=dict(color=color, dash=dash, width=width)))
    for i, (xx, hh, label) in enumerate(r['segments']):
        fig.add_trace(go.Scatter(x=xx, y=bed(xx)+hh, mode='lines',
                                 name='Computed water surface' if i == 0 else 'Post-jump GVF',
                                 line=dict(color='#0284c7', width=4)))
        order = np.argsort(xx)
        xx2, hh2 = np.asarray(xx)[order], np.asarray(hh)[order]
        frac = 0.40 if i == 0 else 0.60
        px = float(xx2[0]+frac*(xx2[-1]-xx2[0]))
        py = float(bed(px)+np.interp(px, xx2, hh2))
        fig.add_annotation(x=px, y=py, text=f'<b>{label}</b>', showarrow=False,
                           yshift=17, font=dict(color='#0284c7', size=15),
                           bgcolor='rgba(255,255,255,0.9)')
    if r['jump']:
        xj, h1, h2 = r['jump']
        fig.add_trace(go.Scatter(x=[xj, xj], y=[bed(xj)+h1, bed(xj)+h2],
                                 mode='lines', name='Hydraulic jump',
                                 line=dict(color='#0284c7', width=4)))
    outlet = float(bed(L))
    bottom = outlet-0.65
    fig.add_trace(go.Scatter(x=[L, L, 132], y=[outlet, bottom, bottom],
                             mode='lines', showlegend=False,
                             line=dict(color='#9a6737', width=5)))
    fig.add_trace(go.Scatter(x=[L, 132], y=[outlet+hd, outlet+hd],
                             mode='lines', name='Reservoir level H_D',
                             line=dict(color='#2563eb', width=2, dash='dash')))
    # Dimension H_D: full-length arrows and numerical value beside the line.
    for y, ay in [(outlet+hd, outlet), (outlet, outlet+hd)]:
        fig.add_annotation(x=119, y=y, ax=119, ay=ay, xref='x', yref='y',
                           axref='x', ayref='y', text='', showarrow=True,
                           arrowhead=2, arrowsize=1.2, arrowwidth=2,
                           arrowcolor='#344054')
    fig.add_annotation(x=121, y=outlet+hd/2, text=f'H<sub>D</sub> = {hd:.2f} m',
                       showarrow=False, xanchor='left',
                       font=dict(size=13, color='#344054'),
                       bgcolor='rgba(255,255,255,0.9)')
    if r['kind'].startswith('mild'):
        by = outlet + (hc+0.001 if r['kind']=='mild_free' else
                       (hn if r['kind']=='mild_uniform' else hd))
        boundaries = [(L, by, 'Outlet critical control' if r['kind']=='mild_free' else 'Downstream BC')]
    else:
        boundaries = [(0, hn, 'Upstream BC')]
        if r['kind']=='steep_inside':
            boundaries.append((L, outlet+hd, 'Downstream BC'))
    for bx, by, label in boundaries:
        fig.add_trace(go.Scatter(x=[bx], y=[by], mode='markers', showlegend=False,
                                 marker=dict(symbol='circle-open', size=17,
                                             color='#dc2626', line=dict(width=3))))
        fig.add_annotation(x=bx, y=by, text=label, showarrow=True,
                           ax=-85 if bx == L else 85, ay=-55,
                           arrowhead=2, arrowcolor='#344054',
                           font=dict(size=12, color='#344054'),
                           bgcolor='rgba(255,255,255,0.9)')
    slope_y = float(bed(60))-0.60
    fig.add_annotation(x=60, y=slope_y,
                       text='MILD SLOPE' if hn > hc else 'STEEP SLOPE',
                       showarrow=False, font=dict(color='#9a6737', size=14))
    high = max([float(np.max(bed(xx)+hh)) for xx, hh, _ in r['segments']] +
               [hn, hc, outlet+hd])
    fig.update_layout(template='plotly_white', height=440,
                      title='Outflow into a reservoir — '+r['name'],
                      margin=dict(l=25, r=15, t=50, b=80),
                      xaxis_title='Distance x (m)', yaxis_title='Elevation z (m)',
                      legend=dict(orientation='h', y=-0.30),
                      xaxis=dict(range=[-3, 148]),
                      yaxis=dict(range=[min(bottom-0.3, slope_y-0.35), high+0.8]))
    return fig


def render():
    st.header('Exercise — Outflow into a Reservoir')
    st.caption('One problem · Classify slope · Determine boundary conditions · Identify profiles')
    key = 'm07_outflow_exercise_v1'
    if key not in st.session_state:
        st.session_state[key] = _make_case()
    if st.button('Generate new exercise', type='primary', key='m07_outflow_generate'):
        st.session_state[key] = _make_case()
    d = st.session_state[key]
    st.markdown('A long, prismatic rectangular channel discharges into a large reservoir. '
                'Assume steady flow, a negligible reservoir velocity, and the idealized '
                'outlet conditions described in the theory. '
                '**The channel length is fixed at L = 100 m.**')
    st.markdown('**Given data**')
    st.latex(rf'Q={d["Q"]:.2f}\ \mathrm{{m^3/s}},\quad B={d["B"]:.1f}\ \mathrm{{m}},\quad '
             rf'K_s={d["Ks"]:.0f}\ \mathrm{{m^{{1/3}}/s}}')
    st.latex(rf'S_0={d["S0"]:.6f},\qquad H_D={d["Hd"]:.4f}\ \mathrm{{m}},\qquad '
             r'L=100\ \mathrm{m}')
    st.markdown('**Required**\n\n'
                '1. Calculate the critical depth $h_c$ and normal depth $h_0$; '
                'classify the bed slope as **mild** or **steep**.\n'
                '2. Identify the **hydraulic boundary condition(s)** and the control section(s).\n'
                '3. Identify the **water-surface profile(s)** and determine whether '
                'a hydraulic jump is expected in the channel.')
    with st.expander('Show complete worked solution', expanded=False):
        st.markdown('### 1. Slope classification')
        st.latex(r'h_c=\left(\frac{Q^2}{gB^2}\right)^{1/3}')
        st.latex(r'Q=K_s\,Bh_0\left(\frac{Bh_0}{B+2h_0}\right)^{2/3}\sqrt{S_0}')
        st.latex(rf'h_c={d["hc"]:.4f}\ \mathrm{{m}},\quad '
                 rf'h_0={d["h0"]:.4f}\ \mathrm{{m}}')
        st.latex(rf'S_c={d["Sc"]:.6f},\qquad S_0={d["S0"]:.6f}')
        slope_class = 'Mild' if d['h0'] > d['hc'] else 'Steep'
        st.success(f'{slope_class} slope: '+
                   ('h₀ > h_c and S₀ < S_c.' if slope_class=='Mild' else
                    'h₀ < h_c and S₀ > S_c.'))
        r = d['result']
        st.markdown('### 2. Boundary condition')
        st.write(r['bc'])
        st.markdown('### 3. Water-surface profile')
        st.success(r['name'])
        if r['jump']:
            xj, h1, h2 = r['jump']
            st.latex(r'M(h_1)=M(h_2),\qquad '
                     r'h_2=\frac{h_1}{2}\left(\sqrt{1+8Fr_1^2}-1\right)')
            st.write(f'Conjugate depths: h₁ = {h1:.4f} m, h₂ = {h2:.4f} m. '
                     f'The jump is located at x_j = {xj:.2f} m from the upstream end.')
        elif r['kind']=='steep_outside':
            st.write(f'The conjugate depth of upstream uniform flow is '
                     f'{r["h2"]:.4f} m. The tailwater is not sufficient to '
                     'force a hydraulic jump inside the channel under the idealized model.')
        st.markdown('### Computed longitudinal profile')
        st.plotly_chart(_plot(d), use_container_width=True)
        st.caption('The channel water surface is calculated using the Module 04 '
                   'adaptive-step explicit Euler GVF method. A hydraulic jump is '
                   'matched by specific force and shown as a 1-D discontinuity. '
                   'The reservoir jet and any jump beyond the outlet are not resolved.')
