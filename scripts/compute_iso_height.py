#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISO-interpolasyonlu kolon yuksekligi h_iso: her y-kolonunda en ustteki
alpha=0.5 gecisinin z-yonunde alt-hucre lineer interpolasyonu, kolonlar
uzerinde max (r_iso metriginin z-yonlu ikizi). Eksen kolonu (iy=0) degeri
ayrica raporlanir.
Kullanim: python3 compute_iso_height.py <case_dir> <time>
"""
import os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute_iso_arrest import read_field
from foam_mesh import read_mesh


def iso_height(alpha, NY, NZ, DZ, H0=1.0):
    a = alpha.reshape(NZ, NY)
    zc = (np.arange(NZ) + 0.5) * DZ
    hmax = 0.0; h_axis = None
    for iy in range(NY):
        col = a[:, iy]; ge = np.where(col >= 0.5)[0]
        if ge.size == 0:
            if iy == 0: h_axis = 0.0
            continue
        iz = ge.max()
        if iz >= NZ - 1:
            h = zc[iz]
        else:
            a0, a1 = col[iz], col[iz + 1]
            h = zc[iz] if a0 == a1 else zc[iz] + (0.5 - a0) / (a1 - a0) * DZ
        if iy == 0:
            h_axis = h
        hmax = max(hmax, h)
    return hmax / H0, (h_axis / H0 if h_axis is not None else None)


def main():
    case = os.path.abspath(sys.argv[1]); t = sys.argv[2]
    M = read_mesh(case)
    NY, NZ, DZ = M['NY'], M['NZ'], M['DZ']
    d = os.path.join(case, t)
    alpha = read_field(os.path.join(d, 'alpha.mayo'), 1, NY * NZ)
    hmax, h_axis = iso_height(alpha, NY, NZ, DZ)
    print('%s t=%s: h_iso_max=%.4f  h_iso_axis=%.4f' % (os.path.basename(case), t, hmax, h_axis))


if __name__ == '__main__':
    main()
