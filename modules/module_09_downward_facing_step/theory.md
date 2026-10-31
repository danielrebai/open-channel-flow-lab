# Downward Facing Step

A downward-facing step connects two prismatic channel reaches at different bed elevations. The channel bed falls by a vertical distance $a>0$ from the upstream reach (U) to the downstream reach (D). Depending on the bed slopes and the available specific energy, the transition may involve subcritical flow, supercritical flow, critical control, or a hydraulic jump.

## Governing principles

For steady flow in a rectangular channel of width $b$, with discharge $Q$ and unit discharge $q=Q/b$, the specific energy is

$$
E(h)=h+\frac{q^2}{2gh^2}.
$$

The critical depth $h_c$ and minimum specific energy are

$$
h_c=\left(\frac{q^2}{g}\right)^{1/3},\qquad E_{\min}=E(h_c)=\frac{3}{2}h_c.
$$

The idealized energy balance across the downward step, neglecting local losses, is

$$
E_D=E_U+a.
$$

Thus the downstream section has greater *specific* energy because its bed is lower. For a given energy greater than $E_{\min}$, the energy curve admits a supercritical solution ($h<h_c$) and a subcritical solution ($h>h_c$). A state with $E<E_{\min}$ is not physically admissible.

The specific force per unit channel width is

$$
M(h)=\frac{h^2}{2}+\frac{q^2}{gh}.
$$

Across a hydraulic jump, the conjugate depths $h_1$ and $h_2$ satisfy $M(h_1)=M(h_2)$ under the usual hydrostatic, prismatic-channel assumptions. Specific energy decreases through the jump; the lossless step relation must not be applied across the jump itself.

Away from the immediate step and from hydraulic jumps, the water-surface profile follows the gradually varied flow (GVF) equation:

$$
\frac{dh}{dx}=\frac{S-S_f}{1-Fr^2},\qquad
Fr^2=\frac{q^2}{gh^3},
$$

where $S$ is the local bed slope and $S_f$ is the friction slope. Normal depth $h_n$ is defined by $S_f(h_n)=S$. On a **mild slope**, $h_n>h_c$; on a **steep slope**, $h_n<h_c$. The numerical illustrations use Manning resistance, with fixed example parameters stated alongside each case.

In the plots, blue denotes the water surface, green the normal-depth reference, red the critical-depth reference, and brown the channel bed. The boundary-condition markers identify the states from which the numerical profiles are determined. A reach that begins at $h=h_n$ is labelled **Uniform flow**; nonuniform branches use the standard M1–M3 or S1–S3 classification.

## Case 1 — Steep / Steep

Both reaches have steep slopes, so their normal depths lie below critical depth. Supercritical flow is governed by the upstream boundary condition. With upstream uniform flow, $h_U=h_{n,U}$ at the prescribed upstream section. The downward step increases the available specific energy, and the downstream flow remains on the supercritical branch in the illustrated configuration.

The step transition is evaluated using $E_D=E_U+a$. A critical depth must not be imposed arbitrarily at the step when the supercritical upstream flow already supplies the controlling condition. The downstream profile is obtained from the supercritical state after the step and integrated along the lower reach.

<!-- CASE:steep_steep -->

## Case 2 — Mild / Mild

Both reaches have mild slopes, so normal flow is subcritical. The downstream boundary condition influences the upstream water surface. Two distinct energy regimes must be considered.

### 2a. Sufficient energy

When the energy balance admits the required upstream and downstream subcritical states, the flow adjusts through the downward step without choking. The states lie on the subcritical branch of $E(h)$ and satisfy

$$
E_D-E_U=a.
$$

The upstream profile is integrated from the controlling downstream state, with normal depth providing the uniform-flow reference.

<!-- CASE:mild_mild_sufficient -->

### 2b. Insufficient energy

Before constructing the adjusted profile, test the hypothetical upstream energy implied by the prescribed downstream state:

$$
E_{U,\mathrm{required}}=E_D-a.
$$

If $E_{U,\mathrm{required}}<E_{\min}$, no upstream depth satisfies the assumed lossless transition. The preliminary energy diagram makes this incompatibility explicit. The flow must instead adjust its control and water levels; a critical state can occur at the upstream edge of the step.

A supercritical region may develop below the step, followed by a hydraulic jump where it meets the downstream-controlled subcritical flow. The jump position is determined by matching conjugate depths through the specific-force relation, rather than placing a jump arbitrarily on the profile.

<!-- CASE:mild_mild_insufficient -->

## Case 3 — Mild / Steep

The upstream reach has subcritical normal flow, while the downstream reach has supercritical normal flow. The transition can be controlled at the upstream edge of the step, where $h_U=h_c$. The downstream depth then follows from

$$
E_D=E(h_c)+a.
$$

Because $a>0$, the downstream energy exceeds the critical minimum. The relevant downstream state is on the supercritical branch, $h_D<h_c$, and the lower reach develops a supercritical profile. Critical depth cannot simultaneously occur on both sides of a nonzero downward step under the lossless energy relation.

<!-- CASE:mild_steep -->

## Case 4 — Steep / Mild

The upstream reach tends toward supercritical uniform flow, while the downstream reach tends toward subcritical uniform flow. There are consequently **two controlling boundary conditions**: one upstream and one downstream. These controls need not connect through a single continuous GVF profile.

The transition may require one or more hydraulic jumps, depending on the imposed states and the available reach lengths. A jump connects supercritical and subcritical depths with equal specific force, while dissipating specific energy. The step relation $E_D=E_U+a$ is applied only between the sections immediately adjacent to the step, not across a jump.

The longitudinal diagram shows the calculated branches and any hydraulically admissible jump locations for the fixed example. A critical state must not be assigned to the upstream step edge solely because the bed elevation changes: the upstream supercritical boundary condition remains essential.

<!-- CASE:steep_mild -->

## Reading the quantitative diagrams

Each case includes a longitudinal water-surface profile followed by the specific-energy diagram. The energy diagram identifies the upstream and downstream depths $h_U$ and $h_D$, their energy levels $E_U$ and $E_D$, and the step drop $a=E_D-E_U$. Vertical arrows distinguish the prescribed input state from the resulting output state. Where a hydraulic jump is involved, the specific-force diagram provides the corresponding momentum comparison.

The examples are fixed, reproducible numerical illustrations. Their discharge, roughness, slopes, reach lengths and step heights are model inputs, not universal values. The plotted GVF branches are numerical solutions under those assumptions; jump locations and admissibility depend on the selected boundary conditions and momentum matching.
