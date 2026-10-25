# Gradually Varied Flow

In this chapter, the gradually varied flow profiles are derived.

## 1. Governing Equation

Consider steady flow at constant discharge $Q$ in a prismatic channel. The coordinate $x$ increases downstream. The flow depth $y=y(x)$ varies sufficiently slowly for the pressure distribution to be approximately hydrostatic. There are no lateral inflows, and the velocity-head coefficient is taken as unity, consistently with the Toy. Bed slopes are sufficiently small to neglect the distinction between vertical depth and depth measured normal to the channel bed.

The mechanical energy equation for steady, gradually varied flow reads as follows:

$$
\frac{dH}{dx}=-S_f,
\qquad
\frac{dz_b}{dx}=-S_0,
\qquad
\boxed{\frac{dE}{dx}=S_0-S_f}.
$$

Since the specific energy $E$ depends on the flow depth $y$ for a given discharge, applying the chain rule yields:

$$
\frac{dE}{dx}=\frac{dE}{dy}\frac{dy}{dx},
\qquad
\boxed{\frac{dy}{dx}=\frac{S_0-S_f}{dE/dy}}.
$$

This is a first-order ordinary differential equation governing the water-surface profile, which can be solved numerically subject to an appropriate boundary condition.

To understand the qualitative behavior of the solutions to this ODE, we need to examine the signs of its numerator and denominator. Together, they determine the sign of the water-depth gradient along the streamwise direction and, consequently, whether the water-surface profile increases or decreases downstream.

### The Numerator: Bed Slope and Friction Slope

The numerator of the gradually varied flow equation is given by $S_0-S_f$, where $S_0$ is the bed slope and $S_f$ is the friction slope.

For a rectangular channel, the friction slope can be evaluated using Manning's equation:

$$
S_f(y)=\left(\frac{nQ}{A(y)R(y)^{2/3}}\right)^2,
$$

where $A=by$ is the flow area and $R=A/(b+2y)$ is the hydraulic radius.

For a given discharge and channel geometry, the friction slope decreases as the flow depth increases, whereas the bed slope remains constant.

The **normal depth** $y_0$ is defined by the condition

$$
S_f(y_0)=S_0.
$$

At this depth, the numerator vanishes, corresponding to uniform flow when the denominator is nonzero.

[[numerator]]

Three cases can therefore be distinguished:

- For $y<y_0$, the friction slope exceeds the bed slope ($S_f>S_0$), and the numerator is **negative**: $S_0-S_f<0$.
- For $y=y_0$, the two slopes are equal ($S_f=S_0$), and the numerator is **zero**: $S_0-S_f=0$.
- For $y>y_0$, the friction slope is smaller than the bed slope ($S_f<S_0$), and the numerator is **positive**: $S_0-S_f>0$.

Therefore, the normal depth separates the regions of positive and negative numerator. Combining this result with the sign of the denominator allows us to determine whether the flow depth increases or decreases in the downstream direction.

### The Denominator: Specific Energy

To determine the sign of the denominator, we examine how the specific energy varies with flow depth. For a rectangular channel, assuming a constant discharge $Q$, the specific energy is

$$
\begin{aligned}
E &= y+\frac{Q^2}{2gb^2y^2} \\
  &= y+\frac{q^2}{2gy^2},
\end{aligned}
$$

where $q=Q/b$ is the discharge per unit width.

[[SPECIFIC_ENERGY_PLOT]]

Differentiating with respect to $y$ gives

$$
\begin{aligned}
\frac{dE}{dy} &= 1-\frac{q^2}{gy^3} \\
              &= \boxed{1-\mathrm{Fr}^2},
\end{aligned}
$$

where $\mathrm{Fr}$ is the Froude number.

The specific-energy curve reaches its minimum at the **critical depth** $y_c$, where $\mathrm{Fr}=1$ and $dE/dy=0$.

For **supercritical flow** ($y<y_c$, $\mathrm{Fr}>1$), the derivative $dE/dy$ is negative: specific energy decreases as flow depth increases.

For **critical flow** ($y=y_c$, $\mathrm{Fr}=1$), the specific energy reaches its minimum and $dE/dy=0$. Consequently, the denominator of the gradually varied flow equation vanishes. If $S_0-S_f\neq 0$, the water-depth gradient $dy/dx$ becomes unbounded as the critical depth is approached, and the differential equation is singular at this point.

For **subcritical flow** ($y>y_c$, $\mathrm{Fr}<1$), the derivative $dE/dy$ is positive: specific energy increases as flow depth increases.

Thus, the sign of the denominator in the gradually varied flow equation is determined entirely by the flow regime, while the critical depth separates the two branches of the specific-energy curve.

## M Profiles — Mild Slope

For a **mild slope**, the normal depth is larger than the critical depth:

$$
\boxed{y_0>y_c},\qquad S_0>0.
$$

Using the downstream coordinate $x$ and the flow depth $y$, the gradually varied flow (GVF) equation is

$$
\boxed{\frac{dy}{dx}=\frac{S_0-S_f(y)}{dE/dy}
=\frac{S_0-S_f(y)}{1-\mathrm{Fr}^2}},
$$

For the mild-slope classification, the relevant reference depths are the **normal depth** $y_0$, at which $S_f(y_0)=S_0$, and the **critical depth** $y_c$, at which $dE/dy=1-\mathrm{Fr}^2=0$.

For a rectangular channel with constant width $b$ and discharge $Q$,

$$
A=by,\qquad U=\frac{Q}{by},\qquad
\mathrm{Fr}^2=\frac{U^2}{gy}=\frac{Q^2}{gb^2y^3},
$$

so the mean velocity changes with depth according to

$$
\frac{dU}{dx}=-\frac{Q}{by^2}\frac{dy}{dx}
=-\frac{U}{y}\frac{dy}{dx}.
$$

Therefore, **increasing depth implies decreasing velocity**, and **decreasing depth implies increasing velocity**. In the profile plots, the water surface is blue and the channel bed is brown; the **normal-depth reference is green** and the **critical-depth reference is red**.

### M1 Profile — $y>y_0>y_c$

**1. Sign of the depth gradient**

Because $y>y_0$, the friction slope is smaller than the bed slope. Because $y>y_c$, the flow is subcritical:

$$
\underbrace{S_0-S_f(y)}_{>0},\qquad
\underbrace{\frac{dE}{dy}=1-\mathrm{Fr}^2}_{>0}
\quad\Longrightarrow\quad
\boxed{\frac{dy}{dx}=\frac{+}{+}>0}.
$$

The depth **increases downstream**, while

$$
\frac{dU}{dx}=-\frac{U}{y}\frac{dy}{dx}<0.
$$

Thus M1 represents a **decelerating subcritical flow** in a mild-slope channel.

**2. Upstream limit: approach to normal depth**

As $y\to y_0^+$, friction approaches the bed slope, whereas the specific-energy derivative remains positive:

$$
S_f(y)\to S_0,\qquad
1-\mathrm{Fr}^2(y_0)>0,
$$

$$
\boxed{\frac{dy}{dx}\to0^+}.
$$

The profile approaches the **normal-depth line asymptotically** in the upstream direction. In the autonomous GVF equation this corresponds to $x\to-\infty$; normal depth is not reached at a finite position along a nonuniform M1 solution.

**3. Downstream limit: horizontal water-surface asymptote**

For a very large depth, the wetted area increases and the friction slope decreases. In particular, for fixed $Q$ and $b$,

$$
\lim_{y\to\infty}S_f(y)=0,\qquad
\lim_{y\to\infty}\mathrm{Fr}^2=0,
$$

hence

$$
\boxed{\lim_{y\to\infty}\frac{dy}{dx}
=\frac{S_0-0}{1-0}=S_0}.
$$

The bed elevation $z_b$ satisfies $dz_b/dx=-S_0$. Since the free-surface elevation is $z_w=z_b+y$,

$$
\frac{dz_w}{dx}=\frac{dz_b}{dx}+\frac{dy}{dx}
=-S_0+\frac{dy}{dx}
\longrightarrow -S_0+S_0=0.
$$

**Physical interpretation:** far downstream, the depth grows at almost exactly the rate at which the bed falls. Consequently, the **water surface becomes horizontal** even though the flow depth continues to increase. The free-surface slope therefore tends to zero, yielding a horizontal asymptote.

[[m1]]

### M2 Profile — $y_c<y<y_0$

**1. Sign of the depth gradient**

Here $y<y_0$, so friction exceeds the bed slope; however, $y>y_c$, so the flow remains subcritical:

$$
\underbrace{S_0-S_f(y)}_{<0},\qquad
\underbrace{\frac{dE}{dy}=1-\mathrm{Fr}^2}_{>0}
\quad\Longrightarrow\quad
\boxed{\frac{dy}{dx}=\frac{-}{+}<0}.
$$

The depth **decreases downstream**, and therefore

$$
\frac{dU}{dx}=-\frac{U}{y}\frac{dy}{dx}>0.
$$

Thus M2 is an **accelerating subcritical flow** in a mild-slope channel.

**2. Upstream limit: normal-depth asymptote**

As $y\to y_0^-$,

$$
S_0-S_f(y)\to0^-,\qquad
1-\mathrm{Fr}^2(y_0)>0,
$$

$$
\boxed{\frac{dy}{dx}\to0^-}.
$$

The M2 profile approaches the **normal-depth line asymptotically upstream** ($x\to-\infty$ in the mathematical solution).

**3. Downstream limit: vertical tangent at critical depth**

As $y\to y_c^+$, the specific-energy derivative tends to zero from above, while the numerator remains negative because $y_c<y_0$:

$$
1-\mathrm{Fr}^2\to0^+,\qquad
S_0-S_f(y_c)<0.
$$

Consequently,

$$
\boxed{\frac{dy}{dx}\to-\infty}.
$$

Equivalently, $dx/dy\to0^-$: the curve $y(x)$ develops a **vertical tangent** as it approaches critical depth. This occurs at a finite downstream location for the idealized M2 solution, not necessarily at $x\to+\infty$. The standard GVF equation becomes singular there; the critical point is not crossed smoothly by this equation when its numerator is nonzero.

[[m2]]

### M3 Profile — $0<y<y_c<y_0$

**1. Sign of the depth gradient**

Both numerator and denominator are negative: $y<y_0$ gives $S_f>S_0$, and $y<y_c$ gives $\mathrm{Fr}>1$.

$$
\underbrace{S_0-S_f(y)}_{<0},\qquad
\underbrace{\frac{dE}{dy}=1-\mathrm{Fr}^2}_{<0}
\quad\Longrightarrow\quad
\boxed{\frac{dy}{dx}=\frac{-}{-}>0}.
$$

Therefore,

$$
\frac{dy}{dx}>0,\qquad
\frac{dU}{dx}=-\frac{U}{y}\frac{dy}{dx}<0.
$$

M3 represents a **decelerating supercritical flow** in a mild-slope channel: depth increases and velocity decreases downstream.

**2. Downstream limit: vertical tangent at critical depth**

When $y\to y_c^-$, the denominator tends to zero from below, while the numerator remains negative:

$$
1-\mathrm{Fr}^2\to0^-,\qquad
S_0-S_f(y_c)<0,
$$

$$
\boxed{\frac{dy}{dx}\to+\infty}.
$$

Thus the M3 profile reaches a **vertical tangent** as it approaches critical depth from below. As for M2, the critical point is singular for the standard GVF equation and requires separate physical analysis.

**3. Formal shallow-depth limit and physical limitation**

Extrapolating the M3 profile toward vanishing depth has **no physical meaning all the way to $y=0$**. For a rectangular channel at constant discharge,

$$
U=\frac{Q}{by}
\quad\Longrightarrow\quad
\boxed{\lim_{y\to0^+}U=+\infty}.
$$

Such unbounded velocity is not physically realizable; moreover, the assumptions of gradually varied flow and the resistance model cease to be reliable at sufficiently small depths. The mathematical curve must therefore **not** be interpreted as an actual flow profile down to zero depth.

For completeness, Manning's relation also shows why the friction slope becomes large at small depth:

$$
A=by,\qquad R=\frac{by}{b+2y}\sim y,
\qquad S_f(y)=\left(\frac{nQ}{AR^{2/3}}\right)^2
\sim\frac{n^2Q^2}{b^2y^{10/3}}
\quad(y\to0^+).
$$

This asymptotic result characterizes the idealized resistance model, but does not make the zero-depth limit physically valid.

[[m3]]

## S Profiles — Steep Slope

### General Characteristics of S Profiles

A **steep-slope channel** is characterized by a normal depth smaller than the critical depth:

$$
\boxed{y_0<y_c}.
$$

Uniform flow is therefore supercritical, since $\mathrm{Fr}(y_0)>1$. For steady flow at constant discharge in a prismatic rectangular channel, the governing equation is

$$
\boxed{\frac{dy}{dx}=\frac{S_0-S_f(y)}{1-\mathrm{Fr}^2(y)}}.
$$

The numerator vanishes at $y=y_0$, where $S_f=S_0$, and the denominator vanishes at $y=y_c$, where $\mathrm{Fr}=1$. Because $y_0<y_c$, these depths divide the admissible positive depths into three regions:

- **S1:** $y>y_c>y_0$ — subcritical, decelerating flow.
- **S2:** $y_0<y<y_c$ — supercritical, accelerating flow.
- **S3:** $0<y<y_0<y_c$ — supercritical, decelerating flow.

Here $x$ increases downstream, $y$ is the flow depth, and $U=Q/(by)$ is the mean velocity. For a constant rectangular width $b$,

$$
\frac{dU}{dx}=-\frac{U}{y}\frac{dy}{dx}.
$$

Thus an increasing depth implies decreasing velocity, and vice versa. In the profile plots, **critical depth is red** and **normal depth is green**.

### S1 Profile — $y>y_c>y_0$

**1. Sign of the depth gradient and flow regime**

Since $y>y_0$, the friction slope is smaller than the bed slope; since $y>y_c$, the flow is subcritical:

$$
S_0-S_f(y)>0,\qquad
\frac{dE}{dy}=1-\mathrm{Fr}^2>0.
$$

Consequently,

$$
\boxed{\frac{dy}{dx}=\frac{+}{+}>0},
\qquad
\frac{dU}{dx}=-\frac{U}{y}\frac{dy}{dx}<0.
$$

The S1 profile describes **decelerating subcritical flow**: depth increases and mean velocity decreases downstream in a steep-slope channel.

**2. Upstream limit: vertical tangent at critical depth**

As $y\to y_c^+$, the denominator tends to zero from above. Because $y_c>y_0$, the numerator remains strictly positive:

$$
1-\mathrm{Fr}^2\to0^+,
\qquad S_0-S_f(y_c)>0.
$$

Therefore,

$$
\boxed{\frac{dy}{dx}\to+\infty},
\qquad \frac{dx}{dy}\to0^+.
$$

The S1 curve has a **vertical tangent in the depth-versus-distance diagram** at its critical-depth endpoint. This endpoint occurs at a finite longitudinal coordinate in the idealized GVF solution; it is not an asymptote at $x\to-\infty$. The standard GVF equation is singular at critical depth when its numerator is nonzero.

**3. Large-depth limit: horizontal water-surface asymptote**

As $y\to\infty$, the cross-sectional area and hydraulic radius increase, so Manning's friction slope tends to zero. The mean velocity and Froude number also tend to zero:

$$
S_f(y)\to0,\qquad
U=\frac{Q}{by}\to0,\qquad
\mathrm{Fr}^2=\frac{Q^2}{gb^2y^3}\to0.
$$

Hence

$$
\boxed{\frac{dy}{dx}\to S_0}.
$$

The water-surface elevation is $z_w=z_b+y$. Since $dz_b/dx=-S_0$,

$$
\frac{dz_w}{dx}=-S_0+\frac{dy}{dx}\to0.
$$

Thus the **water surface becomes asymptotically horizontal**, even though the depth continues to increase as the bed descends. The large-depth limit is a mathematical extrapolation of the profile.

[[s1]]

### S2 Profile — $y_0<y<y_c$

**1. Sign of the depth gradient and flow regime**

For depths above normal depth, $S_f<S_0$, whereas depths below critical depth correspond to supercritical flow:

$$
S_0-S_f(y)>0,\qquad
1-\mathrm{Fr}^2<0.
$$

Therefore,

$$
\boxed{\frac{dy}{dx}=\frac{+}{-}<0},
\qquad
\frac{dU}{dx}=-\frac{U}{y}\frac{dy}{dx}>0.
$$

S2 is an **accelerating supercritical profile**: the depth decreases and the velocity increases downstream.

**2. Upstream limit: vertical tangent at critical depth**

As $y\to y_c^-$,

$$
1-\mathrm{Fr}^2\to0^-,\qquad
S_0-S_f(y_c)>0,
$$

and consequently

$$
\boxed{\frac{dy}{dx}\to-\infty},
\qquad \frac{dx}{dy}\to0^-.
$$

The S2 profile approaches critical depth with a **vertical tangent** at a finite upstream endpoint of the idealized solution. The GVF equation cannot be continued smoothly through that singular point without additional analysis.

**3. Downstream limit: normal-depth asymptote**

As $y\to y_0^+$, the friction slope approaches the bed slope, while the denominator remains negative because $y_0<y_c$:

$$
S_0-S_f(y)\to0^+,\qquad
1-\mathrm{Fr}^2(y_0)<0.
$$

Thus

$$
\boxed{\frac{dy}{dx}\to0^-}.
$$

The depth approaches $y_0$ **asymptotically downstream** ($x\to+\infty$ in the idealized mathematical solution). Unlike the critical-depth endpoint, normal depth is approached with a vanishing depth gradient rather than a vertical tangent.

[[s2]]

### S3 Profile — $0<y<y_0<y_c$

**1. Sign of the depth gradient and flow regime**

Below normal depth, friction exceeds the bed slope; below critical depth, the flow remains supercritical:

$$
S_0-S_f(y)<0,\qquad
1-\mathrm{Fr}^2<0.
$$

It follows that

$$
\boxed{\frac{dy}{dx}=\frac{-}{-}>0},
\qquad
\frac{dU}{dx}=-\frac{U}{y}\frac{dy}{dx}<0.
$$

The S3 profile represents **decelerating supercritical flow**: depth increases and velocity decreases downstream.

**2. Downstream limit: normal-depth asymptote**

As $y\to y_0^-$, the numerator approaches zero from below, while the denominator remains strictly negative:

$$
S_0-S_f(y)\to0^-,\qquad
1-\mathrm{Fr}^2(y_0)<0.
$$

Therefore,

$$
\boxed{\frac{dy}{dx}\to0^+}.
$$

The S3 profile approaches **normal depth asymptotically downstream**. In particular, the limiting gradient is zero, not infinite: $y_0$ is an equilibrium depth of the GVF equation.

**3. Shallow-depth limit and physical restriction**

Extrapolation upstream toward $y\to0^+$ requires caution. For a rectangular channel,

$$
U=\frac{Q}{by}\to+\infty,
\qquad
\mathrm{Fr}^2=\frac{Q^2}{gb^2y^3}\to+\infty.
$$

Using Manning's resistance relation and $R\sim y$ for small depths,

$$
S_f(y)\sim\frac{n^2Q^2}{b^2y^{10/3}}
\qquad (y\to0^+).
$$

Consequently, within this idealized model,

$$
\frac{dy}{dx}
=\frac{S_0-S_f}{1-\mathrm{Fr}^2}
\sim\frac{gn^2}{y^{1/3}}>0.
$$

Although the mathematical gradient grows as $y$ approaches zero, the mean velocity becomes unbounded and the assumptions underlying gradually varied flow and Manning's resistance law are no longer physically reliable. **The zero-depth limit is not a physically realizable continuation of the S3 profile.**

[[s3]]



## H Profiles — Horizontal Bed

For a horizontal channel, the bed slope vanishes:

$$
S_0=0.
$$

The gradually varied flow equation reduces to

$$
\boxed{\frac{dy}{dx}=\frac{-S_f(y)}{1-\mathrm{Fr}^2(y)}}.
$$

For positive discharge and finite flow depth, $S_f>0$. Consequently, the numerator is strictly negative. There is **no finite normal depth**, because the uniform-flow condition $S_f(y_0)=S_0=0$ cannot be satisfied at finite $y$. The critical depth $y_c$ divides the solutions into the subcritical H2 and supercritical H3 regions. The channel bed is horizontal in both profiles.

### H2 Profile — $y>y_c$

**1. Sign of the depth gradient and flow regime**

Above critical depth, $\mathrm{Fr}<1$ and the denominator is positive. Therefore,

$$
S_0-S_f=-S_f<0,\qquad 1-\mathrm{Fr}^2>0,
$$

$$
\boxed{\frac{dy}{dx}<0}.
$$

Since the mean velocity in a rectangular channel is $U=Q/(by)$,

$$
\frac{dU}{dx}=-\frac{U}{y}\frac{dy}{dx}>0.
$$

Thus, H2 describes **accelerating subcritical flow**: the water depth decreases and the velocity increases downstream.

**2. Critical-depth limit**

As $y\to y_c^+$, the denominator tends to zero from above, whereas $S_f(y_c)>0$:

$$
1-\mathrm{Fr}^2\to0^+,\qquad -S_f(y_c)<0,
$$

$$
\boxed{\frac{dy}{dx}\to-\infty}.
$$

The H2 profile therefore reaches the critical-depth boundary with a **vertical tangent in the depth-versus-distance diagram**. This is a singular endpoint of the idealized GVF equation.

**3. Large-depth limit**

For $y\to\infty$, the hydraulic radius of a rectangular channel approaches $b/2$, the friction slope tends to zero, and $\mathrm{Fr}\to0$. Hence,

$$
\frac{dy}{dx}\to0^-.
$$

The mathematical H2 profile becomes progressively flatter at large depths, extending upstream toward arbitrarily large $y$. This does **not** represent a finite normal-depth asymptote: no finite uniform-flow depth exists for $S_0=0$.

[[h2]]

### H3 Profile — $0<y<y_c$

**1. Sign of the depth gradient and flow regime**

Below critical depth, $\mathrm{Fr}>1$ and the denominator is negative. Therefore,

$$
S_0-S_f=-S_f<0,\qquad 1-\mathrm{Fr}^2<0,
$$

$$
\boxed{\frac{dy}{dx}>0}.
$$

It follows that

$$
\frac{dU}{dx}=-\frac{U}{y}\frac{dy}{dx}<0.
$$

Thus, H3 describes **decelerating supercritical flow**: the depth increases and the velocity decreases downstream.

**2. Critical-depth limit**

As $y\to y_c^-$, the denominator tends to zero from below and the numerator remains strictly negative:

$$
1-\mathrm{Fr}^2\to0^-,\qquad -S_f(y_c)<0,
$$

$$
\boxed{\frac{dy}{dx}\to+\infty}.
$$

The H3 profile reaches the critical-depth boundary with a **vertical tangent in the depth-versus-distance diagram**.

**3. Shallow-depth limit and physical restriction**

As $y\to0^+$,

$$
U=\frac{Q}{by}\to+\infty,\qquad
\mathrm{Fr}^2=\frac{Q^2}{gb^2y^3}\to+\infty.
$$

For a rectangular channel, $R\sim y$ as $y\to0^+$. Using Manning's equation,

$$
S_f(y)\sim\frac{n^2Q^2}{b^2y^{10/3}},
$$

and consequently

$$
\frac{dy}{dx}=\frac{-S_f}{1-\mathrm{Fr}^2}
\sim\frac{gn^2}{y^{1/3}}\to+\infty.
$$

Although the mathematical model admits a formal shallow-depth limit, the corresponding unbounded velocity and gradient violate the physical assumptions underlying the gradually varied flow approximation. **The zero-depth limit is not a physically realizable continuation of the H3 profile.**

[[h3]]
