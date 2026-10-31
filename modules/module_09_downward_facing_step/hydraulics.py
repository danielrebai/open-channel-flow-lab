"""Rectangular-channel GVF, Manning friction and hydraulic-jump calculations."""
import numpy as np
from scipy.optimize import brentq
G=9.81

def energy(h,q): return h+q*q/(2*G*h*h)
def force(h,q): return h*h/2+q*q/(G*h)
def critical(q): return (q*q/G)**(1/3)
def sf(h,q,b,n):
    area=b*h; radius=area/(b+2*h)
    return (n*q*b/(area*radius**(2/3)))**2
def normal(q,b,n,s):
    return brentq(lambda h:sf(h,q,b,n)-s,0.001,100)
def depth_at_energy(e,q,branch):
    k=critical(q)
    if e<1.5*k-1e-9: raise ValueError('Energy below critical minimum')
    if abs(e-1.5*k)<1e-9:return k
    if branch=='super':return brentq(lambda h:energy(h,q)-e,k*1e-4,k*(1-1e-9))
    return brentq(lambda h:energy(h,q)-e,k*(1+1e-9),max(100,2*e))
def conjugate(h,q):
    return h/2*(np.sqrt(1+8*q*q/(G*h**3))-1)
def integrate(x0,h0,x1,s,q,b,n,k,points=250):
    """Module 04/07 adaptive explicit Euler GVF integration.

    Signed spatial steps, relative-depth limiter and critical-depth guard.
    The normal-depth equilibrium is preserved exactly.
    """
    direction = 1.0 if x1 > x0 else -1.0
    x, h = float(x0), float(h0)
    xs, hs = [x], [h]
    critical_tol = max(0.003, 0.005*k)
    # An exact critical boundary is singular: start infinitesimally on the
    # prescribed subcritical/supercritical branch (the plotted control remains hc).
    if abs(h-k) < 1e-10:
        h = k*(1.0001 if h >= k else 0.9999)
        hs[0] = h
    for _ in range(30000):
        remaining = abs(x1-x)
        if remaining < 1e-9:
            break
        den = 1.0-(k/h)**3
        if h <= 0 or abs(den) < 1e-10:
            break
        f = (s-sf(h,q,b,n))/den
        dx = min(remaining, (1.0 if h>k else 0.5)*h)
        if abs(f)>1e-12:
            dx = min(dx, 0.025*max(h,0.05)/abs(f))
            if abs(h-k)>critical_tol:
                dx = min(dx,0.25*abs(h-k)/abs(f))
        if dx<1e-8:
            break
        for _attempt in range(35):
            hnew=h+direction*f*dx
            if (np.isfinite(hnew) and hnew>0 and
                (hnew-k)*(h-k)>0 and
                abs(hnew-h)<=0.05*max(h,0.05)):
                break
            dx*=0.5
        else:
            break
        x+=direction*dx
        h=hnew
        xs.append(x);hs.append(h)
    else:
        raise RuntimeError('Euler GVF step limit reached')
    return np.asarray(xs),np.asarray(hs)
