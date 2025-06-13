#!/usr/bin/env python3

import os
import numpy as np
from pyevtk.hl import gridToVTK

# --------------------------------------------------
# Function definition
# --------------------------------------------------
def generate_abc_flow(N, A, B, C,
                      epsilons, omegas, betas,
                      a_list,
                      t_start, t_end, n_step,
                      outdir, basename,
                      progress_callback=None):
    """
    Generate a time-dependent ABC flow VTK series with multi-component phase.

    Parameters:
        N (int): grid points per axis
        A, B, C (float): ABC flow coefficients
        epsilons (sequence of float): amplitudes of sinusoidal phase terms
        omegas   (sequence of float): angular frequencies of sinusoidal phase terms
        betas    (sequence of float): phase offsets of sinusoidal phase terms
        a_list   (sequence of float): linear phase growth rates
        t_start (float): start time
        t_end   (float): end time
        n_step  (int): number of time steps
        outdir   (str): output directory
        basename (str): base name for VTK files
    """
    # Phase function phi(t) = sum_i epsilons[i]*sin(omegas[i]*t + betas[i]) + sum_j a_list[j]*t
    def phi(t):
        sinusoidal = sum(eps * np.sin(omega * t + beta)
                         for eps, omega, beta in zip(epsilons, omegas, betas))
        linear = sum(a * t for a in a_list)
        return sinusoidal + linear

    # Create grid
    L = 2.0 * np.pi
    coords = np.linspace(0.0, L, N, dtype=np.float32)
    x3d, y3d, z3d = np.meshgrid(coords, coords, coords, indexing="ij")
    x_coords = coords.astype(np.float32)
    y_coords = coords.astype(np.float32)
    z_coords = coords.astype(np.float32)

    # Prepare output folder
    os.makedirs(outdir, exist_ok=True)

    dt = (t_end - t_start) / n_step
    vtr_names = []
    times = []

    for k in range(n_step):

        if progress_callback:
            progress_callback(k+1, n_step)

        t = t_start + k * dt
        ph = phi(t)

        # Velocity components with time-dependent phase
        vx = A * (np.sin(z3d + ph) + np.cos(y3d + ph))
        vy = B * (np.sin(x3d + ph) + np.cos(z3d + ph))
        vz = C * (np.sin(y3d + ph) + np.cos(x3d + ph))

        fname = f"{basename}_{k:04d}"
        gridToVTK(
            os.path.join(outdir, fname),
            x_coords, y_coords, z_coords,
            pointData={"velocity": (vx, vy, vz)}
        )

        vtr_names.append(f"{fname}.vtr")
        times.append(t)

    # Write PVD index file
    pvd_path = os.path.join(outdir, f"{basename}_series.pvd")
    with open(pvd_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">\n')
        f.write('  <Collection>\n')
        for name, t in zip(vtr_names, times):
            f.write(f'    <DataSet timestep="{t:.6f}" group="" part="0" file="{name}"/>\n')
        f.write('  </Collection>\n')
        f.write('</VTKFile>\n')

    print(f"Generated {len(vtr_names)} time steps in '{outdir}'")


# --------------------------------------------------
# Main: default parameters for standalone test
# --------------------------------------------------
if __name__ == "__main__":
    # Default parameters
    N = 48
    A, B, C = 1.0, 1.0, 1.0

    # Multi-component sinusoidal phase terms
    epsilons = [0.5, 0.2]       # example amplitudes
    omegas   = [2.0, 1.0]       # example angular frequencies
    betas    = [0.0, np.pi/4]   # example phase offsets

    # Multi-component linear phase growth rates
    a_list = [1.0, 0.3]         # example linear rates

    t_start = 0.0
    t_end   = 10.0
    n_step  = 200
    outdir  = "output"
    basename = "abc"

    generate_abc_flow(
        N, A, B, C,
        epsilons, omegas, betas,
        a_list,
        t_start, t_end, n_step,
        outdir, basename
    )
