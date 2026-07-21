#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENEL transient run-out cikarici (cell-center). Mesh boyutu blockMeshDict'ten OTOMATIK okunur.
  r(t) = en uzak alpha.mayo>0.5 hucresinin y-merkezi  (canonical run-out, cell-center -> staircase)
  h(t) = en uzak alpha.mayo>0.5 hucresinin z-merkezi
  h_over_h0 = h/H0   (R0=H0=1.0)
Hucre siralamasi (pseudo-2D 1xNYxNZ blok): index i = iy + iz*NY.
Cikti: <case>/h_transient.csv (t,h_over_h0)
Kullanim: python3 compute_r_h.py <case_dir>   (varsayilan: cwd)
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from foam_mesh import read_mesh

R0 = H0 = 1.0
ALPHA_THR = 0.5

def read_alpha(path, ncell):
    with open(path) as f:
        txt = f.read()
    m = re.search(r'internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(\s*', txt)
    if m:
        n = int(m.group(1)); start = m.end(); end = txt.find(')', start)
        vals = [float(x) for x in txt[start:end].split()]
        return vals
    m = re.search(r'internalField\s+uniform\s+([-\d.eE+]+)\s*;', txt)
    if m:
        return [float(m.group(1))] * ncell
    raise RuntimeError(f'{path}: internalField okunamadi')

def main():
    case = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    case = os.path.abspath(case)
    M = read_mesh(case); NY, NZ, DY, DZ = M['NY'], M['NZ'], M['DY'], M['DZ']
    ncell = NY * NZ
    times = []
    for nm in os.listdir(case):
        full = os.path.join(case, nm)
        if not os.path.isdir(full): continue
        try: t = float(nm)
        except ValueError: continue
        if os.path.exists(os.path.join(full, 'alpha.mayo')):
            times.append((t, full))
    times.sort()
    rows = []
    for t, d in times:
        a = read_alpha(os.path.join(d, 'alpha.mayo'), ncell)
        iy_max = iz_max = -1
        for i, v in enumerate(a):
            if v > ALPHA_THR:
                iy = i % NY; iz = i // NY
                if iy > iy_max: iy_max = iy
                if iz > iz_max: iz_max = iz
        r = (iy_max + 0.5) * DY if iy_max >= 0 else 0.0
        h = (iz_max + 0.5) * DZ if iz_max >= 0 else 0.0
        rows.append((t, h / H0))
    out = os.path.join(case, 'h_transient.csv')
    with open(out, 'w') as f:
        f.write('t,h_over_h0\n')
        for t, h in rows:
            f.write('%.4f,%.4f\n' % (t, h))
    print('wrote %s (%d satir, mesh %dx%d)' % (out, len(rows), NY, NZ))

if __name__ == '__main__':
    main()
