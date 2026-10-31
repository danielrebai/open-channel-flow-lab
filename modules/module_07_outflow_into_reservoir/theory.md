# Outflow into a Reservoir

*Module 07 · Channel outflow · Downstream tailwater · Gradually varied flow and hydraulic jumps*

## 1. Physical setting and governing equations

Consider a prismatic open channel conveying a steady discharge $Q$ into a large reservoir. The reservoir water level, measured vertically above the channel bed at the outlet, is $H_D$. The channel bed slope is $i$ (or $S_0$), the normal depth is $h_0$, and the critical depth is $h_c$. The Strickler roughness coefficient is $K_s$, the kinetic-energy correction coefficient is $\alpha$, and $A(h)$, $B(h)$, and $R(h)$ denote the wetted area, free-surface width, and hydraulic radius.

The discharge and channel geometry are assumed known. The flow is steady and one-dimensional, and the channel is sufficiently long for normal flow to be an appropriate upstream reference state. Gradually varied flow (GVF) theory describes the water-surface profile away from hydraulic jumps and the immediate outlet region.

Critical depth and normal depth follow from

$$
\frac{A^3(h_c)}{B(h_c)}=\frac{\alpha Q^2}{g},
$$

$$
Q=A(h_0)K_sR(h_0)^{2/3}\sqrt{i}.
$$

For a rectangular channel of width $b$,

$$
A(h)=bh,\qquad B(h)=b,\qquad R(h)=\frac{bh}{b+2h}.
$$

When $\alpha=1$, the critical depth is

$$
h_c=\left(\frac{Q^2}{gb^2}\right)^{1/3}.
$$

The specific energy and GVF equation are

$$
E(h,Q)=h+\frac{\alpha Q^2}{2gA(h)^2},
$$

$$
\frac{dh}{dx}=\frac{i-S_f(h)}{1-Fr^2(h)},
$$

where $x$ increases downstream and

$$
S_f(h)=\left(\frac{Q}{K_sA(h)R(h)^{2/3}}\right)^2,
\qquad
Fr^2(h)=\frac{\alpha Q^2B(h)}{gA(h)^3}.
$$

For constant $\alpha$, $h=h_c$ corresponds to minimum specific energy. Flow is subcritical when $h>h_c$ and supercritical when $h<h_c$. In the figures, the normal-depth and critical-depth reference lines are measured vertically from the channel bed.

## 2. Outflow from a mild-slope channel

For a mild slope, $i<i_c$ and $h_0>h_c$. Normal flow is subcritical, so the reservoir can influence the water-surface profile upstream through the downstream boundary condition.

### 2.1 High tailwater: $H_D>h_0$ — M1 profile

When the outlet is hydraulically connected to the reservoir and the tailwater level exceeds normal depth, the downstream condition is

$$
h(L)=H_D.
$$

The water depth increases toward the outlet, producing an **M1 backwater profile**. Far upstream, the depth approaches $h_0$.

<!-- PROFILE_FIGURE:mild_m1 -->

### 2.2 Intermediate tailwater: $h_c<H_D<h_0$ — M2 profile

When the tailwater lies between critical and normal depth, the downstream boundary condition is again

$$
h(L)=H_D.
$$

The depth decreases downstream, producing an **M2 drawdown profile** that approaches normal depth upstream.

<!-- PROFILE_FIGURE:mild_m2 -->

### 2.3 Tailwater equal to normal depth: $H_D=h_0$

When the reservoir level matches normal depth at the outlet, the idealized solution is **uniform flow**:

$$
h(x)=h_0.
$$

No backwater or drawdown profile is required.

<!-- PROFILE_FIGURE:mild_uniform -->

### 2.4 Low tailwater: $H_D\le h_c$ — outlet critical control

When the reservoir level is too low to maintain a subcritical outlet depth, the downstream tailwater no longer provides the controlling subcritical boundary condition. In an idealized outlet-control model, the channel approaches critical depth at its downstream control section:

$$
h(L)\simeq h_c.
$$

An **M2 drawdown profile** develops upstream of that section. The actual brink depth, free jet, and local outlet flow cannot be obtained from the GVF equation alone and depend on the outlet geometry.

<!-- PROFILE_FIGURE:mild_free -->

For a submerged outlet, a simplified local energy balance may be written as

$$
E(h,Q)=H_D+\Delta E.
$$

If the reservoir velocity is negligible and the local energy change is approximated by the upstream velocity head,

$$
\Delta E\approx\frac{\alpha Q^2}{2gA(h)^2},
$$

then $h\approx H_D$. This approximation requires negligible additional outlet losses; where such losses are significant, the outlet boundary depth must be evaluated with an appropriate energy-loss model.

## 3. Outflow from a steep-slope channel

For a steep slope, $i>i_c$ and $h_0<h_c$. Normal flow is supercritical. Downstream disturbances cannot propagate upstream through a continuously supercritical reach. For a long reach approaching uniform flow, the upstream boundary condition is $h=h_0$.

The reservoir may nevertheless produce a hydraulic jump. Its location depends on the upstream momentum, the downstream water-surface profile, and the available tailwater.

### 3.1 Low tailwater: free supercritical outflow

With sufficiently low tailwater, the flow remains supercritical throughout the channel and discharges into the reservoir. The channel profile is **uniform flow** when the upstream depth equals $h_0$. The outlet jet and mixing region lie outside the GVF description.

<!-- PROFILE_FIGURE:steep_free -->

### 3.2 Hydraulic jump downstream of the channel

For a suitable tailwater level, a hydraulic jump may form just beyond the outlet or within the reservoir. The channel remains supercritical, with **uniform flow** up to the outlet. Determining the jump position in the reservoir requires a local momentum model and the receiving-basin geometry.

<!-- PROFILE_FIGURE:steep_jump_lake -->

### 3.3 Hydraulic jump inside the channel — S1 profile

At sufficiently high tailwater, the hydraulic jump may move upstream into the steep channel. The flow is supercritical upstream of the jump, where it is **uniform flow** in the idealized long-reach case. Immediately downstream of the jump, the flow is subcritical. Because the depth exceeds both $h_c$ and $h_0$, the downstream GVF branch is an **S1 profile**.

The hydraulic jump itself is a rapidly varied transition: the water depth changes abruptly from $h_1$ to its conjugate depth $h_2$. The S1 profile is integrated upstream from the reservoir boundary and matched to the supercritical branch through the momentum equation.

<!-- PROFILE_FIGURE:steep_jump_channel -->

### 3.4 Transition between jump locations

Neither $H_D=h_c$ nor $H_D=h_0$ alone determines the location of a hydraulic jump. The relevant conditions include the conjugate depth of the supercritical flow, the downstream profile, and local outlet effects. As the tailwater rises, the jump may move from the receiving reservoir into the channel. If no admissible in-channel jump can be matched, the local outlet region must be analyzed separately.

## 4. Hydraulic jumps and specific force

The conjugate depths across a hydraulic jump are determined by **momentum conservation**, not by equality of specific energy. For a short jump with approximately hydrostatic end sections and negligible external horizontal forces, the specific force is

$$
M(h)=\frac{Q^2}{gA(h)}+A(h)\bar z(h),
$$

where $\bar z(h)$ is the vertical distance from the free surface to the centroid of the wetted cross-section.

For a rectangular channel, with discharge per unit width $q=Q/b$,

$$
\frac{M(h)}{b}=\frac{q^2}{gh}+\frac{h^2}{2}.
$$

The conjugate depths $h_1<h_c<h_2$ satisfy

$$
M(h_1)=M(h_2).
$$

Thus,

$$
h_2=\frac{h_1}{2}\left(\sqrt{1+8Fr_1^2}-1\right),
\qquad
Fr_1=\frac{Q}{bh_1\sqrt{gh_1}}.
$$

A hydraulic jump dissipates energy:

$$
E(h_1,Q)>E(h_2,Q).
$$

To locate an in-channel jump, calculate the upstream supercritical depth and its conjugate depth, determine the downstream subcritical GVF profile from the reservoir boundary, and find the position where the downstream depth equals the conjugate depth. This gives the idealized jump position in a one-dimensional model.

<!-- PROFILE_FIGURE:jump_force -->

## 5. Summary of flow configurations

| Channel | Tailwater condition | Flow configuration | Governing condition |
|---|---|---|---|
| Mild ($h_0>h_c$) | $H_D>h_0$ | M1 backwater | Downstream $h(L)=H_D$ |
| Mild | $H_D=h_0$ | Uniform flow | $h=h_0$ |
| Mild | $h_c<H_D<h_0$ | M2 drawdown | Downstream $h(L)=H_D$ |
| Mild | $H_D\le h_c$ | M2 toward outlet critical control | Idealized $h(L)\simeq h_c$ |
| Steep ($h_0<h_c$) | Low tailwater | Supercritical uniform flow | Upstream $h=h_0$ |
| Steep | Jump beyond outlet | Supercritical uniform flow in channel | Upstream $h=h_0$; local momentum at outlet |
| Steep | Sufficiently high tailwater | Uniform flow, hydraulic jump, S1 profile | Upstream $h=h_0$; downstream $h(L)=H_D$; conjugate-depth matching |

## 6. Interpretation of the numerical figures

The water-surface profiles shown in this module are calculated for specified illustrative channel parameters. Gradually varied profiles are integrated numerically using the first-order explicit Euler method with adaptive spatial steps, consistent with the numerical approach introduced for GVF. Normal-depth reference lines represent exact uniform-flow states for the chosen parameters.

A hydraulic jump inside the channel is represented as a discontinuity joining conjugate depths; its internal roller structure is not resolved. Likewise, the jet and mixing region beyond the vertical outlet wall are outside the one-dimensional GVF model. These limitations distinguish the computed channel profiles from the local rapidly varied flow at the outlet.
