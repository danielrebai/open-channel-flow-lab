"""Module 06 — Intake from Reservoir: one exercise, two competing hypotheses.

Steady rectangular channel, negligible entrance losses, alpha=1.
Both mild and steep hypotheses are solved and checked for consistency.
"""
import math
import random

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy.optimize import brentq

G = 9.81


def area(y, b):
    return b * y


def radius(y, b):
    return b * y / (b + 2 * y)


def discharge_uniform(y, b, ks, slope):
    return ks * area(y, b) * radius(y, b) ** (2 / 3) * math.sqrt(slope)


def normal_depth(q, b, ks, slope):
    lo, hi = 0.0, 1.0
    while discharge_uniform(hi, b, ks, slope) < q:
        hi *= 2
    for _ in range(90):
        mid = (lo + hi) / 2
        if discharge_uniform(mid, b, ks, slope) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def critical_depth(q, b):
    return (q * q / (G * b * b)) ** (1 / 3)


def critical_slope(q, b, ks):
    k = critical_depth(q, b)
    return (q / (ks * area(k, b) * radius(k, b) ** (2 / 3))) ** 2


def specific_energy(y, q, b):
    return y + q * q / (2 * G * (b * y) ** 2)


def solve_hypotheses(H0, slope, ks, b):
    """Solve both candidate closures; verify slope class independently."""
    # Steep assumption: critical section at intake, H0=3k/2.
    k_s = 2 * H0 / 3
    q_s = b * math.sqrt(G * k_s ** 3)
    h0_s = normal_depth(q_s, b, ks, slope)
    sc_s = critical_slope(q_s, b, ks)
    steep_ok = (h0_s < k_s and slope > sc_s)

    # Mild assumption: uniform at intake and downstream, with H0=E(h0).
    # Restrict to the SUBCRITICAL energy branch: h0 in (2H0/3, H0).
    # On that branch, the function can be nonmonotone for some inputs;
    # detect every root and retain only a hydraulically mild one.
    def residual(y):
        q = discharge_uniform(y, b, ks, slope)
        return specific_energy(y, q, b) - H0

    ys = np.linspace(2 * H0 / 3 + H0 * 1e-9, H0, 801)
    roots = []
    for a, c in zip(ys[:-1], ys[1:]):
        fa, fc = residual(float(a)), residual(float(c))
        if fa * fc < 0:
            root = brentq(residual, float(a), float(c), xtol=1e-13)
            if not roots or abs(root - roots[-1]) > 1e-8:
                roots.append(root)
    mild_candidates = []
    for h in roots:
        q = discharge_uniform(h, b, ks, slope)
        k = critical_depth(q, b)
        sc = critical_slope(q, b, ks)
        mild_candidates.append(dict(Q=q, h0=h, k=k, Sc=sc,
                                    valid=(h > k and slope < sc)))
    mild = next((r for r in mild_candidates if r['valid']), None)
    if mild is None and mild_candidates:
        mild = mild_candidates[0]

    steep = dict(Q=q_s, h0=h0_s, k=k_s, Sc=sc_s, valid=steep_ok)
    mild_valid = mild is not None and mild['valid']
    if steep_ok == mild_valid:
        raise ValueError('Case does not have exactly one consistent hypothesis')
    return dict(steep=steep, mild=mild, winner='Steep' if steep_ok else 'Mild')


def generate_case():
    rng = random.SystemRandom()
    for _ in range(500):
        H0 = round(rng.uniform(1.5, 3.8), 2)
        b = round(rng.uniform(3.0, 7.0), 1)
        ks = float(rng.choice((40, 50, 60, 70, 80)))
        # Critical slope for the steep candidate sets a useful scale.
        k = 2 * H0 / 3
        q = b * math.sqrt(G * k ** 3)
        sc = critical_slope(q, b, ks)
        factor = rng.uniform(0.18, 0.50) if rng.random() < 0.5 else rng.uniform(1.8, 3.5)
        slope = sc * factor
        try:
            result = solve_hypotheses(H0, slope, ks, b)
            return dict(H0=H0, slope=slope, ks=ks, b=b, result=result)
        except (ValueError, OverflowError, ZeroDivisionError):
            continue
    raise RuntimeError('Unable to generate a hydraulically consistent exercise')


def profile_figure(case):
    """Theory-matched intake diagram using the exercise's computed solution."""
    from .theory import _euler_supercritical
    winner = case['result']['winner']
    steep = winner == 'Steep'
    chosen = case['result'][winner.lower()]
    d = dict(H0=case['H0'], b=case['b'], ks=case['ks'],
             slope=case['slope'], Q=chosen['Q'], yc=chosen['k'], y0=chosen['h0'])
    slope, L, reservoir_level = d['slope'], 90.0, d['H0']
    intake_depth = d['yc'] if steep else d['y0']
    fig = go.Figure()

    wall_x, wall_top = -9.0, -0.60
    t = np.linspace(0.0, 1.0, 120)
    bx = ((1-t)**3 * wall_x + 3*(1-t)**2*t*wall_x
          + 3*(1-t)*t*t*(-4.0) + t**3*0.0)
    by = ((1-t)**3 * wall_top + 3*(1-t)**2*t*(-0.10)
          + 3*(1-t)*t*t*0.0 + t**3*0.0)
    x_channel = np.linspace(0.0, L, 400)
    bed_channel = -slope*x_channel
    fig.add_trace(go.Scatter(
        x=np.r_[[-30.0, wall_x, wall_x], bx, x_channel[1:]],
        y=np.r_[[-2.2, -2.2, wall_top], by, bed_channel[1:]],
        name='Reservoir wall and channel bed', mode='lines',
        line=dict(color='#93602f', width=5)))

    # The short 3D intake region cannot be resolved by 1D GVF.
    # Keep the requested shaded transition, but do not call it numerical.
    approach_start = -13.0
    xa = np.linspace(approach_start, 0.0, 120)
    u = (xa-approach_start)/(0.0-approach_start)
    smooth = 3*u*u-2*u*u*u
    ya = reservoir_level + (intake_depth-reservoir_level)*smooth
    # Shade the entire plot height over the qualitative intake approach.
    # Plotly vrect uses paper coordinates vertically, so the band always
    # spans the full displayed y-axis range.
    # Full-height rectangular band: y coordinates are paper fractions, not elevations.
    fig.add_shape(
        type='rect', xref='x', yref='paper',
        x0=approach_start, x1=0.0, y0=0, y1=1,
        fillcolor='rgba(8,126,194,0.13)',
        line=dict(width=0), layer='below',
    )
    fig.add_trace(go.Scatter(
        x=[-30.0, approach_start], y=[reservoir_level]*2,
        name='Reservoir water level', mode='lines',
        line=dict(color='#087ec2', width=4)))
    fig.add_trace(go.Scatter(
        x=xa, y=ya, name='Intake approach (qualitative)', mode='lines',
        line=dict(color='#087ec2', width=3, dash='dash')))

    fig.add_trace(go.Scatter(
        x=x_channel, y=bed_channel+d['yc'],
        name=f'Critical depth yc = {d["yc"]:.3f} m', mode='lines',
        line=dict(color='#d62828', dash='dash', width=2)))
    fig.add_trace(go.Scatter(
        x=x_channel, y=bed_channel+d['y0'],
        name=f'Uniform depth y0 = {d["y0"]:.3f} m', mode='lines',
        line=dict(color='#228b50', dash='dash', width=5)))

    if steep:
        xx, yy = _euler_supercritical(d, L)
        fig.add_trace(go.Scatter(
            x=xx, y=-slope*xx+yy,
            name='Computed supercritical GVF (Euler)', mode='lines',
            line=dict(color='#087ec2', width=4)))
        fig.add_trace(go.Scatter(
            x=[0], y=[d['yc']], name='Critical control at intake',
            mode='markers', marker=dict(symbol='circle-open', size=15,
                                        color='#d62828', line=dict(width=3))))
        fig.add_annotation(x=0, y=d['yc'], text='Critical control',
                           showarrow=True, ax=95, ay=-65)
    else:
        # The green dashed line denotes the uniform-flow reference.
        # The blue solid line is the actual water surface, coincident with it.
        fig.add_trace(go.Scatter(
            x=x_channel, y=bed_channel+d['y0'],
            name='Water surface (uniform flow)', mode='lines',
            line=dict(color='#087ec2', width=3)))
        # Downstream boundary y(L)=y0 yields y(x)=y0 identically.
        fig.add_trace(go.Scatter(
            x=[L], y=[bed_channel[-1]+d['y0']],
            name='Downstream uniform-flow boundary', mode='markers',
            marker=dict(symbol='circle-open', size=15,
                        color='#228b50', line=dict(width=3))))
        fig.add_annotation(x=L, y=bed_channel[-1]+d['y0'],
                           text='Downstream control: y(L) = y₀',
                           showarrow=True, ax=-125, ay=-55)

    # Reservoir energy head H0, measured vertically from the intake-bed datum z=0.
    # Two arrowheads emphasize the complete head difference.
    head_x = -24.0
    fig.add_trace(go.Scatter(
        x=[head_x, head_x], y=[0.0, reservoir_level],
        mode='lines', name='Reservoir energy head H₀',
        line=dict(color='#344054', width=2), hoverinfo='skip',
        showlegend=False))
    fig.add_annotation(x=head_x, y=reservoir_level, ax=head_x, ay=0.0,
                       xref='x', yref='y', axref='x', ayref='y',
                       text='', showarrow=True, arrowhead=2,
                       arrowsize=1.2, arrowwidth=2, arrowcolor='#344054')
    fig.add_annotation(x=head_x, y=0.0, ax=head_x, ay=reservoir_level,
                       xref='x', yref='y', axref='x', ayref='y',
                       text='', showarrow=True, arrowhead=2,
                       arrowsize=1.2, arrowwidth=2, arrowcolor='#344054')
    fig.add_annotation(x=head_x+1.2, y=reservoir_level/2,
                       text=f'H₀ = {reservoir_level:.2f} m',
                       showarrow=False, xanchor='left',
                       font=dict(size=13, color='#344054'),
                       bgcolor='rgba(255,255,255,0.8)')

    fig.add_annotation(x=-20, y=reservoir_level+0.23,
                       text='Reservoir: V ≈ 0', showarrow=False)
    fig.add_annotation(x=-5.8, y=reservoir_level+0.42,
                       text='Qualitative!', showarrow=False,
                       font=dict(color='#087ec2', size=11))
    fig.add_annotation(x=45, y=-slope*45-0.65,
                       text='STEEP SLOPE' if steep else 'MILD SLOPE',
                       showarrow=False, font=dict(color='#875022', size=13))
    fig.update_layout(
        title='Reservoir intake — steep channel' if steep else 'Reservoir intake — mild channel',
        xaxis_title='Longitudinal coordinate x (m)',
        yaxis_title='Elevation (m)', template='plotly_white', height=460,
        margin=dict(l=25, r=25, t=65, b=85),
        legend=dict(orientation='h', y=-0.27),
    )
    fig.update_yaxes(range=[min(-2.5, -slope*L-1.1), reservoir_level+0.8])
    return fig


def render():
    st.header('Exercise — Intake from Reservoir')
    st.caption('One problem · Test both hydraulic hypotheses · Rectangular channel')
    key = 'm06_intake_exercise_v1'
    if key not in st.session_state:
        st.session_state[key] = generate_case()
    if st.button('Generate new exercise', type='primary', key='m06_intake_generate'):
        st.session_state[key] = generate_case()
    d = st.session_state[key]
    st.markdown('A large reservoir supplies a long, prismatic rectangular channel. '
                'Neglect entrance energy losses and assume the velocity in the '
                'reservoir is negligible. The downstream boundary is free from backwater effects.')
    st.markdown('**Given data**')
    st.latex(rf'H_0={d["H0"]:.2f}\ \mathrm{{m}},\qquad i={d["slope"]:.6g}')
    st.latex(rf'K_s={d["ks"]:.0f}\ \mathrm{{m^{{1/3}}/s}},\qquad B={d["b"]:.1f}\ \mathrm{{m}}')
    st.markdown('**Required**\n\n'
                '1. **Test both hypotheses**, mild and steep. For each, calculate '
                'the discharge and relevant depths, then verify whether the '
                'computed normal and critical depths (and critical slope) actually '
                'support the assumed classification. **Only one hypothesis is admissible.**\n'
                '2. For the physically admissible solution, determine the discharge '
                r'$Q$, normal depth $h_0$, critical depth $k$, and water depth at '
                'the first channel section, $h(0)$.')

    with st.expander('Show complete worked solution', expanded=False):
        r = d['result']
        st.markdown('### Hypothesis 1 — Steep channel')
        st.markdown('Assume the intake is a critical control. From the reservoir energy equation:')
        st.latex(r'H_0=k+\frac{Q^2}{2gB^2k^2}=\frac{3}{2}k,\qquad '
                 r'k=\frac{2H_0}{3},\qquad Q=B\sqrt{gk^3}')
        s = r['steep']
        st.write(f"Candidate: Q = {s['Q']:.4f} m³/s; k = {s['k']:.4f} m; "
                 f"h₀ = {s['h0']:.4f} m; critical slope = {s['Sc']:.6g}.")
        st.latex(r'\mathrm{Steep\ check:}\quad h_0<k\quad\mathrm{and}\quad i>i_c')
        st.success('Steep hypothesis: consistent') if s['valid'] else st.error('Steep hypothesis: inconsistent')

        st.markdown('### Hypothesis 2 — Mild channel')
        st.markdown('Assume the channel carries uniform flow to the intake. '
                    'Combine reservoir energy with the full-radius Strickler equation:')
        st.latex(r'H_0=h_0+\frac{Q^2}{2gB^2h_0^2}')
        st.latex(r'Q=K_s\,Bh_0\left(\frac{Bh_0}{B+2h_0}\right)^{2/3}\sqrt{i}')
        m = r['mild']
        if m is None:
            st.write('No admissible subcritical-branch root exists for the mild closure.')
            st.error('Mild hypothesis: inconsistent')
        else:
            st.write(f"Candidate: Q = {m['Q']:.4f} m³/s; h₀ = {m['h0']:.4f} m; "
                     f"k = {m['k']:.4f} m; critical slope = {m['Sc']:.6g}.")
            st.latex(r'\mathrm{Mild\ check:}\quad h_0>k\quad\mathrm{and}\quad i<i_c')
            st.success('Mild hypothesis: consistent') if m['valid'] else st.error('Mild hypothesis: inconsistent')

        winner = r['winner']
        chosen = r[winner.lower()]
        st.markdown('### Physically admissible solution')
        st.success(f'{winner} slope — only this hypothesis satisfies its classification checks.')
        first = chosen['k'] if winner == 'Steep' else chosen['h0']
        st.latex(rf'Q={chosen["Q"]:.4f}\ \mathrm{{m^3/s}},\quad '
                 rf'h_0={chosen["h0"]:.4f}\ \mathrm{{m}},\quad '
                 rf'k={chosen["k"]:.4f}\ \mathrm{{m}}')
        st.latex(rf'h(0)={first:.4f}\ \mathrm{{m}}')
        st.markdown('The first section is **critical** for the steep solution '
                    'and **uniform** for the mild solution.')
        st.plotly_chart(profile_figure(d), use_container_width=True)
