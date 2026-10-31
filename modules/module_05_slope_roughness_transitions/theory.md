# Changes in Bed Slope and Roughness

*Two infinitely long prismatic reaches connected by a change in bed slope or resistance. Transcription and explanatory English text based on the 16-page handwritten notes (original manuscript pages 32–47). Schematic profiles are displayed alongside the cases by `theory.py`.*

## 1. Reference conditions and notation

Let sections 1 and 3 be infinitely far upstream and downstream, and let section 2 denote the transition. The discharge $Q$ and the cross-sectional geometry are fixed. The normal depths in the two reaches are $y_{0,1}$ and $y_{0,2}$; $y_c$ denotes the critical depth in the original notes (the manuscript uses $K$ for critical depth). The Strickler coefficient is denoted by $K_s$.

The critical condition is written in the notes as

$$
\frac{A^3(y_c)}{T(y_c)}=\frac{Q^2}{g}\quad\longrightarrow\quad y_c,
$$

where $T(y)$ is the free-surface top width. For a rectangular channel of width $b$, this becomes $y_c=(Q^2/(gb^2))^{1/3}$.

For uniform flow,

$$
Q=A(y_0)K_s R(y_0)^{2/3}\sqrt{S_0},
$$

where $S_0$ is the positive bed slope, $R=A/P$ is the hydraulic radius, and $P$ is the wetted perimeter. At fixed discharge and geometry, a larger $K_s\sqrt{S_0}$ produces a smaller normal depth.

The classification used throughout is

$$
\begin{aligned}
y_0>y_c &\quad\Longleftrightarrow\quad S_0<S_c\quad\text{(mild)},\\
y_0<y_c &\quad\Longleftrightarrow\quad S_0>S_c\quad\text{(steep)}.
\end{aligned}
$$

The original manuscript uses $S_c$ to denote the critical slope. All schematic conclusions below concern idealized profiles and the direction in which boundary conditions can influence the flow.

## 2. Changes in bed slope

### 2.1 Mild-to-steep slope (manuscript page 32)

Assume

$$S_{0,1}<S_c,\qquad S_{0,2}>S_c.$$

The critical depth $y_c$ is unchanged because $Q$ and the section are unchanged. The uniform-flow relation gives

$$y_{0,1}>y_c,\qquad y_{0,2}<y_c.$$

The slope break at section 2 is a critical control, at which the idealized depth reaches $y_c$. Upstream of section 2, the water surface follows an **M2** drawdown profile, approaching $y_{0,1}$ far upstream. Downstream, it follows an **S2** profile, approaching $y_{0,2}$ far downstream.

**boundary condition:** $y(2)=y_c$.

The notes emphasize two points: imposing separate normal-flow boundary conditions at both infinities does not create an independent control at the transition; and the gradually varied profiles must meet the critical condition at the common point. The critical passage is an idealization of a local transition.


<!-- PROFILE_FIGURE:slope_mild_steep -->

### 2.2 Mild-to-mild slope: first ordering (manuscript page 33)

Assume

$$S_{0,1}<S_{0,2}<S_c.$$

The uniform-flow equation gives

$$y_{0,1}>y_c,\qquad y_{0,2}>y_c,\qquad y_{0,1}>y_{0,2}.$$

both reaches are subcritical, so information propagates upstream. The downstream reach is uniform at $y_{0,2}$; this condition at section 2 controls the upstream adjustment. The upstream profile is an **M2** curve connecting $y_{0,1}$ to $y_{0,2}$.

**boundary condition:** $y(2)=y_{0,2}$.


<!-- PROFILE_FIGURE:slope_mild_mild_decrease -->

### 2.3 Mild-to-mild slope: reverse ordering (manuscript page 34)

Assume

$$S_{0,2}<S_{0,1}<S_c.$$

Then

$$y_{0,1}>y_c,\qquad y_{0,2}>y_c,\qquad y_{0,1}<y_{0,2}.$$

Again, the downstream normal depth controls the solution. The upstream adjustment is an **M1** backwater profile, approaching $y_{0,1}$ upstream.

**boundary condition:** $y(2)=y_{0,2}$.


<!-- PROFILE_FIGURE:slope_mild_mild_increase -->

### 2.4 Steep-to-steep slope: first ordering (manuscript page 35)

Assume

$$S_{0,1}>S_{0,2}>S_c.$$

both reaches are supercritical:

$$y_{0,1}<y_c,\qquad y_{0,2}<y_c,\qquad y_{0,1}<y_{0,2}.$$

Supercritical flow carries the upstream condition downstream. The upstream reach is uniform; in the downstream reach an **S3** profile adjusts from $y_{0,1}$ toward $y_{0,2}$.

**boundary condition:** $y(2)=y_{0,1}$.


<!-- PROFILE_FIGURE:slope_steep_steep_decrease -->

### 2.5 Steep-to-steep slope: reverse ordering (manuscript page 35)

Assume

$$S_{0,2}>S_{0,1}>S_c.$$

Consequently,

$$y_{0,1}<y_c,\qquad y_{0,2}<y_c,\qquad y_{0,1}>y_{0,2}.$$

The upstream reach is uniform, and the downstream adjustment is an **S2** profile.

**boundary condition:** $y(2)=y_{0,1}$.


<!-- PROFILE_FIGURE:slope_steep_steep_increase -->

## 3. Changes in roughness (manuscript pages 36–38)

Here the bed slope $S_0$ is unchanged while the Strickler coefficient changes from $K_{s,1}$ to $K_{s,2}$. The normal-flow equations are

$$
Q=A(y_{0,1})K_{s,1}R(y_{0,1})^{2/3}\sqrt{S_0}
=A(y_{0,2})K_{s,2}R(y_{0,2})^{2/3}\sqrt{S_0}.
$$

The critical depth $y_c$ remains unchanged. A larger Strickler coefficient means less resistance and a smaller normal depth:

$$
K_{s,1}<K_{s,2}\quad\Longrightarrow\quad y_{0,1}>y_{0,2}.
$$

### 3.1 Mild channel; roughness decreases downstream (manuscript page 36)

For $S_0<S_c$ in both reaches and $K_{s,1}<K_{s,2}$,

$$
y_{0,1}>y_c,\qquad y_{0,2}>y_c,\qquad y_{0,1}>y_{0,2}.
$$

The downstream normal depth controls the upstream **M2** adjustment.

**boundary condition:** $y(2)=y_{0,2}$.


<!-- PROFILE_FIGURE:rough_mild_decrease -->

### 3.2 Mild channel; roughness increases downstream (manuscript page 36)

For $S_0<S_c$ in both reaches and $K_{s,1}>K_{s,2}$,

$$
y_{0,1}>y_c,\qquad y_{0,2}>y_c,\qquad y_{0,1}<y_{0,2}.
$$

The upstream profile is **M1** and the downstream reach is uniform.

**boundary condition:** $y(2)=y_{0,2}$.


<!-- PROFILE_FIGURE:rough_mild_increase -->

### 3.3 Steep channel; roughness increases downstream (manuscript page 37)

For $S_0>S_c$ in both reaches and $K_{s,1}>K_{s,2}$,

$$
y_{0,1}<y_c,\qquad y_{0,2}<y_c,\qquad y_{0,1}<y_{0,2}.
$$

The upstream normal depth controls a downstream **S3** adjustment.

**boundary condition:** $y(2)=y_{0,1}$.


<!-- PROFILE_FIGURE:rough_steep_increase -->

### 3.4 Steep channel; roughness decreases downstream (manuscript page 37)

For $S_0>S_c$ in both reaches and $K_{s,1}<K_{s,2}$,

$$
y_{0,1}<y_c,\qquad y_{0,2}<y_c,\qquad y_{0,1}>y_{0,2}.
$$

The upstream normal depth controls a downstream **S2** adjustment.

**boundary condition:** $y(2)=y_{0,1}$.


<!-- PROFILE_FIGURE:rough_steep_decrease -->

### 3.5 Why the uniform-flow equation gives similar effects (manuscript page 38)

The original notes explicitly regroup the uniform-flow relation as

$$
Q=\underbrace{A(y_0)R(y_0)^{2/3}}_{\text{geometry-dependent function of }y_0}
\underbrace{K_s\sqrt{S_0}}_{\text{combined resistance/slope factor}}.
$$

Thus $K_s$ and $\sqrt{S_0}$ have the **same effect on the normal depth** when the discharge and section are fixed. This statement concerns the normal-flow equation, not the geometry of the bed or the spatial shape of the free-surface profile.

## 4. Steep-to-mild transition and hydraulic jump (manuscript pages 39–41)

For a change from steep to mild,

$$
S_{0,1}>S_c,\qquad S_{0,2}<S_c,
$$

and hence

$$
y_{0,1}<y_c,\qquad y_{0,2}>y_c.
$$

The upstream flow is supercritical, while the downstream normal flow is subcritical. The original notes indicate an upstream boundary condition at section 1 and a downstream boundary condition at section 3. Neither can propagate through the other regime by a single gradually varied profile. A **hydraulic jump** is therefore required in the depicted configuration.

A hydraulic jump is a rapidly varied transition in which the free surface is discontinuous on the scale of a gradually varied flow model. The jump position must satisfy a compatibility condition involving the upstream and downstream profiles and the conjugate-depth relation.

### 4.1 Specific-force matching at a candidate jump section (manuscript pages 39–41)

The notes write the jump condition in the form

$$
\Sigma(y_U,\bar Q)=\Sigma(y_D,\bar Q),
$$

where $y_U$ and $y_D$ are the depths immediately upstream and downstream of the jump, and $\bar Q$ is the given discharge. The original handwritten symbol resembles $\bar Q$; it is retained here to distinguish the prescribed discharge from the discharge variable used in the sketches.

For a prismatic section, the specific-force function is

$$
\Sigma(y,\bar Q)=y_G(y)A(y)+\frac{\bar Q^2}{gA(y)},
$$

where $y_G$ is the depth of the centroid of the wetted section below the free surface. The original pages 40–41 compare the values of $\Sigma$ associated with the two normal depths and distinguish three possibilities:

$$
\begin{array}{ll}
\text{Case 1:}&\Sigma(y_{0,1},\bar Q)=\Sigma(y_{0,2},\bar Q),\\[2pt]
\text{Case 2:}&\Sigma(y_{0,1},\bar Q)>\Sigma(y_{0,2},\bar Q),\\[2pt]
\text{Case 3:}&\Sigma(y_{0,1},\bar Q)<\Sigma(y_{0,2},\bar Q).
\end{array}
$$

In the first case the jump can occur at the slope change, provided the conjugate-depth condition is satisfied. In the second and third cases the jump moves to the downstream or upstream reach, respectively, so that the depths at its location satisfy the specific-force equality. The accompanying handwritten sketches show the specific-force curve and the relative positions of the normal depths and the critical depth.


**Case 1 — Equal specific forces:** the upstream and downstream points lie at the same height on the specific-force curve.

<!-- PROFILE_FIGURE:specific_force_case_1 -->

**Case 2 — Upstream specific force greater:** the upstream point lies above the downstream point on the specific-force curve.

<!-- PROFILE_FIGURE:specific_force_case_2 -->

**Case 3 — Upstream specific force smaller:** the upstream point lies below the downstream point on the specific-force curve.

<!-- PROFILE_FIGURE:specific_force_case_3 -->

<!-- PROFILE_FIGURE:jump_cases -->

## 5. Momentum balance for the hydraulic jump (manuscript pages 42–44)

The notes next derive the jump condition from the integral balance of momentum for a control volume enclosing the jump. Their starting point is the vector equilibrium

$$
\vec G+\vec\Pi_{p,U}+\vec\Pi_{\mu,U}
+\vec\Pi_{p,D}+\vec\Pi_{\mu,D}
+\vec\Pi_{p,b}+\vec\Pi_{\mu,b}
+\vec M_U+\vec M_D=\vec 0.
$$

Here $\vec G$ is the weight, $\vec\Pi_p$ represents pressure forces, $\vec\Pi_\mu$ viscous forces, and $\vec M$ momentum-flux contributions; the subscripts $U$, $D$, and $b$ denote upstream, downstream, and bed/boundary terms.

Projecting in the flow direction $\hat s$ gives the component contributions indicated in the notes:

$$
\vec G\cdot\hat s=\gamma W\,S_0,
$$

$$
\vec\Pi_{p,U}\cdot\hat s=p_U A_U,
\qquad
\vec\Pi_{\mu,U}\cdot\hat s\simeq0,
$$

$$
\vec\Pi_{p,D}\cdot\hat s=-p_D A_D,
\qquad
\vec\Pi_{\mu,D}\cdot\hat s\simeq0,
$$

$$
\vec\Pi_{p,b}\cdot\hat s\simeq0,
\qquad
\vec\Pi_{\mu,b}\cdot\hat s=-\tau_b P_b,
$$

$$
\vec M_U\cdot\hat s=\frac{\rho Q^2}{A_U},
\qquad
\vec M_D\cdot\hat s=-\frac{\rho Q^2}{A_D}.
$$

Combining these terms, and expressing the hydrostatic pressure forces by their centroid depths, gives

$$
\gamma W S_0+\gamma y_{G,U}A_U+\frac{\rho Q^2}{A_U}
-\tau_b P_b-\gamma y_{G,D}A_D-\frac{\rho Q^2}{A_D}=0.
$$

Grouping the upstream and downstream specific-force terms:

$$
\underbrace{y_{G,U}A_U+\frac{Q^2}{gA_U}}_{\Sigma_U}
-\underbrace{y_{G,D}A_D+\frac{Q^2}{gA_D}}_{\Sigma_D}
=\frac{\tau_b P_b}{\gamma}-Wi.
$$

The manuscript subsequently estimates the order of the neglected terms using a characteristic depth $y_c$, channel width $b$, and jump length $L$:

$$
W\sim KBL,\qquad P_b\sim bL,
$$

and notes that a typical bed slope is small, $S_0\sim10^{-3}$, while $L$ is only several characteristic depths. The corresponding bed-friction and weight terms are small compared with the main momentum terms, leading to

$$
\boxed{\Sigma_U\simeq\Sigma_D}.
$$

This is an approximation for a short jump, not an exact energy-conservation law.

## 6. Rectangular-channel conjugate-depth derivation (manuscript page 45)

Assume a rectangular channel of width $b$ and momentum correction factors $\alpha=\beta=1$, as written in the notes. Let $y_U$ and $y_D$ denote the depths immediately before and after the jump.

The equality of specific force is

$$
\Sigma(y_U,\bar Q)=\Sigma(y_D,\bar Q),
$$

with

$$
\Sigma=y_GA+\frac{\bar Q^2}{gA},
\qquad y_G=\frac y2,\quad A=bh.
$$

Therefore,

$$
\frac{y_U}{2}by_U+\frac{\bar Q^2}{gby_U}
=\frac{y_D}{2}by_D+\frac{\bar Q^2}{gby_D}.
$$

The notes recall the critical condition

$$
\frac{A^3(y_c)}{T(y_c)}=\frac{\bar Q^2}{g},
$$

which for the rectangular section gives

$$
\frac{b^3y_c^3}{b}=\frac{\bar Q^2}{g},
\qquad
\bar Q^2=gb^2y_c^3.
$$

Substitution into the momentum equality yields

$$
\frac12 by_U^2+\frac{gb^2y_c^3}{gby_U}
=\frac12 by_D^2+\frac{gb^2y_c^3}{gby_D},
$$

$$
\frac{y_U^2}{2}+\frac{y_c^3}{y_U}
=\frac{y_D^2}{2}+\frac{y_c^3}{y_D},
$$

$$
\frac{y_D^2-y_U^2}{2}
=y_c^3\left(\frac1{y_U}-\frac1{y_D}\right),
$$

$$
\frac{(y_D-y_U)(y_D+y_U)}{2}
=y_c^3\frac{y_D-y_U}{y_Dy_U}.
$$

For a nontrivial jump $y_D\ne y_U$, division by $y_D-y_U$ gives the final handwritten relation:

$$
\boxed{y_D+y_U=\frac{2y_c^3}{y_Dy_U}}.
$$

## 7. Energy dissipation across the jump (manuscript pages 46–47)

The notes ask whether the jump is highly dissipative. For two sections at approximately the same bed elevation, they define

$$
\Delta E=E_U-E_D,
$$

where the rectangular-channel specific energy is

$$
E(y)=y+\frac{\bar Q^2}{2gb^2y^2}.
$$

Substitution gives

$$
\Delta E=
\left(y_U+\frac{\bar Q^2}{2gb^2y_U^2}\right)
-\left(y_D+\frac{\bar Q^2}{2gb^2y_D^2}\right),
$$

$$
\Delta E=(y_U-y_D)
+\frac{\bar Q^2}{2gb^2}\left(\frac1{y_U^2}-\frac1{y_D^2}\right),
$$

$$
\Delta E=-(y_D-y_U)
+\frac{\bar Q^2}{2gb^2}\frac{y_D^2-y_U^2}{y_D^2y_U^2},
$$

$$
\Delta E=-(y_D-y_U)
+\frac{gb^2y_c^3}{2gb^2}
\frac{(y_D-y_U)(y_D+y_U)}{y_D^2y_U^2},
$$

$$
\Delta E=-(y_D-y_U)
+\frac{y_c^3}{2}\frac{(y_D-y_U)(y_D+y_U)}{y_D^2y_U^2}.
$$

Using the conjugate-depth relation $y_c^3=y_Dy_U(y_D+y_U)/2$ gives

$$
\Delta E=-(y_D-y_U)
+\frac{y_Dy_U(y_D+y_U)}{4}
\frac{(y_D-y_U)(y_D+y_U)}{y_D^2y_U^2},
$$

$$
\Delta E=(y_D-y_U)
\left[-1+\frac{(y_D+y_U)^2}{4y_Dy_U}\right],
$$

$$
\Delta E=(y_D-y_U)
\left[\frac{-4y_Dy_U+y_U^2+y_D^2+2y_Dy_U}{4y_Dy_U}\right],
$$

$$
\Delta E=(y_D-y_U)
\left[\frac{y_U^2+y_D^2-2y_Dy_U}{4y_Dy_U}\right],
$$

$$
\boxed{\Delta E=\frac{(y_D-y_U)^3}{4y_Dy_U}}.
$$

The final page of the notes gives the order-of-magnitude estimates

$$
O(E)=y_c,\qquad O(y_D)-O(y_U)\sim y_c,\qquad O(\Delta E)=y_c.
$$

Thus the energy loss is not negligible in general. The manuscript closes by contrasting the two approaches:

**Energetic approach**

$$
E_U-E_D=\Delta E,
\qquad O(y_c)-O(y_c)=O(y_c).
$$

The right-hand side cannot be discarded when the jump is appreciable.

**Mechanical (momentum) approach**

$$
\Sigma_U-\Sigma_D=RjA_b-Wi,
$$

where the manuscript denotes the small bed-resistance contribution by $RjA_b$. The accompanying order estimate is

$$
O(y_c^2)-O(y_c^2)=O\!\left(\frac{6y_c^2}{100}\right).
$$

This term is comparatively small in the idealized short-jump momentum balance, so the leading-order result is $\Sigma_U\simeq\Sigma_D$.

---

**Transcription notes requiring confirmation before publication.** The handwritten momentum-force symbols on manuscript pages 42–43 and the last order estimate on page 47 are faint. They have been transcribed in a consistent notation, but should be checked against the author's intended symbols. The notes' use of $K$ for *critical depth* has been converted to $y_c$ and distinguished from $K_s$ for Strickler roughness. The manuscript equations have been retained; the new schematic plots are illustrative and do not replace the derivations.
