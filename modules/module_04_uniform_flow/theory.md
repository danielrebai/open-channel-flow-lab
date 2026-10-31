# Uniform Flow

## 1. Uniform flow and the energy equation
Uniform flow is characterized by a constant water depth $y_0$, called the **normal depth**:

$$
\boxed{y(x)=y_0=\mathrm{constant}},
\qquad \boxed{\frac{dy}{dx}=0}.
$$

For steady flow at constant discharge in a prismatic channel, the cross-sectional area $A(y_0)$ and mean velocity $U=Q/A(y_0)$ are also constant. Consequently, the velocity head is constant, and the bed, free surface, and energy grade line are parallel.

Let $z_b(x)$ be the bed elevation and $E$ the specific energy measured relative to the bed. The total energy head is

$$
H=z_b+E,
\qquad
E=y+\alpha\frac{U^2}{2g},
$$

where $\alpha$ is the kinetic-energy correction coefficient. In the simplified calculations used throughout the laboratory, $\alpha=1$.

The steady-flow energy equation and the bed-slope definition are

$$
\frac{dH}{dx}=-S_f,
\qquad
\frac{dz_b}{dx}=-S_0.
$$

Since $H=z_b+E$,

$$
\frac{dE}{dx}
=\frac{dH}{dx}-\frac{dz_b}{dx}
=-S_f+S_0.
$$

Therefore,

$$
\boxed{\frac{dE}{dx}=S_0-S_f}.
$$

Under uniform-flow conditions, $y$, $U$, and hence $E$ are constant along the channel. Thus

$$
\frac{dE}{dx}=0
\quad\Longrightarrow\quad
0=S_0-S_f,
$$

and the fundamental uniform-flow condition is

$$
\boxed{S_0=S_f}.
$$

In an alternative notation frequently used for open-channel hydraulics, the bed slope is written $i$ and the friction slope $J$; the same condition is $i=J$.

## 2. Chézy resistance equation

The empirical **Chézy equation** expresses the friction slope in terms of the mean cross-sectional velocity and hydraulic radius:

$$
\boxed{S_f=\frac{U^2}{C^2R}},
$$

where

$$
U=\frac{Q}{A},
\qquad
R=\frac{A}{P}.
$$

Here $A$ is the wetted cross-sectional area, $P$ is the wetted perimeter, $R$ is the hydraulic radius, and $C$ is the Chézy coefficient. The quadratic dependence $S_f\propto U^2$ is characteristic of the resistance approximation adopted for fully turbulent flow.

Because slopes are dimensionless, the dimensions of $C$ follow from Chézy's equation:

$$
[C]
=\left[\frac{U^2}{RS_f}\right]^{1/2}
=\frac{L^{1/2}}{T}.
$$

The coefficient $C$ depends on the boundary roughness and on the hydraulic radius:

$$
C=C\bigl(\text{roughness},R(y)\bigr).
$$

### 2.1 Gauckler–Strickler and Manning coefficients

Two widely used representations of the Chézy coefficient are

$$
\boxed{C=K_sR^{1/6}}
\qquad\text{(Gauckler–Strickler)},
$$

and

$$
\boxed{C=\frac{1}{n}R^{1/6}}
\qquad\text{(Manning)}.
$$

The coefficients are related by

$$
\boxed{K_s=\frac{1}{n}}.
$$

Here $n$ is the **Manning roughness coefficient**, the resistance parameter used in the gradually varied flow module; $K_s$ is the corresponding Strickler coefficient. Neither coefficient is dimensionless:

$$
[K_s]=\frac{L^{1/3}}{T}
=\mathrm{m^{1/3}/s},
\qquad
[n]=\frac{T}{L^{1/3}}
=\mathrm{s/m^{1/3}}.
$$

Substitution into Chézy's equation gives

$$
S_f=\frac{U^2}{K_s^2R^{4/3}}
=\frac{n^2U^2}{R^{4/3}}.
$$

For a fixed velocity and hydraulic radius,

$$
S_f\propto\frac{1}{K_s^2}\propto n^2.
$$

Thus a rougher channel has a **smaller $K_s$**, a **larger $n$**, and greater friction losses under otherwise identical conditions. Indicative Strickler coefficients may range from approximately $25\ \mathrm{m^{1/3}/s}$ for rough surfaces to $80\ \mathrm{m^{1/3}/s}$ for smoother surfaces; these are illustrative values, not universal design recommendations.

## 3. Uniform-flow velocity

Starting with Chézy's formula and substituting $C=K_sR^{1/6}$,

$$
\begin{aligned}
S_f
&=\frac{U^2}{C^2R}\\
&=\frac{U^2}{K_s^2R^{1/3}R}\\
&=\frac{U^2}{K_s^2R^{4/3}}.
\end{aligned}
$$

Rearranging,

$$
\boxed{U^2=K_s^2R^{4/3}S_f}.
$$

For uniform flow, $S_f=S_0$, so the positive downstream mean velocity is

$$
\boxed{U=K_sR^{2/3}\sqrt{S_0}}.
$$

Equivalently, using Manning's coefficient,

$$
\boxed{U=\frac{1}{n}R^{2/3}\sqrt{S_0}}.
$$

Both expressions describe the same uniform-flow resistance relationship. They require a positive bed slope for a nonzero, gravity-driven uniform discharge.

## 4. Normal depth

The **normal depth** $y_0$ is the depth of steady uniform flow corresponding to a specified discharge $Q$, bed slope $S_0$, channel roughness, and cross-sectional geometry.

Using $Q=UA$ in the Gauckler–Strickler equation gives

$$
\boxed{Q=K_sA(y_0)R(y_0)^{2/3}\sqrt{S_0}}.
$$

The equivalent Manning form is

$$
\boxed{Q=\frac{1}{n}A(y_0)R(y_0)^{2/3}\sqrt{S_0}}.
$$

For specified $Q$, $S_0$, $n$ (or $K_s$), and channel geometry, these equations determine $y_0$. Because $A$ and $R$ depend on depth, the normal-depth equation is generally implicit.

### 4.1 Rectangular channel

For a rectangular channel of width $b$,

$$
A(y_0)=by_0,
\qquad
P(y_0)=b+2y_0,
\qquad
R(y_0)=\frac{by_0}{b+2y_0}.
$$

Therefore,

$$
\boxed{
Q=K_s(by_0)
\left(\frac{by_0}{b+2y_0}\right)^{2/3}
\sqrt{S_0}
}.
$$

Or, in the notation used for friction in the gradually varied flow module,

$$
\boxed{
Q=\frac{by_0}{n}
\left(\frac{by_0}{b+2y_0}\right)^{2/3}
\sqrt{S_0}
}.
$$

For finite $b$, the equation is normally solved numerically. It is equivalent to solving

$$
\boxed{
S_f(y_0)=\left(\frac{nQ}{A(y_0)R(y_0)^{2/3}}\right)^2=S_0
}.
$$

### 4.2 Numerical computation of normal depth

For a rectangular channel of finite width, the normal-depth equation is implicit because the hydraulic radius depends on $y_0$. A simple way to compute $y_0$ is to rearrange the discharge equation into a **fixed-point iteration**.

Starting from

$$
Q=K_s b y_0\left(\frac{b y_0}{b+2y_0}\right)^{2/3}\sqrt{S_0},
$$

collect the powers of $y_0$:

$$
Q=K_s b^{5/3}\sqrt{S_0}\,\frac{y_0^{5/3}}{(b+2y_0)^{2/3}}.
$$

Raising both sides to the power $3/5$ and isolating $y_0$ gives

$$
\boxed{
y_0=\frac{1}{b}\left(\frac{Q}{K_s\sqrt{S_0}}\right)^{3/5}
(b+2y_0)^{2/5}
}.
$$

Starting from an initial estimate $y_0^{(1)}$, successive approximations are calculated as

$$
\boxed{
y_0^{(k+1)}=\frac{1}{b}
\left(\frac{Q}{K_s\sqrt{S_0}}\right)^{3/5}
\left(b+2y_0^{(k)}\right)^{2/5},
\qquad k=1,2,\ldots
}.
$$

A particularly simple initial estimate is

$$
\boxed{y_0^{(1)}=0}.
$$

Although zero is not a physical normal depth for $Q>0$, it is a valid **starting value for this iteration**: the first update is positive. Alternatively, the wide-rectangular-channel approximation derived below provides a positive initial estimate,

$$
y_0^{(1)}=\left(\frac{Q}{K_s b\sqrt{S_0}}\right)^{3/5}.
$$

Continue the iteration until two consecutive estimates differ by less than a chosen tolerance, for example

$$
\left|y_0^{(k+1)}-y_0^{(k)}\right|<\varepsilon_y,
$$

where $\varepsilon_y$ is a prescribed depth tolerance. Finally, substitute the computed depth into the **original** discharge equation and verify that

$$
Q\approx K_s A(y_0)R(y_0)^{2/3}\sqrt{S_0}.
$$

This iterative procedure applies for $Q>0$, $b>0$, $K_s>0$, and $S_0>0$. The convergence check should be based on both the change in depth and the discharge residual when high numerical accuracy is required.

### 4.3 Wide rectangular channel

If the channel is wide relative to its depth,

$$
b\gg 2y_0,
\qquad
R(y_0)=\frac{by_0}{b+2y_0}\approx y_0.
$$

The discharge equation simplifies to

$$
Q\approx K_sby_0^{5/3}\sqrt{S_0}
=\frac{b}{n}y_0^{5/3}\sqrt{S_0}.
$$

Solving for $y_0$,

$$
\boxed{
y_0\approx\left(\frac{Q}{K_sb\sqrt{S_0}}\right)^{3/5}
=\left(\frac{nQ}{b\sqrt{S_0}}\right)^{3/5}
}.
$$

This explicit expression is valid under the **wide-channel approximation**; it is not exact for a finite-width rectangular channel.

## 5. Normal rating curve

For fixed channel geometry, roughness, and positive bed slope, the **normal rating curve** relates discharge to normal depth:

$$
\boxed{Q=K_sA(y_0)R(y_0)^{2/3}\sqrt{S_0}}.
$$

Normal depth increases with discharge. In a wide rectangular channel, the explicit approximation above gives

$$
\boxed{y_0\propto Q^{3/5}}.
$$

For a natural channel, the area and hydraulic radius may vary differently with depth. Consequently, the shape and local power-law behavior of the rating curve depend on the cross-sectional geometry; a universal exponent cannot be assigned without further assumptions.

<!-- FIGURE: normal_rating -->

## 6. Classification of channel slopes

The classification of channel slopes compares **normal depth** $y_0$ with **critical depth** $y_c$. The critical depth depends on discharge and channel geometry, whereas normal depth also depends on resistance and bed slope.

For a rectangular channel, with $q=Q/b$ and $\alpha=1$,

$$
\boxed{y_c=\left(\frac{q^2}{g}\right)^{1/3}},
\qquad q=\frac{Q}{b}.
$$

### 6.1 Critical slope

The **critical slope** $S_c$ is the positive bed slope at which the normal and critical depths coincide:

$$
\boxed{S_0=S_c\quad\Longleftrightarrow\quad y_0=y_c}.
$$

For fixed discharge, geometry, and roughness, substituting $y_c$ into the uniform-flow equation gives

$$
\boxed{
S_c=\left[\frac{Q}{K_sA(y_c)R(y_c)^{2/3}}\right]^2
=\left[\frac{nQ}{A(y_c)R(y_c)^{2/3}}\right]^2
}.
$$

At critical slope, uniform flow is critical: $\mathrm{Fr}=1$.

<!-- FIGURE: critical -->

### 6.2 Mild slope

A channel has a **mild slope** when

$$
\boxed{0<S_0<S_c\quad\Longleftrightarrow\quad y_0>y_c}.
$$

The normal depth lies above the critical depth, and uniform flow is **subcritical** ($\mathrm{Fr}<1$).

<!-- FIGURE: mild -->

### 6.3 Steep slope

A channel has a **steep slope** when

$$
\boxed{S_0>S_c\quad\Longleftrightarrow\quad y_0<y_c}.
$$

The normal depth lies below the critical depth, and uniform flow is **supercritical** ($\mathrm{Fr}>1$).

<!-- FIGURE: steep -->

### 6.4 Horizontal bed

For a horizontal channel,

$$
S_0=0.
$$

The uniform-flow condition requires $S_f=S_0=0$. Yet for a positive discharge and finite depth, the Chézy–Manning resistance law gives $S_f>0$. Hence **no finite normal depth exists for $Q>0$** under this gravity-driven uniform-flow model.

Formally, for fixed $Q>0$ and the same channel geometry and roughness,

$$
S_0\to0^+
\quad\Longrightarrow\quad
y_0\to\infty.
$$

<!-- FIGURE: horizontal -->

### 6.5 Adverse slope

An **adverse slope** means that the bed rises downstream:

$$
S_0<0.
$$

The uniform-flow condition would require $S_f=S_0<0$, whereas frictional energy loss is positive for moving water. Therefore, **gravity-driven steady uniform flow with positive discharge has no normal depth on an adverse slope**.

<!-- FIGURE: adverse -->

## 7. Summary

| Channel slope | Bed-slope condition | Depth relation | Uniform-flow regime |
|---|---|---|---|
| Critical | $S_0=S_c$ | $y_0=y_c$ | Critical |
| Mild | $0<S_0<S_c$ | $y_0>y_c$ | Subcritical |
| Steep | $S_0>S_c$ | $y_0<y_c$ | Supercritical |
| Horizontal | $S_0=0$ | No finite $y_0$ for $Q>0$ | No gravity-driven uniform solution |
| Adverse | $S_0<0$ | No $y_0$ for $Q>0$ | No gravity-driven uniform solution |

The central relations are

$$
\boxed{S_0=S_f},
\qquad
\boxed{Q=\frac{1}{n}A(y_0)R(y_0)^{2/3}\sqrt{S_0}},
$$

and, at the critical slope,

$$
\boxed{y_0=y_c\quad\text{when}\quad S_0=S_c}.
$$
