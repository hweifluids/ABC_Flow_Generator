#!/usr/bin/env python3
"""
Generate an unsteady ABC flow (with explicit A, B, C coefficients)
and write:
  • 100 VTK RectilinearGrid files: abc_0000.vtr … abc_0099.vtr
  • an index file: abc_series.pvd carrying real time stamps

Domain    : [0, 2π]^3, uniform N*N*N grid
Flow field:
    u = ( A·sin(z+φ) + C·cos y ,
          B·sin x     + A·cos(z+φ) ,
          C·sin y     + B·cos x )       with φ(t) = t
Default A=B=C=1, but you can change them below.
"""

import os
import numpy as np
from pyevtk.hl import gridToVTK

# --------------------------------------------------
# User parameters
# --------------------------------------------------
N        = 48               # grid points per axis
A, B, C  = 1.0, 1.0, 1.0    # ABC coefficients
t_start  = 0.0
t_end    = 10.0
n_step   = 200
phi      = lambda t: t      # time-dependent phase
outdir   = "output"
basename = "abc"
# --------------------------------------------------

# Coordinate arrays --------------------------------------------------------
L = 2.0 * np.pi
coords = np.linspace(0.0, L, N, dtype=np.float32)
x3d, y3d, z3d = np.meshgrid(coords, coords, coords, indexing="ij")
x_coords = coords.astype(np.float32)
y_coords = coords.astype(np.float32)
z_coords = coords.astype(np.float32)

# Prepare output folder ----------------------------------------------------
os.makedirs(outdir, exist_ok=True)

# Time loop ----------------------------------------------------------------
dt = (t_end - t_start) / n_step
vtr_names = []
times     = []

for k in range(n_step):
    t  = t_start + k * dt
    ph = phi(t)

    # ---------- ABC velocity field ----------
    vx = A * np.sin(z3d + ph) + C * np.cos(y3d)
    vy = B * np.sin(x3d)      + A * np.cos(z3d + ph)
    vz = C * np.sin(y3d)      + B * np.cos(x3d)

    fname = f"{basename}_{k:04d}"
    gridToVTK(os.path.join(outdir, fname),
              x_coords, y_coords, z_coords,
              pointData={"velocity": (vx, vy, vz)})

    vtr_names.append(f"{fname}.vtr")
    times.append(t)

# Write PVD index file -----------------------------------------------------
pvd_path = os.path.join(outdir, "abc_series.pvd")
with open(pvd_path, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0"?>\n')
    f.write('<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">\n')
    f.write('  <Collection>\n')
    for name, t in zip(vtr_names, times):
        f.write(f'    <DataSet timestep="{t:.6f}" group="" part="0" file="{name}"/>\n')
    f.write('  </Collection>\n')
    f.write('</VTKFile>\n')

print(f"Finished.")
