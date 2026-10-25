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
