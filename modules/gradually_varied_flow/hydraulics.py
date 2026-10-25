"""Shared constants and rectangular-channel hydraulic functions."""
G = 9.81

def area(width, depth):
    return width * depth

def hydraulic_radius(width, depth):
    return area(width, depth) / (width + 2 * depth)

def critical_depth(discharge, width):
    return (discharge**2 / (G * width**2))**(1 / 3)

def friction_slope(discharge, width, roughness, depth):
    a = area(width, depth)
    r = hydraulic_radius(width, depth)
    return (roughness * discharge / (a * r**(2/3)))**2

def froude_squared(discharge, width, depth):
    return discharge**2 / (G * width**2 * depth**3)

def normal_depth(discharge, width, roughness, slope):
    if slope <= 0:
        raise ValueError("Normal depth requires positive bed slope.")
    lo, hi = 1e-8, 1.0
    while friction_slope(discharge, width, roughness, hi) > slope:
        hi *= 2
    for _ in range(90):
        mid = (lo + hi) / 2
        if friction_slope(discharge, width, roughness, mid) > slope:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
