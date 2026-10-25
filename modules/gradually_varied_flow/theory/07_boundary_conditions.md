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
