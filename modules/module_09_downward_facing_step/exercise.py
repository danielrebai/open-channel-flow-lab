"""Module 09 — generated exercise with a single worked solution."""
import random

import streamlit as st
import plotly.graph_objects as go

from .hydraulics import critical, normal, energy, force
from .theory import (EXAMPLES, calculate, profile_plot, energy_plot,
                     momentum_plot, insufficient_energy_precheck_plot)

G = 9.81
S_STEEP = 0.018
S_MILD = 0.0005
_CASES = tuple(EXAMPLES)


def _slopes(case):
    return (S_STEEP if case.startswith('steep') else S_MILD,
            S_STEEP if case in ('steep_steep', 'mild_steep') else S_MILD)


def _boundary_text(case):
    return {
        'steep_steep': 'Upstream uniform supercritical flow: h_U = hₙ,U.',
        'mild_mild_sufficient': 'Downstream uniform subcritical flow: h_D = hₙ,D.',
        'mild_mild_insufficient': ('Downstream uniform subcritical flow: h_D = hₙ,D. '
                                   'The assumed upstream energy is insufficient; '
                                   'critical control and an upstream M2 profile are required.'),
        'mild_steep': ('Critical control at the upstream edge of the step: '
                       'h_U = h_c. Integrate the M2 profile upstream from just above h_c.'),
        'steep_mild': ('Two external controls: upstream uniform supercritical flow '
                        'h_U = hₙ,U and downstream uniform subcritical flow h_D = hₙ,D.'),
    }[case]


def _make_exercise():
    """Randomize given data without altering the calibrated hydraulic scenarios.

    For a rectangular channel the solver depends on unit discharge q=Q/B.
    Randomizing B and Q together gives genuinely different supplied Q and B
    while preserving the validated hydraulic regime and jump matching.
    """
    case = random.choice(_CASES)
    p = dict(EXAMPLES[case])
    p['b'] = round(random.uniform(2.5, 7.5), 2)
    return {'case': case, 'params': p}



def _bed_geometry_plot(Su, Sd, a, L):
    """Show only the assigned channel geometry, without solution information."""
    x = [-L, 0.0, 0.0, L]
    z = [Su * L, 0.0, -a, -a - Sd * L]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=z, mode='lines', name='Channel bed',
        line=dict(color='#A66308', width=5), hovertemplate='x=%{x:.2f} m<br>z=%{y:.3f} m<extra></extra>'))
    fig.add_annotation(x=-0.5 * L, y=0.5 * Su * L, text='Upstream reach',
                       showarrow=False, yshift=-28, font=dict(color='#A66308', size=13))
    fig.add_annotation(x=0.5 * L, y=-a - 0.5 * Sd * L, text='Downstream reach',
                       showarrow=False, yshift=-28, font=dict(color='#A66308', size=13))
    fig.add_annotation(x=0, y=-0.5 * a, text=f'a = {a:.2f} m',
                       showarrow=True, ax=65, ay=0, arrowhead=2, font=dict(size=13))
    fig.update_layout(
        template='plotly_white', height=390, showlegend=False,
        margin=dict(l=55, r=35, t=35, b=55),
        xaxis=dict(title='Longitudinal coordinate x [m]', zeroline=False),
        yaxis=dict(title='Bed elevation z [m]', zeroline=False),
        hovermode='closest')
    return fig

def render():
    st.subheader('Exercise · Downward Facing Step')
    key = 'm09_generated_exercise_v2'
    if key not in st.session_state:
        st.session_state[key] = _make_exercise()
    if st.button('Generate new exercise', type='primary', key='m09_generate'):
        st.session_state[key] = _make_exercise()

    exercise = st.session_state[key]
    case, p = exercise['case'], exercise['params']
    Q, B, n, a, L = p['q'] * p['b'], p['b'], p['n'], p['a'], p['length']
    Su, Sd = _slopes(case)
    q = Q / B

    st.markdown('A rectangular channel has a downward-facing step. '
                'Assume steady one-dimensional flow and Manning resistance. '
                'Determine the hydraulic regime and water-surface profile from the data below.')
    st.markdown('**Given data**')
    st.latex(rf'Q={Q:.3f}\ \mathrm{{m^3/s}},\quad B={B:.2f}\ \mathrm{{m}},\quad n={n:.3f}')
    st.latex(rf'S_{{0,U}}={Su:.5f},\quad S_{{0,D}}={Sd:.5f},\quad '
             rf'a={a:.2f}\ \mathrm{{m}},\quad L_U=L_D={L:.0f}\ \mathrm{{m}}')
    st.plotly_chart(_bed_geometry_plot(Su, Sd, a, L), use_container_width=True,
                    key='m09_ex_bed_geometry')

    st.markdown('**Required**')
    st.markdown('1. Compute the normal depths $h_{n,U}$, $h_{n,D}$ and critical depth $h_c$.\n'
                '2. Classify the upstream and downstream slopes.\n'
                '3. Identify the boundary conditions and hydraulic controls.\n'
                '4. Determine the steady water-surface profiles and explain the step '
                'transition using the specific-energy diagram.\n'
                '5. Determine whether a hydraulic jump occurs and, if so, calculate its position.')

    with st.expander('Show worked solution', expanded=False):
        hc = critical(q)
        hnu = normal(q, B, n, Su)
        hnd = normal(q, B, n, Sd)
        st.markdown('### 1. Normal and critical depths')
        st.latex(r'q=\frac{Q}{B},\qquad h_c=\left(\frac{q^2}{g}\right)^{1/3}')
        st.latex(r'Q=\frac{1}{n}A(h_n)R(h_n)^{2/3}\sqrt{S_0},\quad '
                 r'A=Bh,\quad R=\frac{Bh}{B+2h}')
        st.latex(rf'q={q:.4f}\ \mathrm{{m^2/s}},\quad h_c={hc:.4f}\ \mathrm{{m}}')
        st.latex(rf'h_{{n,U}}={hnu:.4f}\ \mathrm{{m}},\quad '
                 rf'h_{{n,D}}={hnd:.4f}\ \mathrm{{m}}')

        st.markdown('### 2. Slope classification')
        for label, hn in [('Upstream', hnu), ('Downstream', hnd)]:
            kind = 'Mild' if hn > hc else 'Steep' if hn < hc else 'Critical'
            sign = '>' if hn > hc else '<' if hn < hc else '='
            st.markdown(f'**{label}: {kind}** — hₙ = {hn:.4f} m {sign} h_c = {hc:.4f} m.')

        st.markdown('### 3. Boundary conditions')
        st.write(_boundary_text(case))

        st.markdown('### 4. Steady profiles and step energy balance')
        st.latex(r'\frac{dh}{dx}=\frac{S_0-S_f}{1-Fr^2},\qquad '
                 r'E(h)=h+\frac{q^2}{2gh^2},\qquad E_D=E_U+a')
        st.write('Integrate each GVF branch from its controlling boundary. '
                 'At the step, use the energy balance and choose the physically '
                 'admissible root on the appropriate flow branch.')
        try:
            data = calculate(case, **p)
            if case == 'mild_mild_insufficient':
                st.markdown('**Preliminary energy-feasibility check**')
                st.plotly_chart(insufficient_energy_precheck_plot(data),
                                use_container_width=True, key='m09_ex_precheck')
                st.write('The trial upstream energy falls below the critical minimum; '
                         'the assumed state cannot pass the step without adjustment.')
            st.markdown('**Integrated longitudinal profile**')
            st.plotly_chart(profile_plot(data), use_container_width=True,
                            key='m09_ex_profile')
            st.markdown('**Specific energy**')
            st.plotly_chart(energy_plot(data), use_container_width=True,
                            key='m09_ex_energy')

            st.markdown('### 5. Hydraulic jumps')
            st.latex(r'M(h)=\frac{h^2}{2}+\frac{q^2}{gh},\qquad M(h_1)=M(h_2)')
            if data['jumps']:
                for xj, h1, h2 in data['jumps']:
                    st.write(f'Hydraulic jump at x = {xj:.2f} m downstream of the step. '
                             f'Conjugate depths: h₁ = {h1:.4f} m, h₂ = {h2:.4f} m. '
                             f'Specific forces: M₁ = {force(h1,q):.4f} m², '
                             f'M₂ = {force(h2,q):.4f} m².')
                st.plotly_chart(momentum_plot(data), use_container_width=True,
                                key='m09_ex_momentum')
            else:
                st.write('No momentum-compatible hydraulic jump was located within '
                         'the modeled reaches for these boundary conditions.')
            for warning in data['warnings']:
                st.warning(warning)
        except (ValueError, ArithmeticError, RuntimeError) as exc:
            st.warning(f'The numerical profile could not be completed: {exc}')
