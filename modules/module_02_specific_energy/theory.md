# Specific Energy in Open-Channel Flow

*Theory — Module 02 · Based on the five pages of the supplied handwritten lecture notes (original pages 5–9).*

## 1. Definition of specific energy

The **specific energy** of an open-channel flow at a cross-section is the hydraulic head measured with respect to the lowest point of that cross-section (the local channel bottom). For a steady flow, its expression is

$$
\boxed{E=h+\frac{\alpha V^2}{2g}}
$$

where $h$ is the flow depth measured from the lowest point of the cross-section, $V$ is the cross-sectional mean velocity, $g$ is gravitational acceleration, and $\alpha$ is the kinetic-energy correction coefficient. The first term is the **piezometric (hydrostatic) head**, and the second term is the **kinetic head** of the flow at the cross-section.

Using continuity, $V=Q/A(h)$, the same expression becomes

$$
\boxed{E(h,Q)=h+\frac{\alpha Q^2}{2gA^2(h)}}.
$$

Here $A(h)$ is the wetted cross-sectional area, which depends on the flow depth and the channel geometry. At a **given discharge** $Q=\mathrm{constant}$, the energy is a function of depth alone:

$$
E(h)=h+\frac{\alpha Q^2}{2gA^2(h)},
\qquad f(h,E,Q)=E-h-\frac{\alpha Q^2}{2gA^2(h)}=0.
$$

The notes first investigate how $E$ changes with $h$ for a fixed discharge, and subsequently how the discharge changes with $h$ for a fixed energy.

### 1.1 Limiting behaviour and asymptotes

For a regular open-channel cross-section, $A(h)\to0$ as $h\to0^+$. If $Q>0$, the kinetic term diverges:

$$
\lim_{h\to0^+}E(h)
=\lim_{h\to0^+}\left[h+\frac{\alpha Q^2}{2gA^2(h)}\right]
=0+\infty=+\infty.
$$

Thus **$h=0$ is a vertical asymptote** of the specific-energy curve for a nonzero discharge.

As $h\to\infty$, provided the wetted area increases without bound, the kinetic term tends to zero:

$$
\lim_{h\to\infty}E(h)
=\lim_{h\to\infty}\left[h+\frac{\alpha Q^2}{2gA^2(h)}\right]
=\infty+0=\infty.
$$

Dividing by $h$ gives

$$
\lim_{h\to\infty}\frac{E(h)}{h}
=\lim_{h\to\infty}\left[1+\frac{\alpha Q^2}{2ghA^2(h)}\right]=1.
$$

Moreover,

$$
\lim_{h\to\infty}\bigl[E(h)-h\bigr]
=\lim_{h\to\infty}\frac{\alpha Q^2}{2gA^2(h)}=0.
$$

Consequently, the line $\boxed{E=h}$ is an **oblique asymptote** at large depths. The energy curve approaches this line from above, because the kinetic head is nonnegative.

<!-- GRAPH_E_H -->

## 2. Minimum specific energy and critical depth

For a fixed discharge $Q$, the specific-energy curve decreases from infinity, reaches a minimum, and then increases. Its minimum occurs at the **critical depth**, denoted throughout this module by $h_c$.

$$
\boxed{\left.\frac{dE}{dh}\right|_{h=h_c}=0}.
$$

Starting from

$$
E(h)=h+\frac{\alpha Q^2}{2g}A^{-2}(h),
$$

and taking $Q$ and $\alpha$ as constant when differentiating, we obtain

$$
\begin{aligned}
\frac{dE}{dh}
&=1+\frac{\alpha Q^2}{2g}\frac{d}{dh}\left[A^{-2}(h)\right]\\
&=1+\frac{\alpha Q^2}{2g}\left[-2A^{-3}(h)\frac{dA}{dh}\right]\\
&=1-\frac{\alpha Q^2}{gA^3(h)}\frac{dA}{dh}.
\end{aligned}
$$

An infinitesimal increase in water level $dh$ adds a thin strip of area of width $B(h)$, where $B(h)$ is the **top width** of the free surface. Therefore,

$$
\boxed{\frac{dA(h)}{dh}=B(h)}.
$$

Substituting this geometrical identity yields

$$
\frac{dE}{dh}=1-\frac{\alpha Q^2 B(h)}{gA^3(h)}.
$$

At the minimum, $dE/dh=0$, so

$$
1-\frac{\alpha Q^2 B(h_c)}{gA^3(h_c)}=0,
$$

and the **critical-flow condition** is

$$
\boxed{\frac{A^3(h_c)}{B(h_c)}=\frac{\alpha Q^2}{g}}.
$$

This relation applies to an arbitrary open-channel cross-section, under the stated assumptions.

## 3. Critical velocity, critical energy and flow regimes

At the critical depth, continuity gives the critical mean velocity:

$$
\boxed{V_c=\frac{Q}{A(h_c)}}.
$$

Rearrange the critical-flow condition:

$$
\frac{A^3(h_c)}{B(h_c)}=\frac{\alpha Q^2}{g}
\quad\Longrightarrow\quad
\frac{Q^2}{A^2(h_c)}=\frac{g}{\alpha}\frac{A(h_c)}{B(h_c)}.
$$

The **hydraulic depth** is defined as

$$
D(h)=\frac{A(h)}{B(h)},
\qquad D_c=\frac{A(h_c)}{B(h_c)}.
$$

Hence,

$$
\boxed{V_c=\sqrt{\frac{g}{\alpha}\frac{A(h_c)}{B(h_c)}}
=\sqrt{\frac{gD_c}{\alpha}}}.
$$

The corresponding minimum specific energy is

$$
E_c=h_c+\frac{\alpha V_c^2}{2g}.
$$

Substituting the critical-velocity expression, without skipping the intermediate step,

$$
\begin{aligned}
E_c
&=h_c+\frac{\alpha}{2g}\left(\frac{gD_c}{\alpha}\right)\\
&=h_c+\frac{D_c}{2}\\
&=\boxed{h_c+\frac{A(h_c)}{2B(h_c)}}.
\end{aligned}
$$

For a **rectangular channel**, $A=Bh$ and $D=A/B=h$. Consequently $D_c=h_c$ and

$$
\boxed{E_c=E_{\min}=\frac32h_c}.
$$

### 3.1 Critical, subcritical and supercritical flow

The generalised Froude number consistent with the retained kinetic-energy coefficient is

$$
Fr_\alpha=\frac{\sqrt{\alpha}\,V}{\sqrt{gD}}.
$$

Thus the minimum-energy condition is $Fr_\alpha=1$. For the standard module assumption $\alpha=1$, this reduces to the familiar

$$
\boxed{Fr=\frac{V}{\sqrt{gD}}}.
$$

The three regimes, as represented in the notes, are:

- **Subcritical:** $Fr<1$, $V<V_c$ in the usual fixed-discharge interpretation, and $h>h_c$.
- **Critical:** $Fr=1$ and $h=h_c$.
- **Supercritical:** $Fr>1$, $V>V_c$ in the usual fixed-discharge interpretation, and $h<h_c$.

The velocity comparisons here refer to the same channel geometry and discharge, with $\alpha=1$ and the usual monotonic geometry assumptions. The most reliable general criterion is the Froude number itself.

## 4. Discharge as a function of depth at constant specific energy

The notes next reverse the question: instead of keeping $Q$ constant and changing $h$, **keep the specific energy $E$ fixed** and determine the discharge compatible with each depth.

Start again from

$$
E=h+\frac{\alpha Q^2}{2gA^2(h)}.
$$

Isolate the kinetic term:

$$
E-h=\frac{\alpha Q^2}{2gA^2(h)}.
$$

Then

$$
Q^2=A^2(h)\frac{2g(E-h)}{\alpha},
$$

and, for nonnegative discharge,

$$
\boxed{Q(h;E)=A(h)\sqrt{\frac{2g(E-h)}{\alpha}}}.
$$

For a given $E>0$, physical depths satisfy $0\le h\le E$. At the endpoints,

$$
Q=0\quad\text{at}\quad h=0\quad\bigl(A(0)=0\bigr),
$$

and

$$
Q=0\quad\text{at}\quad h=E\quad\bigl(E-h=0\bigr).
$$

Between these endpoints, the discharge is positive, so it must attain a maximum. The notes derive its location by setting

$$
\boxed{\left.\frac{dQ}{dh}\right|_{E=\mathrm{constant}}=0}.
$$

Differentiate the discharge expression, keeping $E$ and $\alpha$ constant:

$$
\begin{aligned}
\frac{dQ}{dh}
&=\frac{dA}{dh}\sqrt{\frac{2g(E-h)}{\alpha}}\\
&\quad+A(h)\frac12\left[\frac{2g(E-h)}{\alpha}\right]^{-1/2}
\left(-\frac{2g}{\alpha}\right)=0.
\end{aligned}
$$

Multiply by $\sqrt{2g(E-h)/\alpha}$ to eliminate the denominator:

$$
\frac{dA}{dh}\frac{2g(E-h)}{\alpha}-\frac{A(h)g}{\alpha}=0.
$$

Using $dA/dh=B(h)$,

$$
B(h)\frac{2g(E-h)}{\alpha}-\frac{A(h)g}{\alpha}=0.
$$

Multiply by $\alpha/g$:

$$
\boxed{2B(h)(E-h)-A(h)=0}.
$$

Therefore, at maximum discharge,

$$
\boxed{E=h+\frac12\frac{A(h)}{B(h)}=h+\frac{D(h)}2}.
$$

This is precisely the minimum-energy condition obtained earlier, now reached from a different constraint.

<!-- GRAPH_H_Q -->

## 5. Equivalence of minimum energy and maximum discharge

The two preceding derivations establish the same critical condition:

$$
\boxed{\begin{aligned}
Q=\mathrm{constant}:&\quad E=E_{\min}\text{ at }h=h_c,\\
E=\mathrm{constant}:&\quad Q=Q_{\max}\text{ at }h=h_c.
\end{aligned}}
$$

At either critical state,

$$
\boxed{E_c=h_c+\frac{D_c}{2}}.
$$

In a rectangular channel, $D_c=h_c$, giving again

$$
\boxed{E_c=\frac32h_c}.
$$

The critical depth is therefore the common boundary between the subcritical and supercritical branches of both graphical representations.

### 5.1 Family of $E$–$h$ curves and critical locus

For a rectangular channel with $\alpha=1$, define the **specific discharge**

$$
\boxed{q=\frac QB}.
$$

Then

$$
\boxed{E(h;q)=h+\frac{q^2}{2gh^2}}.
$$

Each value of $q$ gives a different energy–depth curve. Its minimum occurs at

$$
\boxed{h_c=\left(\frac{q^2}{g}\right)^{1/3}}
$$

and the minimum-energy points of the entire family lie on the **critical locus**

$$
\boxed{E_c=\frac32h_c}.
$$

At any assigned energy $E>E_{\min}$, the energy–depth curve has two intersections with the horizontal level $E$: one at $h<h_c$ (supercritical) and the other at $h>h_c$ (subcritical). These are called **alternate depths**.

### 5.2 Family of $h$–$q$ curves at constant energy

For the same rectangular channel, solve the energy equation for specific discharge:

$$
\boxed{q(h;E)=h\sqrt{2g(E-h)}}.
$$

At a fixed $E$, this curve begins at $q=0$ for $h=0$, returns to $q=0$ at $h=E$, and reaches its maximum at the critical state. The maximum occurs at

$$
h_c=\frac{2E}{3}.
$$

Using the critical condition,

$$
\boxed{q_{\max}=\sqrt{gh_c^3}
=\sqrt{g\left(\frac{2E}{3}\right)^3}}.
$$

The maxima of the family of constant-energy curves lie on the **critical locus** in the $h$–$q$ plane:

$$
\boxed{q_c=\sqrt{gh_c^3}}.
$$

A vertical line at a prescribed $q<q_{\max}$ intersects the curve at two depths, corresponding to the same alternate depths identified on the $E$–$h$ plot.

## 6. Connection to the numerical exercises

The theory above uses a general cross-section and retains $\alpha$ where it appears in the original derivations. In the **Toy** and **Exercise** sections of this module, we work with a rectangular cross-section and take $\alpha=1$:

$$
A=Bh,\qquad q=\frac QB,\qquad
E=h+\frac{q^2}{2gh^2},\qquad
Fr=\frac{q}{\sqrt{gh^3}}.
$$

These equations underlie the four exercise types: (1) two depths for a given energy; (2) flow regime and alternate depth; (3) change of specific discharge at constant energy; and (4) change of energy at constant specific discharge. In all cases, the selected physical branch and the critical condition must be checked.

---


