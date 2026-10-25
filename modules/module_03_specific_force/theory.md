## 1. Definition of specific force

For steady open-channel flow, **specific force** (the momentum function) is the sum of the hydrostatic pressure contribution and the momentum-flux contribution, divided by the specific weight $\gamma=\rho g$:

$$
\Sigma=\frac{\Pi_p+M}{\gamma}.
$$

The hydrostatic resultant and the momentum flux are

$$
\Pi_p=\overline p\,A(h)=\gamma y_G(h)A(h),
\qquad M=\beta\rho\frac{Q^2}{A(h)}.
$$

Here $A(h)$ is the wetted area, $y_G(h)$ is the depth of its centroid **below the free surface**, and $\beta$ is the momentum correction coefficient. Consequently,

$$
\boxed{\Sigma(h,Q)=\underbrace{y_G(h)A(h)}_{\text{hydrostatic}}+
\underbrace{\frac{\beta Q^2}{gA(h)}}_{\text{dynamic}}},
\qquad f(\Sigma,Q,h)=0.
$$

The units of $\Sigma$ are $\mathrm{m^3}$. Throughout the interactive rectangular-channel examples we take $\beta=1$, as appropriate for an idealized uniform velocity profile.

## 2. Specific force as a function of depth at constant discharge

For a given $Q>0$, consider $\Sigma(h,Q)$. As $h\to0^+$, $A(h)\to0$ and the dynamic contribution diverges:

$$
\lim_{h\to0^+}\Sigma(h,Q)=0+\infty=+\infty.
$$

For large depths, the hydrostatic contribution grows without bound, hence

$$
\lim_{h\to\infty}\Sigma(h,Q)=+\infty.
$$

Unlike specific energy, the rectangular-channel specific-force curve has **no straight-line oblique asymptote** at large depth. For a rectangular channel of constant width $B$,

$$
A(h)=Bh,\quad y_G(h)=\frac h2,
\quad\boxed{\Sigma(h,Q)=\frac{Bh^2}{2}+\frac{\beta Q^2}{gBh}}.
$$

Therefore,

$$
\frac{\Sigma}{h}=\frac{Bh}{2}+\frac{\beta Q^2}{gBh^2}
\xrightarrow[h\to\infty]{}+\infty.
$$

The hydrostatic term is quadratic in $h$; thus a straight-line asymptote is not appropriate. The curve has a minimum at the critical depth $h_c$.

<!-- GRAPH:SIGMA_H -->

## 3. Hydrostatic contribution for an arbitrary cross-section

To differentiate the pressure term, subdivide the wetted area into horizontal strips. A strip at depth $y$ below the free surface, of width $dB$, has area $dA=y\,dB$ in the geometric construction of the notes; its centroid is at $y/2$ below the free surface. Hence

$$
y_G=\frac{\int_A y\,dA}{A},\qquad
 y_G A=\int_A y\,dA
=\int_0^{B(h)}\frac{y^2}{2}\,dB.
$$

When the free surface rises by $dh$, each previously wetted area element becomes $dh$ deeper. Accordingly,

$$
\boxed{\frac{d}{dh}\big[y_G(h)A(h)\big]=A(h)}.
$$

This identity holds for an arbitrary fixed cross-section under hydrostatic pressure conditions.

## 4. Minimum specific force and critical depth

At constant $Q$ and constant $\beta$,

$$
\frac{d\Sigma}{dh}=
\frac{d}{dh}\big[y_G(h)A(h)\big]
+\frac{d}{dh}\left[\frac{\beta Q^2}{gA(h)}\right].
$$

Using $dA/dh=B(h)$ and the hydrostatic identity,

$$
\frac{d\Sigma}{dh}=A(h)
-\frac{\beta Q^2}{gA^2(h)}\frac{dA}{dh}
=A(h)-\frac{\beta Q^2B(h)}{gA^2(h)}.
$$

Setting this derivative equal to zero at $h=h_c$ gives

$$
A(h_c)-\frac{\beta Q^2B(h_c)}{gA^2(h_c)}=0,
\qquad\boxed{\frac{A^3(h_c)}{B(h_c)}=\frac{\beta Q^2}{g}}.
$$

This is the same critical-depth condition obtained by minimizing specific energy **when $\alpha=\beta$**. In the idealized model, $\alpha\simeq1$ and $\beta\simeq1$, so both conditions coincide. In real nonuniform flows the coefficients need not be identical; this distinction matters.

For a rectangular section, $A=Bh$, $q=Q/B$, and $\beta=1$:

$$
\frac{(Bh_c)^3}{B}=\frac{Q^2}{g}
\quad\Longrightarrow\quad
\boxed{h_c=\left(\frac{q^2}{g}\right)^{1/3}}.
$$

## 5. Critical specific force

Substituting the critical condition into the specific-force expression,

$$
\Sigma_c=\Sigma(h_c,Q)
=y_G(h_c)A(h_c)+\frac{\beta Q^2}{gA(h_c)}.
$$

Since $\beta Q^2/g=A^3(h_c)/B(h_c)$,

$$
\Sigma_c=y_G(h_c)A(h_c)
+\frac{A^3(h_c)}{B(h_c)}\frac1{A(h_c)}
=A(h_c)\left[y_G(h_c)+\frac{A(h_c)}{B(h_c)}\right].
$$

Defining the critical hydraulic depth $D_c=A(h_c)/B(h_c)$,

$$
\boxed{\Sigma_c=A(h_c)\,[y_G(h_c)+D_c]}.
$$

For a rectangular channel, $y_G(h_c)=h_c/2$, $D_c=h_c$, and $A(h_c)=Bh_c$:

$$
\boxed{\Sigma_c=Bh_c\left(\frac{h_c}{2}+h_c\right)
=\frac32 Bh_c^2}.
$$

At a fixed discharge, depths $h<h_c$ lie on the **supercritical** branch and depths $h>h_c$ on the **subcritical** branch. Two different depths with the same specific force are called **conjugate (sequent) depths**, and are central to hydraulic-jump analysis.

## 6. Discharge as a function of depth at constant specific force

For a prescribed $\overline\Sigma$, rearrange the defining equation:

$$
\overline\Sigma=y_G(h)A(h)+\frac{\beta Q^2}{gA(h)},
$$

$$
\boxed{Q^2=\left[\overline\Sigma-y_G(h)A(h)\right]
\frac{gA(h)}{\beta}},
\qquad
\boxed{Q=\sqrt{\left[\overline\Sigma-y_G(h)A(h)\right]
\frac{gA(h)}{\beta}}}.
$$

The physically admissible interval is where $\overline\Sigma-y_GA\ge0$. At $h=0$, $A=0$ and $Q=0$. The other zero occurs at a finite static depth $h_*$ satisfying

$$
\boxed{\overline\Sigma=y_G(h_*)A(h_*)}.
$$

For a rectangular section, $h_*=\sqrt{2\overline\Sigma/B}$. Between these two zero-discharge states, $Q$ reaches a maximum.

<!-- GRAPH:H_Q -->

## 7. Maximum discharge at fixed specific force

Instead of differentiating the square root, maximize $Q^2$ (equivalent for $Q>0$):

$$
\frac{dQ^2}{dh}=\frac g\beta\left\{
-\frac{d}{dh}[y_G(h)A(h)]\,A(h)
+[\overline\Sigma-y_G(h)A(h)]\frac{dA}{dh}
\right\}=0.
$$

Using $d(y_GA)/dh=A$ and $dA/dh=B$,

$$
-A^2(h)+B(h)[\overline\Sigma-y_G(h)A(h)]=0.
$$

From the definition of specific force,

$$
\overline\Sigma-y_G(h)A(h)=\frac{\beta Q^2}{gA(h)}.
$$

Thus

$$
-A^2(h)+\frac{\beta Q^2B(h)}{gA(h)}=0,
\qquad
\boxed{\frac{A^3(h)}{B(h)}=\frac{\beta Q^2}{g}}.
$$

This is exactly the condition obtained when minimizing $\Sigma$ at fixed $Q$. Therefore, for the same cross-section and momentum coefficient,

$$
\boxed{\begin{aligned}
\text{Fixed }Q &: \quad \Sigma\text{ is minimum at }h=h_c,\\
\text{Fixed }\Sigma &: \quad Q\text{ is maximum at }h=h_c.
\end{aligned}}
$$

The minima of the $\Sigma(h)$ curves and the maxima of the $h(Q)$ curves belong to the same **critical locus**. This completes the sequence of derivations in the handwritten notes.

## 8. Connection with the exercises

For the rectangular, idealized model used in the Toy and Exercises ($\beta=1$), it is useful to work with the specific force **per unit width**:

$$
\boxed{m=\frac\Sigma B=\frac{h^2}{2}+\frac{q^2}{gh}},
\qquad q=\frac QB.
$$

Then $m_c=3h_c^2/2$, and two depths $h_1,h_2$ having equal $m$ at the same $q$ satisfy

$$
\frac{h_1^2}{2}+\frac{q^2}{gh_1}
=\frac{h_2^2}{2}+\frac{q^2}{gh_2}.
$$

For a hydraulic jump, the conjugate-depth formula can also be written using the upstream Froude number $Fr_1=q/(h_1\sqrt{gh_1})$:

$$
\boxed{\frac{h_2}{h_1}=\frac12\left(\sqrt{1+8Fr_1^2}-1\right)}.
$$

This final formula is an **additional application** beyond the six pages of notes, included to connect the theory to practical exercises.
