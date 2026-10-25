# Governing equation

For steady, gradually varied flow in a prismatic channel, let $s$ increase downstream, $i$ be the bed slope, and $j$ be the friction slope.

The handwritten notes begin from the energy equation:

$$
\frac{dE}{ds}=i-j
$$

At constant discharge, specific energy depends on depth $h$. The chain rule gives

$$
\frac{dE}{ds}=\frac{dE}{dh}\frac{dh}{ds}
$$

and therefore

$$
\boxed{\frac{dh}{ds}=\frac{i-j}{dE/dh}}
$$

For a rectangular channel,

$$
E(h)=h+\frac{Q^2}{2gb^2h^2},
\qquad
\frac{dE}{dh}=1-Fr^2
$$

so that

$$
\boxed{\frac{dh}{ds}=\frac{i-j}{1-Fr^2}}
$$

**Notation:** These notes use $h$ for depth, $k$ for critical depth, and $h_0$ for normal depth. The Toy uses $y$, $y_c$ and $y_n$ respectively.

*Source: handwritten notes, PDF p. 1 (manuscript p. 20).*

---

# Specific energy and characteristic depths

For fixed discharge, the specific-energy curve has a minimum at critical depth $k$:

$$
\left.\frac{dE}{dh}\right|_{h=k}=0,\qquad Fr=1
$$

For a rectangular channel,

$$
k=\left(\frac{Q^2}{gb^2}\right)^{1/3}
$$

With Manning resistance,

$$
A=bh,\quad R=\frac{bh}{b+2h},\quad
j(h)=\left(\frac{nQ}{AR^{2/3}}\right)^2
$$

The normal depth $h_0$ is the uniform-flow solution of

$$
j(h_0)=i
$$

At $h=k$, the denominator of the GVF equation vanishes; at $h=h_0$, its numerator vanishes. These are **different physical conditions**.

*Source: handwritten notes, PDF pp. 1–2.*

<!-- PLOT: energy -->

---

# Signs and asymptotes

The depth gradient follows from the signs of two functions:

$$
\frac{dh}{ds}=\frac{\underbrace{i-j(h)}_{\text{numerator}}}{\underbrace{1-Fr^2(h)}_{\text{denominator}}}
$$

- $h<k$: $1-Fr^2<0$ (supercritical flow).
- $h=k$: $1-Fr^2=0$ (critical condition).
- $h>k$: $1-Fr^2>0$ (subcritical flow).
- $h=h_0$: $i-j=0$ (uniform-flow condition for positive slope).

As $h$ approaches $h_0$, the gradient tends to zero, and the profile approaches uniform flow asymptotically. At $h=k$, the ordinary GVF equation is singular; continuation through this state needs additional physical treatment.

*Source: handwritten notes, PDF pp. 1–2.*

<!-- PLOT: signs -->

---

# Mild-slope channels

A channel is **mild** when

$$
\boxed{h_0>k}
$$

The three profile families are distinguished by depth:

| Profile | Depth interval | Sign of $dh/ds$ | Regime |
|---|---|---|---|
| M1 | $h>h_0>k$ | Positive | Subcritical |
| M2 | $k<h<h_0$ | Negative | Subcritical |
| M3 | $h<k<h_0$ | Positive | Supercritical |

**M1** is a backwater profile above normal depth. **M2** is a drawdown profile between normal and critical depths. **M3** lies below critical depth and is supercritical.

The signs follow from the governing equation, rather than from memorizing the sketches.

*Source: handwritten notes, PDF pp. 3–4.*

---

# Steep-slope channels

A channel is **steep** when

$$
\boxed{h_0<k}
$$

| Profile | Depth interval | Sign of $dh/ds$ | Regime |
|---|---|---|---|
| S1 | $h>k>h_0$ | Positive | Subcritical |
| S2 | $h_0<h<k$ | Negative | Supercritical |
| S3 | $h<h_0<k$ | Positive | Supercritical |

Notice that **S1 is subcritical despite the steep bed**. The classification of the bed and the local flow regime are not the same thing.

The six qualitative profile sketches are shown below.

*Source: handwritten notes, PDF pp. 5–6.*

<!-- PLOT: profiles -->

---

# Horizontal and adverse slopes

The notes also introduce horizontal and adverse-slope channels.

For a **horizontal channel** ($i=0$),

$$
i-j=-j<0
$$

The sign of $dh/ds$ is opposite to that of $dE/dh$. For an **adverse channel** ($i<0$), the numerator is also negative if $j>0$.

Neither case has a finite normal depth satisfying $j=i$ with positive friction losses. The current Toy and Exercise implementations are limited to **positive bed slopes**.

*Source: handwritten notes, PDF pp. 7–8. The adverse-slope page contains only a heading, so this explanation is a short extension of the governing equation.*

---

# Perturbations and boundary conditions

The notes explain how information travels in an open-channel flow. Small disturbances propagate at characteristic velocities $U-c$ and $U+c$, where $U$ is mean flow velocity and $c$ is shallow-water wave celerity.

- In **subcritical flow** ($Fr<1$), disturbances can propagate both upstream and downstream.
- In **supercritical flow** ($Fr>1$), disturbances propagate downstream only.

Consequently, a prescribed water depth must be placed at the hydraulically controlling boundary:

| Regime | Depth prescribed at | Numerical integration |
|---|---|---|
| Subcritical | Downstream | Upstream |
| Supercritical | Upstream | Downstream |

This is why the Toy rejects a depth condition imposed at the wrong end of the reach.

*Source: handwritten notes, PDF pp. 9–12.*

<!-- PLOT: waves -->

---

# Numerical integration of a GVF profile

The handwritten notes explain the qualitative behavior of profiles. To compute them, the app additionally uses the explicit spatial method described in **Defina, §8.2.1**, equations (99)–(101).

The differential equation is

$$
\frac{dh}{ds}=\frac{i-j}{1-Fr^2}
$$

For **subcritical flow**, integrate upstream:

$$
\boxed{h_{i+1}=h_i-\left(\frac{i-j}{1-Fr^2}\right)_i\Delta s}
$$

For **supercritical flow**, integrate downstream:

$$
\boxed{h_{i+1}=h_i+\left(\frac{i-j}{1-Fr^2}\right)_i\Delta s}
$$

Steps must be reduced near critical depth. The ordinary GVF solver should not force a profile across the singular condition $Fr=1$.

*Supplementary reference: Andrea Defina, Profili di moto permanente (2010), §8.2.1.*
