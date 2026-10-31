"""Intake from Reservoir — Theory.

Based on the two-page lecture note 'Intake from Reservoir'.
Channel depths are computed from energy, Strickler resistance and Euler GVF.
"""

import math
from scipy.optimize import brentq
import numpy as np
import plotly.graph_objects as go
import streamlit as st


G = 9.81


def _area(y, width):
    return width * y


def _radius(y, width):
    return width * y / (width + 2.0 * y)


def _friction(y, discharge, width, ks):
    return (discharge / (ks * _area(y, width) * _radius(y, width) ** (2.0 / 3.0))) ** 2


def _solve_hydraulics(steep):
    # Numerical example, SI units; energy coefficient alpha=1.
    H0, width, ks = 2.4, 4.0, 65.0
    slope = 0.018 if steep else 0.0004
    if steep:
        yc = 2.0 * H0 / 3.0
        discharge = width * math.sqrt(G * yc ** 3)
        y0 = brentq(lambda y: _friction(y, discharge, width, ks) - slope, 0.01, 30.0)
    else:
        # Solve the reservoir energy equation and the Strickler equation together.
        def q_uniform(y):
            return ks * _area(y, width) * _radius(y, width) ** (2.0 / 3.0) * math.sqrt(slope)
        def energy_residual(y):
            q = q_uniform(y)
            return y + q*q / (2*G*_area(y, width)**2) - H0
        y0 = brentq(energy_residual, 0.01, H0)
        discharge = q_uniform(y0)
        yc = (discharge**2/(G*width**2))**(1/3)
    sc = _friction(yc, discharge, width, ks)
    if steep and not (y0 < yc and slope > sc):
        raise ValueError('Steep example is not supercritical at normal flow')
    if not steep and not (y0 > yc and slope < sc):
        raise ValueError('Mild example is not subcritical at normal flow')
    return dict(H0=H0, b=width, ks=ks, slope=slope, Q=discharge,
                yc=yc, y0=y0, Sc=sc)


def _euler_supercritical(d, length=90.0, dx_max=0.10):
    # Spatial Euler, as in the GVF module; start just below the critical depth.
    x, y = 0.0, d['yc'] * (1.0 - 0.002)
    xs, ys = [x], [y]
    while x < length - 1e-10:
        fr2 = d['Q']**2 / (G * d['b']**2 * y**3)
        dydx = (d['slope'] - _friction(y, d['Q'], d['b'], d['ks'])) / (1.0 - fr2)
        if not math.isfinite(dydx):
            raise ValueError('Non-finite GVF derivative')
        step = min(dx_max, length - x)
        if abs(dydx) > 0:
            step = min(step, 0.05*y/abs(dydx))
            if dydx > 0:
                step = min(step, 0.40*(d['yc']-y)/abs(dydx))
        if step < 1e-7:
            break
        ynext = y + step*dydx
        if ynext <= 0 or ynext >= d['yc']*(1.0-1e-6):
            break
        x, y = x + step, ynext
        xs.append(x)
        ys.append(y)
    return np.asarray(xs), np.asarray(ys)


def _schematic(steep: bool) -> go.Figure:
    """Numerical channel solution; shaded reservoir approach is illustrative."""
    d = _solve_hydraulics(steep)
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
    st.header('Theory — Intake from Reservoir')
    st.caption('Reservoir-to-channel transition · Critical control · Uniform-flow control')

    st.markdown('### 1. Physical setting and assumptions')
    st.markdown(
        'Consider a large reservoir feeding a prismatic open channel. The reservoir '
        'velocity is negligible, so its free-surface elevation defines the available '
        'upstream energy. Let the intake section be **section 1** and let '
        r'$H_0$ denote the reservoir water level above the channel bed at that section.'
    )
    st.markdown(
        'We assume steady flow, a hydrostatic pressure distribution in the channel '
        'sections, and **negligible entrance energy losses**, as in the lecture notes. '
        'The energy coefficient is denoted by $\\alpha$.'
    )
    st.latex(r'H_0=E_1=h+\alpha\frac{Q^2}{2gA(h)^2}')
    st.markdown(
        'Here $h$ is the water depth at the intake, $Q$ the discharge, '
        '$A(h)$ the wetted cross-sectional area and $g$ gravitational acceleration. '
        'This equation alone has **two unknowns**, $Q$ and $h$; a second hydraulic '
        'condition is required.'
    )
    st.info(
        'The channel curves use numerical hydraulic states (SI units): steep-flow GVF is integrated '
        'with explicit spatial Euler, while mild-flow depth is the uniform-flow solution. '
        'Only the qualitative reservoir-to-intake approach remains illustrative: a 1D GVF '
        'model cannot resolve its rapidly varied, three-dimensional flow.'
    )

    st.markdown('### 2. Steep channel — critical control at the intake')
    ds = _solve_hydraulics(True)
    st.caption(f'Numerical example: H₀={ds["H0"]:.2f} m · b={ds["b"]:.2f} m · Kₛ={ds["ks"]:.1f} m¹ᐟ³/s · S₀={ds["slope"]:.5f} · Q={ds["Q"]:.3f} m³/s · yc={ds["yc"]:.3f} m · y₀={ds["y0"]:.3f} m')
    st.plotly_chart(_schematic(True), use_container_width=True)
    st.markdown(
        'For a sufficiently steep channel, the flow downstream of the entrance is '
        'supercritical. The reservoir is subcritical, so the transition must pass '
        'through a **critical section** at the intake (section 1), under the idealized '
        'conditions shown in the notes.'
    )
    st.latex(r'\begin{cases}H_0=h_c+\alpha\dfrac{Q^2}{2gA(h_c)^2}\\[6pt]'
             r'\dfrac{A(h_c)^3}{B(h_c)}=\dfrac{\alpha Q^2}{g}\end{cases}')
    st.markdown(
        'Here $B(h)$ is the free-surface width. The second equation is the '
        'critical-flow condition (for a constant energy coefficient $\\alpha$). '
        'Together the two equations determine **$Q$ and $h_c$**.'
    )
    st.markdown('For a rectangular channel of width $b$, with $\\alpha=1$:')
    st.latex(r'A=bh,\qquad B=b,\qquad h_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}')
    st.latex(r'H_0=\frac{3}{2}h_c,\qquad h_c=\frac{2H_0}{3},\qquad '
             r'Q=b\sqrt{g\left(\frac{2H_0}{3}\right)^3}')
    st.caption('The explicit rectangular-channel result assumes α = 1 and negligible entrance losses.')

    st.markdown('### 3. Mild channel — downstream uniform-flow control')
    dm = _solve_hydraulics(False)
    st.caption(f'Numerical example: H₀={dm["H0"]:.2f} m · b={dm["b"]:.2f} m · Kₛ={dm["ks"]:.1f} m¹ᐟ³/s · S₀={dm["slope"]:.5f} · Q={dm["Q"]:.3f} m³/s · yc={dm["yc"]:.3f} m · y₀={dm["y0"]:.3f} m')
    st.plotly_chart(_schematic(False), use_container_width=True)
    st.markdown(
        'For a mild channel, the downstream flow is subcritical. The lecture notes '
        'consider a sufficiently long channel with **no downstream backwater influence**. '
        'The boundary condition is imposed **at the downstream end**, where the depth equals the normal depth $h_0$. '
        'Under these assumptions, **uniform flow extends up to the intake**, so '
        r'$h(x)=h_0$ throughout the channel. Integrating the GVF equation upstream from $h(L)=h_0$ yields $dh/dx=0$ because $S_f(h_0)=S_0$. There is **no M2 profile**.'
    )
    st.latex(r'h(L)=h_0,\qquad S_f(h_0)=S_0\quad\Longrightarrow\quad h(x)=h_0')
    st.latex(r'\begin{cases}H_0=h_0+\alpha\dfrac{Q^2}{2gA(h_0)^2}\\[6pt]'
             r'Q=K_sA(h_0)R(h_0)^{2/3}\sqrt{S_0}\end{cases}')
    st.markdown(
        'The first equation is the energy relation used in the lecture notes; '
        'the second is the **Gauckler–Strickler uniform-flow equation**. '
        'They are solved together for **$Q$ and $h_0$**.'
    )
    st.markdown('For a rectangular channel, use the **full hydraulic radius**, consistent with Module 04:')
    st.latex(r'A(h_0)=bh_0,\qquad R(h_0)=\frac{bh_0}{b+2h_0}')
    st.latex(r'Q=K_sbh_0\left(\frac{bh_0}{b+2h_0}\right)^{2/3}\sqrt{S_0}')
    st.markdown(
        'The wide-channel approximation is **not** used in the primary calculation. '
        'For a specified $H_0$, $b$, $K_s$ and $S_0$, the coupled equations '
        'can be solved numerically.'
    )

    st.markdown('### 4. Selecting the hydraulic model')
    st.markdown(
        'The choice between these two models depends on the actual flow regime '
        'and the available control. In the steep case the entrance critical section '
        'controls the discharge; in the mild case the idealized downstream uniform '
        'state controls it. The reservoir energy equation by itself is insufficient.'
    )
    st.markdown(
        '**Scope of this theory:** channel depths and the steep-channel GVF are computed. '
        'The qualitative approach at the intake is illustrative only. Entrance losses, '
        'finite-length effects and downstream submergence are not included.'
    )
