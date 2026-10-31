"""Module 07: computed gradually varied flow profiles for a rectangular channel.

Illustrative, explicitly specified hydraulic parameters; local outlet jet and
finite-length hydraulic jump are outside the one-dimensional GVF model.
"""
from pathlib import Path
import re
import numpy as np
from scipy.optimize import brentq
import plotly.graph_objects as go
import streamlit as st

HERE = Path(__file__).resolve().parent
G = 9.81
B = 5.0
HC = 1.0
Q = B * np.sqrt(G * HC**3)  # makes critical depth exactly 1 m
L = 100.0


def _hydraulics(steep):
    s0 = 0.013 if steep else 0.003
    hn = 0.62 if steep else 1.48
    area = B * hn
    radius = area / (B + 2 * hn)
    ks = Q / (area * radius ** (2 / 3) * np.sqrt(s0))
    return s0, hn, ks


def _sf(h, ks):
    a = B * h
    r = a / (B + 2 * h)
    return (Q / (ks * a * r ** (2 / 3))) ** 2


def _fr2(h):
    return Q**2 / (G * B**2 * h**3)


def _rhs(h, s0, ks):
    """GVF depth gradient, as used in Module 04."""
    if h <= 0 or abs(1.0 - _fr2(h)) < 1e-10:
        raise ValueError('Invalid depth or critical-flow singularity')
    return (s0 - _sf(h, ks)) / (1.0 - _fr2(h))


def _integrate(x_start, x_end, h_start, s0, ks, target=None):
    """Module 04 method: adaptive spatial-step, first-order explicit Euler.

    Upstream integration uses a negative signed step; downstream a positive
    step. Stop rather than crossing critical depth. Optionally stop at a
    specified conjugate depth, interpolating within the final Euler step.
    """
    direction = 1 if x_end > x_start else -1
    x, h = float(x_start), float(h_start)
    xs, hs = [x], [h]
    critical_tol = max(0.003, 0.005 * HC)
    for _ in range(30000):
        remaining = abs(x_end - x)
        if remaining < 1e-9:
            break
        f = _rhs(h, s0, ks)
        # Same relative-depth and near-critical limits as Module 04.
        dx = min(remaining, (1.0 if h > HC else 0.5) * h)
        if abs(f) > 1e-12:
            dx = min(dx, 0.025 * max(h, 0.05) / abs(f))
            if abs(h - HC) > critical_tol:
                dx = min(dx, 0.25 * abs(h - HC) / abs(f))
        if dx < 1e-8:
            break
        for _attempt in range(35):
            next_h = h + direction * f * dx  # explicit Euler
            if (np.isfinite(next_h) and next_h > 0 and
                (next_h - HC) * (h - HC) > 0 and
                abs(next_h - h) <= 0.05 * max(h, 0.05)):
                break
            dx *= 0.5
        else:
            break
        next_x = x + direction * dx
        if target is not None and (h - target) * (next_h - target) <= 0:
            fraction = (target - h) / (next_h - h)
            xs.append(x + fraction * (next_x - x))
            hs.append(target)
            return np.asarray(xs), np.asarray(hs), True
        x, h = next_x, next_h
        xs.append(x)
        hs.append(h)
    else:
        raise RuntimeError('Explicit Euler step limit reached')
    return np.asarray(xs), np.asarray(hs), False


def _conjugate(h1):
    return 0.5 * h1 * (np.sqrt(1 + 8 * _fr2(h1)) - 1)


def _profile(kind):
    steep = kind.startswith('steep')
    s0, hn, ks = _hydraulics(steep)
    hd = {'mild_m1': 1.95, 'mild_m2': 1.19,
          'mild_uniform': hn, 'mild_free': 0.58,
          'steep_free': 0.45, 'steep_jump_lake': 1.20,
          'steep_jump_channel': 1.95}[kind]
    bed = lambda x: -s0 * np.asarray(x)
    fig = go.Figure()
    x = np.linspace(0, L, 501)
    fig.add_trace(go.Scatter(x=x, y=bed(x), mode='lines', name='Channel bed',
                             line=dict(color='#9a6737', width=4)))
    fig.add_trace(go.Scatter(x=x, y=bed(x)+HC, mode='lines', name='Critical depth h_c',
                             line=dict(color='#dc2626', dash='dash', width=2)))
    fig.add_trace(go.Scatter(x=x, y=bed(x)+hn, mode='lines', name='Normal depth h₀',
                             line=dict(color='#16a34a', dash='dot', width=2)))

    segments = []
    jump = None
    note = ''
    if kind == 'mild_uniform':
        segments = [(x, np.full_like(x, hn))]
    elif kind in ('mild_m1', 'mild_m2'):
        xx, hh, _ = _integrate(L, 0, hd, s0, ks)
        segments = [(xx[::-1], hh[::-1])]
    elif kind == 'mild_free':
        # Criticality is singular in the GVF equation. Integrate from a point
        # infinitesimally upstream of the idealized critical control.
        xx, hh, _ = _integrate(L, 0, HC + 0.001, s0, ks)
        segments = [(xx[::-1], hh[::-1])]
        note = 'Idealized critical control: h(L) ≈ h_c; the brink/nappe is not resolved.'
    elif kind in ('steep_free', 'steep_jump_lake'):
        segments = [(x, np.full_like(x, hn))]
        note = ('Supercritical channel remains at normal depth; downstream reservoir '
                'jet/jump is outside the GVF domain.')
    elif kind == 'steep_jump_channel':
        # Upstream supercritical normal flow and a downstream subcritical GVF
        # branch from reservoir tailwater. Solve conjugate-depth matching for x_j.
        h2 = _conjugate(hn)
        downstream_backward_x, downstream_backward_h, found = _integrate(
            L, 0, hd, s0, ks, target=h2)
        if not found:
            raise RuntimeError('No physically admissible in-channel jump for these inputs')
        xj = float(downstream_backward_x[-1])
        jump = (xj, hn, h2)
        upstream_x = np.linspace(0, xj, 250)
        segments = [(upstream_x, np.full_like(upstream_x, hn)),
                    (downstream_backward_x[::-1], downstream_backward_h[::-1])]
        note = f'Jump position x_j = {xj:.2f} m, from specific-force matching (h₁ = {hn:.2f} m, h₂ = {h2:.2f} m).'

    for i, (xx, hh) in enumerate(segments):
        fig.add_trace(go.Scatter(x=xx, y=bed(xx)+hh, mode='lines',
                                 name='Computed water surface' if i == 0 else 'Post-jump GVF',
                                 line=dict(color='#0284c7', width=4)))
    if jump:
        xj, h1, h2 = jump
        fig.add_trace(go.Scatter(x=[xj, xj], y=[bed(xj)+h1, bed(xj)+h2],
                                 mode='lines', name='Hydraulic jump (1D discontinuity)',
                                 line=dict(color='#0284c7', width=4)))

    outlet = float(bed(L))
    bottom = outlet - 0.65
    fig.add_trace(go.Scatter(x=[L, L, 132], y=[outlet, bottom, bottom],
                             mode='lines', name='Vertical outlet wall and reservoir bed',
                             showlegend=False, line=dict(color='#9a6737', width=5)))
    fig.add_trace(go.Scatter(x=[L, 132], y=[outlet+hd, outlet+hd],
                             mode='lines', name='Reservoir level H_D',
                             line=dict(color='#2563eb', width=2, dash='dash')))
    # Vertical H_D dimension referenced to the outlet bed, as in Module 06.
    dx = 119
    fig.add_trace(go.Scatter(x=[dx, dx], y=[outlet, outlet+hd], mode='lines',
                             showlegend=False, hoverinfo='skip',
                             line=dict(color='#344054', width=2)))
    for y, ay in [(outlet+hd, 28), (outlet, -28)]:
        fig.add_annotation(x=dx, y=y, ax=0, ay=ay, xref='x', yref='y',
                           axref='pixel', ayref='pixel', text='', showarrow=True,
                           arrowhead=2, arrowsize=1.1, arrowwidth=2,
                           arrowcolor='#344054')
    fig.add_annotation(x=121, y=outlet+hd/2,
                       text=f'H<sub>D</sub> = {hd:.2f} m', showarrow=False,
                       xanchor='left', font=dict(size=13, color='#344054'),
                       bgcolor='rgba(255,255,255,0.9)')
    # Visible profile names, anchored above the computed water surface.
    # Plotly layout annotations remain visible independently of trace rendering.
    profile_labels = {
        'mild_m1': [(0, 0.48, 'M1')],
        'mild_m2': [(0, 0.48, 'M2')],
        'mild_uniform': [(0, 0.48, 'Uniform flow')],
        'mild_free': [(0, 0.48, 'M2')],
        'steep_free': [(0, 0.48, 'Uniform flow')],
        'steep_jump_lake': [(0, 0.48, 'Uniform flow')],
        'steep_jump_channel': [
            (0, 0.45, 'Uniform flow'),
            (1, 0.55, 'S1'),
        ],
    }
    for segment_index, fraction, profile_name in profile_labels[kind]:
        xx, hh = segments[segment_index]
        order = np.argsort(xx)
        xx_sorted = np.asarray(xx)[order]
        hh_sorted = np.asarray(hh)[order]
        label_x = float(xx_sorted[0] + fraction * (xx_sorted[-1] - xx_sorted[0]))
        label_h = float(np.interp(label_x, xx_sorted, hh_sorted))
        surface_y = float(bed(label_x)) + label_h
        fig.add_annotation(
            x=label_x, y=surface_y,
            xref='x', yref='y',
            text=f'<b>{profile_name}</b>',
            showarrow=False,
            xanchor='center', yanchor='bottom', yshift=16,
            font=dict(size=17, color='#0069a6'),
            bgcolor='rgba(255,255,255,0.96)',
            borderpad=3,
            opacity=1,
        )

    # Boundary conditions: red circled markers and callouts, as in Module 06.
    # Subcritical branches are controlled downstream; supercritical branches upstream.
    boundary_points = []
    if kind in ('mild_m1', 'mild_m2', 'mild_uniform'):
        boundary_points.append((L, outlet + hd, 'Downstream BC: h = H<sub>D</sub>'
                                if kind != 'mild_uniform' else
                                'Downstream BC: h = h<sub>0</sub>'))
    elif kind == 'mild_free':
        boundary_points.append((L, outlet + HC + 0.001,
                                'Outlet critical control: h ≈ h<sub>c</sub>'))
    elif kind in ('steep_free', 'steep_jump_lake'):
        boundary_points.append((0, hn, 'Upstream BC: h = h<sub>0</sub>'))
    elif kind == 'steep_jump_channel':
        boundary_points.extend([
            (0, hn, 'Upstream BC: h = h<sub>0</sub>'),
            (L, outlet + hd, 'Downstream BC: h = H<sub>D</sub>'),
        ])

    for bx, by, label in boundary_points:
        fig.add_trace(go.Scatter(
            x=[bx], y=[by], mode='markers', showlegend=False,
            hovertemplate=label.replace('<sub>', '').replace('</sub>', '') + '<extra></extra>',
            marker=dict(symbol='circle-open', size=17, color='#dc2626',
                        line=dict(color='#dc2626', width=3)),
        ))
        # Keep the annotation in the channel region, away from the H_D dimension.
        fig.add_annotation(
            x=bx, y=by, xref='x', yref='y',
            ax=-80 if bx == L else 90, ay=-52,
            axref='pixel', ayref='pixel',
            text=label, showarrow=True, arrowhead=2,
            arrowcolor='#344054', arrowwidth=1.5,
            font=dict(size=12, color='#344054'),
            bgcolor='rgba(255,255,255,0.85)',
        )

    # Slope classification beneath the channel bed (Module 06 convention).
    slope_label = 'STEEP SLOPE' if steep else 'MILD SLOPE'
    slope_label_y = float(bed(65)) - (0.55 if steep else 0.65)
    fig.add_annotation(
        x=65, y=slope_label_y, text=slope_label,
        showarrow=False, font=dict(size=14, color='#9a6737'),
        bgcolor='rgba(255,255,255,0.75)',
    )
    titles = {'mild_m1': 'Mild: M1 backwater', 'mild_m2': 'Mild: M2 drawdown',
              'mild_uniform': 'Mild: uniform outflow',
              'mild_free': 'Mild: critical outlet control',
              'steep_free': 'Steep: free supercritical outflow',
              'steep_jump_lake': 'Steep: jump downstream of channel',
              'steep_jump_channel': 'Steep: hydraulic jump inside channel'}
    yvals = [float(np.max(bed(xx)+hh)) for xx, hh in segments]
    fig.update_layout(template='plotly_white', height=400,
                      margin=dict(l=25, r=15, t=40, b=45), title=titles[kind],
                      xaxis_title='Distance x (m)', yaxis_title='Elevation z (m)',
                      legend=dict(orientation='h', y=-0.3),
                      xaxis=dict(range=[-3, 148]),
                      yaxis=dict(range=[min(bottom-0.3, slope_label_y-0.35),
                                        max(yvals + [hn, HC, outlet+hd])+0.65]))
    return fig, note, (s0, hn, ks, hd)


def _force_figure():
    h = np.linspace(0.3, 2.6, 350)
    q = Q / B
    m = q*q/(G*h) + h*h/2
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=h, y=m, mode='lines', name='Specific force M/b',
                             line=dict(color='#0284c7', width=3)))
    fig.add_vline(x=HC, line_dash='dash', line_color='#dc2626')
    fig.update_layout(template='plotly_white', height=320,
                      xaxis_title='Depth h (m)', yaxis_title='M/b (m²)',
                      margin=dict(l=20, r=20, t=20, b=25))
    return fig


def render():
    st.header('Theory — Outflow into a Reservoir')
    st.caption('Channel outflow · Reservoir tailwater · M1/M2 profiles · Hydraulic jumps')
    manuscript = (HERE / 'theory.md').read_text(encoding='utf-8')
    parts = re.split(r'<!-- PROFILE_FIGURE:([a-z0-9_]+) -->', manuscript)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                st.markdown(part)
        elif part == 'jump_force':
            st.plotly_chart(_force_figure(), use_container_width=True)
            st.caption('Specific force calculated for the same rectangular-channel discharge and width.')
        else:
            fig, note, (s0, hn, ks, hd) = _profile(part)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f'Explicit Euler GVF (Module 04 method; adaptive spatial steps), rectangular channel: Q = {Q:.3f} m³/s, '
                       f'b = {B:.2f} m, S₀ = {s0:.4f}, Kₛ = {ks:.2f} m¹ᐟ³/s, '
                       f'h₀ = {hn:.2f} m, h_c = {HC:.2f} m, L = {L:.0f} m. '
                       + note)
