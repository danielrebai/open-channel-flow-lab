# Gradually varied flow

This chapter follows the handwritten notes in their original sequence: governing equation and specific energy; mild-slope profiles; steep-slope profiles; horizontal and adverse beds; propagation of disturbances; boundary conditions. Each profile is discussed separately. The final numerical section explains how these ideas are implemented in the Toy.

## 1. Governing equation 

Consider steady flow at constant discharge $Q$ in a prismatic channel. The coordinate $x$ increases downstream. The depth $y=y(x)$ varies sufficiently slowly for the pressure distribution to be approximately hydrostatic. There are no lateral inflows, and the velocity-head coefficient is taken as one, consistently with the Toy. Bed slopes are small enough to neglect the distinction between vertical depth and depth normal to the bed.

### Notation

| Symbol | Meaning | Unit |
|---|---|---|
| $x$ | Downstream coordinate | m |
| $z_b$ | Bed elevation | m |
| $y$ | Flow depth | m |
| $y_n$ | Normal depth | m |
| $y_c$ | Critical depth | m |
| $Q$ | Discharge | m³/s |
| $b$ | Rectangular-channel width | m |
| $U=Q/A$ | Mean velocity | m/s |
| $S_0=-dz_b/dx$ | Bed slope, positive for a bed falling downstream | m/m |
| $S_f=-dH/dx$ | Energy-loss slope, positive in the flow direction | m/m |
| $n$ | Manning roughness coefficient | s/m$^{1/3}$ |
| $Fr$ | Froude number | dimensionless |

The handwritten symbols for depth, critical depth, normal depth and streamwise coordinate are replaced throughout by $y$, $y_c$, $y_n$ and $x$, matching the Toy. Bed and energy-loss slopes are denoted by $S_0$ and $S_f$.

### From total head to the depth equation

For a rectangular channel,

$$
A=by,\qquad U=\frac{Q}{by},\qquad
E(y)=y+\frac{U^2}{2g}=y+\frac{Q^2}{2gb^2y^2}.
$$

Here $E$ is the specific energy measured above the local bed. Total head is

$$
H=z_b+E.
$$

The steady energy equation and the definition of bed slope give

$$
\frac{dH}{dx}=-S_f,
\qquad \frac{dz_b}{dx}=-S_0,
\qquad \boxed{\frac{dE}{dx}=S_0-S_f}.
$$

Specific energy can therefore increase downstream even while total head decreases: the bed is falling and gravitational potential energy is being converted into specific energy.

Since discharge and channel geometry are fixed,

$$
\frac{dE}{dx}=\frac{dE}{dy}\frac{dy}{dx},
\qquad
\boxed{\frac{dy}{dx}=\frac{S_0-S_f}{dE/dy}}.
$$

Differentiating $E(y)$ yields

$$
\frac{dE}{dy}=1-\frac{Q^2}{gb^2y^3}=1-Fr^2,
\qquad Fr^2=\frac{U^2}{gy}=\frac{Q^2}{gb^2y^3}.
$$

Thus the governing equation used in the Toy is

$$
\boxed{\frac{dy}{dx}=\frac{S_0-S_f(y)}{1-Fr^2(y)}}.
$$

The numerator compares bed slope with energy dissipation; the denominator identifies the local flow regime. Their signs determine whether depth increases or decreases downstream.

### Resistance law outside uniform flow

The notes use a resistance relation to express losses as a function of depth. The Toy uses Manning's law, evaluated locally:

$$
P=b+2y,\qquad R=\frac{A}{P}=\frac{by}{b+2y},
\qquad
\boxed{S_f(y)=\left(\frac{nQ}{A(y)R(y)^{2/3}}\right)^2}.
$$

Applying a uniform-flow resistance law locally is a modelling assumption of gradually varied flow; it does not require the actual flow to be uniform. For fixed $Q,b,n$, $S_f$ decreases as $y$ increases.

## 2. Specific energy, characteristic depths and limiting behaviour

*Handwritten notes: PDF pp. 1–2 (manuscript pp. 20–21).*

### Critical depth

At fixed discharge, specific energy has a minimum where

$$
\frac{dE}{dy}=0,\qquad Fr=1.
$$

For a rectangular channel,

$$
\boxed{y_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}},
\qquad E_{\min}=\frac32 y_c.
$$

For $y>y_c$, $Fr<1$ and $dE/dy>0$: the flow is subcritical. For $0<y<y_c$, $Fr>1$ and $dE/dy<0$: the flow is supercritical. An energy value above the minimum admits two alternate depths, one on each branch. Alternate depths are not the conjugate depths of a hydraulic jump, which are related by momentum balance.

<!-- PLOT: energy -->

### Normal depth

For a positive bed slope, normal depth is the uniform-flow equilibrium:

$$
\boxed{S_f(y_n)=S_0}.
$$

Equivalently,

$$
Q=\frac{1}{n}A(y_n)R(y_n)^{2/3}\sqrt{S_0}.
$$

Unlike $y_c$, $y_n$ depends on roughness and bed slope. Because $S_f$ decreases with depth,

$$
y<y_n\Rightarrow S_f>S_0,
\qquad y>y_n\Rightarrow S_f<S_0.
$$

### Two different limits

If $y_n\ne y_c$, the denominator remains nonzero at normal depth, so

$$
y\to y_n\quad\Rightarrow\quad \frac{dy}{dx}\to0.
$$

A nonuniform profile approaches the uniform-flow line asymptotically; it does not reach and cross it at a finite distance in the smooth autonomous model. If the prescribed depth is exactly $y_n$, the solution is uniform throughout.

At critical depth, if $S_0-S_f(y_c)\ne0$, the denominator vanishes and the formal magnitude of $dy/dx$ becomes unbounded. This is the vertical tangent in the sketches. It indicates loss of validity of the gradually varied approximation, rather than a physically vertical water surface predicted reliably by this model. Such a critical limit can occur at a finite streamwise position $x_c$.

When $y_n=y_c$, numerator and denominator vanish together. This critical-slope case requires a separate limiting analysis; the statements about a nonzero numerator at critical depth do not apply to it.

<!-- PLOT: signs -->

### Reading a longitudinal sketch

Depth and water-surface elevation are different quantities:

$$
z_w=z_b+y,\qquad \frac{dz_w}{dx}=-S_0+\frac{dy}{dx}.
$$

A positive depth gradient does not by itself imply an upward-sloping water surface. As $y\to\infty$, $S_f\to0$ and $Fr\to0$, so $dy/dx\to S_0$ and $dz_w/dx\to0$. This is the horizontal limiting direction shown for the deep M1 and S1 profiles.

At constant discharge,

$$
\frac{dU}{dx}=-\frac{Q}{by^2}\frac{dy}{dx}.
$$

An increasing depth therefore means decreasing velocity; a decreasing depth means increasing velocity.

## 3. Mild-slope channel

*Handwritten notes: PDF pp. 3–4 (manuscript pp. 22–23).*

A positive slope is mild for the specified discharge, geometry and roughness when

$$
\boxed{y_n>y_c}.
$$

The normal-depth line lies above the critical-depth line. The three intervals must be examined separately.

### 3.1 M1 profile: $y>y_n>y_c$

**Sign analysis.** Since depth exceeds normal depth, friction losses are smaller than bed slope. Since depth also exceeds critical depth, the flow is subcritical:

$$
S_0-S_f>0,\qquad 1-Fr^2>0,
\qquad \boxed{\frac{dy}{dx}>0}.
$$

**Physical behaviour.** Depth increases and velocity decreases downstream. M1 is a decelerating subcritical backwater profile. A raised downstream water level, such as a reservoir or downstream obstruction, can produce this behaviour when the upstream reach remains on the subcritical branch.

**Limits.** Following the profile upstream, $y\to y_n$ asymptotically. Following its mathematical continuation downstream, depth grows; for very large depth, $dy/dx\to S_0$ and the free surface tends towards a horizontal direction. This deep limit describes the trend of the idealized solution; it does not require every real channel to extend to infinite depth.

**Control.** Prescribe a downstream depth $y_b>y_n$ and integrate upstream. The downstream disturbance produces a backwater influence extending upstream towards uniform flow.

### 3.2 M2 profile: $y_c<y<y_n$

**Sign analysis.** Depth below $y_n$ gives friction losses larger than bed slope, while depth above $y_c$ gives subcritical flow:

$$
S_0-S_f<0,\qquad 1-Fr^2>0,
\qquad \boxed{\frac{dy}{dx}<0}.
$$

**Physical behaviour.** Depth decreases and velocity increases downstream. M2 is an accelerating subcritical drawdown profile. It can occur upstream of a control that lowers the downstream depth, such as a transition towards a critical control.

**Limits.** Upstream, the profile approaches $y_n$ asymptotically from below. Downstream, it approaches $y_c$ from above with a formally unbounded negative depth gradient. The critical endpoint is generally at a finite $x_c$, where a local control or rapidly varied-flow description is required.

**Control.** Prescribe a downstream depth $y_c<y_b<y_n$ and integrate upstream. A downstream critical control may select the overall drawdown, but the ordinary Toy solver must start at a noncritical depth rather than directly at $Fr=1$.

### 3.3 M3 profile: $0<y<y_c<y_n$

**Sign analysis.** Both numerator and denominator are negative:

$$
S_0-S_f<0,\qquad 1-Fr^2<0,
\qquad \boxed{\frac{dy}{dx}>0}.
$$

**Physical behaviour.** Depth increases and velocity decreases downstream, while the flow remains supercritical. A shallow jet entering a mild reach, for example downstream of a sluice gate, may generate an M3 profile.

**Limits.** Downstream, the smooth branch tends towards $y_c$ from below with a formally unbounded positive gradient. It cannot be continued through critical depth by simply using the same GVF equation. A hydraulic jump may connect the supercritical reach to a subcritical reach before this formal endpoint; its location requires an additional matching condition.

Tracing the branch upstream reduces depth. At fixed nonzero $Q$, the limit $y\to0$ implies $U=Q/(by)\to\infty$. This is an inadmissible limiting extrapolation for the present model, not evidence that water becomes compressible at an ordinary shallow depth. Other assumptions, including hydrostatic pressure and the local resistance approximation, cease to be reliable near such extremes.

**Control.** Prescribe an upstream depth $0<y_b<y_c$ and integrate downstream. Normal depth lies on a different flow branch, so M3 cannot approach $y_n$ smoothly without a transition.

## 4. Steep-slope channel

*Handwritten notes: PDF pp. 5–6 (manuscript pp. 24–25).*

A positive slope is steep for the specified hydraulic parameters when

$$
\boxed{y_n<y_c}.
$$

The normal-depth line now lies below the critical-depth line. A steep bed does not imply that every possible flow on it is supercritical.

### 4.1 S1 profile: $y>y_c>y_n$

**Sign analysis.** Depth exceeds both characteristic depths:

$$
S_0-S_f>0,\qquad 1-Fr^2>0,
\qquad \boxed{\frac{dy}{dx}>0}.
$$

**Physical behaviour.** Depth increases and velocity decreases downstream. S1 is a decelerating subcritical profile on a steep bed. A sufficiently high downstream water level can sustain a subcritical reach, potentially downstream of a hydraulic jump.

**Limits.** Upstream, the branch approaches $y_c$ from above, with a formal positive vertical tangent at its critical endpoint. It cannot approach $y_n$ on this branch, because normal depth is below critical depth. Downstream, the deep-water limit gives $dy/dx\to S_0$ and an approximately horizontal free surface.

**Control.** Prescribe a downstream depth $y_b>y_c$ and integrate upstream. If an upstream supercritical reach is also present, its connection to S1 requires a separate hydraulic-jump calculation.

### 4.2 S2 profile: $y_n<y<y_c$

**Sign analysis.** Depth exceeds normal depth but remains below critical depth:

$$
S_0-S_f>0,\qquad 1-Fr^2<0,
\qquad \boxed{\frac{dy}{dx}<0}.
$$

**Physical behaviour.** Depth decreases and velocity increases downstream. S2 is an accelerating supercritical profile. It commonly describes the adjustment from a near-critical entrance towards the supercritical normal flow of a steep reach.

**Limits.** Upstream, the branch approaches $y_c$ from below with a formal negative vertical tangent. Downstream, it approaches $y_n$ asymptotically from above. Unlike M2, S2 approaches normal depth in the downstream direction.

**Control.** Prescribe an upstream depth $y_n<y_b<y_c$ and integrate downstream. A critical entrance needs a separate treatment before starting the noncritical GVF computation.

### 4.3 S3 profile: $0<y<y_n<y_c$

**Sign analysis.** Depth lies below both characteristic depths:

$$
S_0-S_f<0,\qquad 1-Fr^2<0,
\qquad \boxed{\frac{dy}{dx}>0}.
$$

**Physical behaviour.** Depth increases and velocity decreases downstream. S3 is a decelerating supercritical profile, possible when a shallow upstream jet enters a steep channel below its normal depth.

**Limits.** Downstream, the branch approaches $y_n$ asymptotically from below, remaining supercritical. Upstream continuation reduces depth; extrapolation to zero depth would imply unbounded velocity and lies outside the useful physical range of this model. S3 does not reach $y_c$ along its downstream adjustment, since $y_n$ is encountered as an asymptote first.

**Control.** Prescribe an upstream depth $0<y_b<y_n$ and integrate downstream.

### Comparison of the six positive-slope profiles

The following existing plot collects the six qualitative profiles. Use each panel together with its corresponding discussion above. These sketches illustrate the classification; they are not a numerical integration for the selected Toy parameters.

<!-- PLOT: profiles -->

| Profile | Depth interval | $S_0-S_f$ | $1-Fr^2$ | $dy/dx$ | Downstream velocity trend | Depth control |
|---|---|---|---|---|---|---|
| M1 | $y>y_n>y_c$ | + | + | + | Decreasing | Downstream |
| M2 | $y_c<y<y_n$ | − | + | − | Increasing | Downstream |
| M3 | $0<y<y_c<y_n$ | − | − | + | Decreasing | Upstream |
| S1 | $y>y_c>y_n$ | + | + | + | Decreasing | Downstream |
| S2 | $y_n<y<y_c$ | + | − | − | Increasing | Upstream |
| S3 | $0<y<y_n<y_c$ | − | − | + | Decreasing | Upstream |

## 5. Horizontal channel

*Handwritten notes: PDF p. 7 (manuscript p. 26).*

For a horizontal bed,

$$
S_0=0,\qquad \frac{dy}{dx}=\frac{-S_f}{1-Fr^2}.
$$

With nonzero discharge and positive roughness, $S_f>0$ at every finite depth. There is no finite normal depth satisfying $S_f=S_0=0$. The notation $y_n\to\infty$ is a formal limit as a positive slope tends to zero, not a finite uniform-flow state. There is no H1 interval.

### 5.1 H2 profile: $y>y_c$

**Signs and behaviour.** The numerator is negative and the denominator positive, so $dy/dx<0$. Depth decreases and velocity increases downstream: H2 is accelerating subcritical flow.

**Limits.** Downstream, the branch approaches critical depth with a formal negative vertical tangent at a finite endpoint. Upstream, depth increases, with $dy/dx\to0^-$ in the deep limit. No finite normal-depth line is approached.

**Control.** A downstream depth selects the subcritical profile; integrate upstream.

### 5.2 H3 profile: $0<y<y_c$

**Signs and behaviour.** Numerator and denominator are both negative, so $dy/dx>0$. Depth increases and velocity decreases downstream: H3 is decelerating supercritical flow.

**Limits.** Downstream, the branch approaches critical depth from below, where the gradually varied description fails. Upstream extrapolation tends towards smaller depths and eventually leaves the model's useful range.

**Control.** Prescribe an upstream depth and integrate downstream. The Toy currently restricts bed slope to positive values, so H2 and H3 are theoretical extensions rather than selectable Toy cases.

## 6. Adverse bed slope

*PDF p. 8 (manuscript p. 27) contains the heading only. The discussion below is an extension derived from the governing equation.*

For a bed rising downstream,

$$
S_0<0,\qquad S_0-S_f<0.
$$

There is no normal depth for positive discharge and positive energy losses: $S_f(y_n)=S_0$ cannot hold. Only the intervals above and below critical depth remain.

### 6.1 A2 profile: $y>y_c$

The numerator is negative and the denominator positive, so $dy/dx<0$. Depth decreases and velocity increases downstream, while flow stays subcritical. Its downstream critical limit requires a separate local treatment. The depth condition belongs downstream and integration proceeds upstream.

### 6.2 A3 profile: $0<y<y_c$

Both numerator and denominator are negative, so $dy/dx>0$. Depth increases and velocity decreases downstream, while flow stays supercritical. Its formal downstream limit is critical depth from below; a jump or other transition may intervene. The depth condition belongs upstream and integration proceeds downstream.

Adverse-slope cases are not available in the current Toy. They obey the same sign analysis but have no normal-depth asymptote.

## 7. Disturbances and propagation of information

*Handwritten notes: PDF p. 9 (manuscript p. 28).*

Uniform flow can be disturbed by changes in bed slope, roughness or cross section, inflow from or outflow into a reservoir, and local structures such as gates and weirs. A local disturbance and the gradually varied adjustment away from it need not be described by the same model: abrupt transitions generally require an additional local balance.

For small, long gravity waves in a rectangular channel, the wave celerity relative to the water is

$$
c=\sqrt{gy},\qquad Fr=\frac{U}{c}.
$$

Relative to the channel, the characteristic velocities are

$$
\boxed{U-c\quad\text{and}\quad U+c}.
$$

### Subcritical flow

When $Fr<1$, $U<c$. One characteristic travels upstream and the other downstream:

$$
U-c<0,\qquad U+c>0.
$$

A downstream water-level disturbance can therefore influence the upstream reach. This gives the physical explanation for downstream depth control in subcritical GVF.

### Supercritical flow

When $Fr>1$, $U>c$ and both characteristics travel downstream:

$$
U-c>0,\qquad U+c>0.
$$

Small disturbances cannot carry information upstream against this flow. Upstream conditions determine the supercritical adjustment downstream. A sufficiently strong downstream obstruction may instead cause a jump and change the flow-regime configuration; that process is outside a single smooth GVF branch.

<!-- PLOT: waves -->

## 8. Boundary conditions

*Handwritten notes: PDF p. 10 (manuscript p. 29).*

For steady flow without lateral inflows,

$$
\frac{dQ}{dx}=0,
\qquad
\frac{dy}{dx}=\frac{S_0-S_f(y)}{1-Fr^2(y)}.
$$

The discharge is specified and remains constant. The first-order depth equation then needs one depth condition on a noncritical branch. The physical position of that condition follows from information propagation.

On a reach $0\le x\le L$:

| Regime | Given discharge | Depth condition | Integration direction |
|---|---|---|---|
| Subcritical | $Q=\bar Q$ | $y(L)=y_b>y_c$ | From downstream towards upstream |
| Supercritical | $Q=\bar Q$ | $y(0)=y_b<y_c$ | From upstream towards downstream |

These rules describe the steady, fixed-discharge problem used here; they are not a complete specification of every possible unsteady boundary-value problem.

A numerical routine may be able to march an ODE from another end, but that alone does not make the imposed boundary condition physically appropriate. The Toy therefore rejects an upstream subcritical depth condition, a downstream supercritical depth condition, and a depth at or too close to critical depth.

## 9. Selecting the physical profile around a disturbance

*Handwritten notes: PDF pp. 11–12 (manuscript pp. 30–31).*

The final sketches ask which side of a local disturbance can adjust smoothly towards uniform flow. Two checks are needed: the sign of $dy/dx$ must match the profile interval, and the branch must respect the direction of hydraulic influence.

### 9.1 Mild channel

For a mild channel, uniform flow is subcritical because $y_n>y_c$.

**A depth above normal: M1.** If a downstream control raises the depth above $y_n$, the upstream adjustment is M1. Depth increases towards the control and tends to $y_n$ far upstream. A sketch showing decreasing depth downstream in this interval contradicts the positive gradient required by the equation.

**A depth between critical and normal: M2.** A downstream control imposing $y_c<y_b<y_n$ selects an upstream M2 drawdown. Depth decreases towards the control and tends to $y_n$ far upstream. A sketch with a positive gradient in this interval is inconsistent with the sign analysis.

**A depth below critical: M3.** This condition is supercritical and must be imposed upstream for a smooth downstream adjustment. The resulting M3 branch deepens downstream. It cannot merge smoothly with the mild channel's subcritical normal flow: a hydraulic jump or another transition is needed. The jump is not represented by the GVF differential equation, and its position requires matching the supercritical and subcritical reaches.

### 9.2 Steep channel

For a steep channel, uniform flow is supercritical because $y_n<y_c$.

**A depth above critical: S1.** This is a subcritical reach controlled from downstream. Moving upstream, S1 tends towards critical depth rather than the supercritical normal depth. Connection to an upstream supercritical reach requires a separate transition, often a hydraulic jump when the conditions permit one.

**A depth between normal and critical: S2.** An upstream condition $y_n<y_b<y_c$ gives an S2 profile. Depth decreases downstream and approaches $y_n$ from above. A downstream-increasing curve in this interval has the wrong sign.

**A depth below normal: S3.** An upstream condition $0<y_b<y_n$ gives an S3 profile. Depth increases downstream and approaches $y_n$ from below. A downstream-decreasing curve in this interval has the wrong sign.

The organizing rule is the conclusion of the notes: subcritical reaches are controlled by downstream depth, whereas supercritical reaches are controlled by upstream depth. Bed classification alone does not identify the controlling end; the local flow regime does.

## 10. Numerical integration in the Toy

*Implementation supplement, following the method identified in the supplied Toy as Defina, §8.2.1. This section is additional to the handwritten notes.*

Define

$$
f(y)=\frac{S_0-S_f(y)}{1-Fr^2(y)}.
$$

The Toy first computes $y_c$ explicitly and solves $S_f(y_n)=S_0$ by bisection. It then checks the prescribed boundary depth and its location before integrating.

### Explicit Euler step

For subcritical flow, integrate upstream with a positive step magnitude $\Delta x_i$:

$$
x_{i+1}=x_i-\Delta x_i,
\qquad \boxed{y_{i+1}=y_i-f(y_i)\Delta x_i}.
$$

For supercritical flow, integrate downstream:

$$
x_{i+1}=x_i+\Delta x_i,
\qquad \boxed{y_{i+1}=y_i+f(y_i)\Delta x_i}.
$$

All hydraulic quantities in $f(y_i)$ are evaluated at the current depth. This is a first-order explicit method. The minus sign for upstream integration changes the marching direction; it does not change the downstream-coordinate sign analysis used to classify profiles.

### Step control and stopping

The supplied Toy chooses a local step based on depth and reduces it when the gradient is large or the current depth is near critical. It also halves trial steps if needed to retain positive depth, limit the depth increment and stay on the same side of critical depth.

With automatic length enabled, the calculation may stop when it has approached normal depth or critical depth within numerical tolerances, or when a length or step limit is reached. These tolerances do not turn a normal-depth asymptote into an exact finite-distance endpoint. The denominator guard can stop the solver before critical depth is reached.

The solver does not calculate a hydraulic jump or continue smoothly through a singular critical state. Numerical safeguards prevent invalid steps; they do not extend the physical validity of the GVF approximation.

### Accuracy and plotting

At fixed inputs and algorithm settings, the Toy's calculations are deterministic. Euler integration is approximate: a smaller spatial step generally reduces discretization error on a regular branch, but cannot repair an invalid physical model near a rapid transition. A step-refinement comparison is useful when quantitative accuracy matters; the current Toy does not provide a built-in convergence study.

The physical water-surface elevation is $z_w=z_b+y$. The Toy can display depths with a visual amplification factor $a$, producing $z_{\mathrm{display}}=z_b+a y$. When $a\ne1$, the displayed elevation and apparent surface slope are not physical elevations and slopes. Hover values report the actual depths, and the amplification does not change the numerical solution.

## Sources and scope

The chapter's sequence and qualitative argument follow the supplied twelve-page handwritten PDF. Its notation has been aligned with the supplied Toy, and Manning's resistance law is used to match that implementation. The adverse-slope discussion expands a heading-only manuscript page; the numerical and display sections explain the supplied code. Critical endpoints are distinguished from infinite-distance normal-depth asymptotes, and formal extreme-depth limits are kept separate from physically reliable predictions.
