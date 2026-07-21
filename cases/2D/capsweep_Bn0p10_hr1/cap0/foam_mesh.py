#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paylasilan yardimci: bir case'in system/blockMeshDict'inden mesh boyutlarini okur.
Pseudo-2D yapisal blok varsayar: blocks ( hex (...) (1 NY NZ) ...), vertices'ten LY,LZ.
Donus: dict(NY, NZ, LY, LZ, DY, DZ)."""
import os, re

def read_mesh(case_dir):
    bm = os.path.join(case_dir, 'system', 'blockMeshDict')
    with open(bm) as f:
        txt = f.read()
    # blocks ( hex (0 1 2 3 4 5 6 7) (1 NY NZ) ...
    m = re.search(r'hex\s*\([^)]*\)\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)', txt)
    if not m:
        raise RuntimeError(f'{bm}: blocks hex (1 NY NZ) okunamadi')
    nx, NY, NZ = int(m.group(1)), int(m.group(2)), int(m.group(3))
    # vertices ( (x y z) (x y z) ... ) -> LY = max y, LZ = max z
    vm = re.search(r'vertices\s*\((.*?)\)\s*;', txt, re.S)
    pts = re.findall(r'\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)', vm.group(1))
    ys = [float(p[1]) for p in pts]; zs = [float(p[2]) for p in pts]
    LY, LZ = max(ys), max(zs)
    return dict(NY=NY, NZ=NZ, LY=LY, LZ=LZ, DY=LY/NY, DZ=LZ/NZ)
