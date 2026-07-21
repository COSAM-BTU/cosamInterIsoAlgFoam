#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENEL iso-contour run-out + YIELD-ARREST cikarici. Mesh blockMeshDict'ten OTOMATIK.
  (1) iso-contour r(t): en uzak alpha=0.5 gecisi (alt-hucre lineer interp), tum z satirlarinda max -> Liu/Valette metrigi
  (2) yield-arrest: akan mayo hucre (alpha>0.5 & gammaDot>gammaMin) ilk stabil sifir
      gammaDot = sqrt(2 S:S), S=symm(grad U); grad U yapisal mesh'te numpy FD (postProcess YOK).
Cikti: <case>/iso_arrest.csv (t,t_bar,r_iso,yield_count) + ozet stdout (arrest + r_iso(arrest)).
Kullanim: python3 compute_iso_arrest.py <case_dir> [tc]   (tc varsayilan 1/0.9; Bn'e gore degisir!)
"""
import os, re, sys, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from foam_mesh import read_mesh

GMIN = 1e-3
ALPHA_THR = 0.5

def read_field(path, ncomp, ncell):
    with open(path) as f:
        txt = f.read()
    i = txt.find('internalField'); seg = txt[i:]
    if 'nonuniform' not in seg:
        a = seg.find('uniform') + 7; b = seg.find(';', a)
        vals = seg[a:b].strip().lstrip('(').rstrip(')').split()
        if ncomp == 1: return np.full(ncell, float(vals[0]))
        return np.tile([float(x) for x in vals], (ncell, 1))
    p = seg.find('<'); lp = seg.find('\n', p); rest = seg[lp:]
    op = rest.find('('); cnt = int(rest[:op].strip().split()[-1]); cp = rest.find('\n)', op)
    body = rest[op+1:cp]
    if ncomp == 1:
        return np.fromstring(body.replace('\n', ' '), sep=' ')[:cnt]
    body = body.replace('(', ' ').replace(')', ' ')
    return np.fromstring(body, sep=' ')[:cnt*ncomp].reshape(cnt, ncomp)

def iso_runout(alpha, NY, NZ, DY, R0=1.0):
    a = alpha.reshape(NZ, NY); yc = (np.arange(NY) + 0.5) * DY; rmax = 0.0
    for iz in range(NZ):
        row = a[iz]; ge = np.where(row >= 0.5)[0]
        if ge.size == 0: continue
        iy = ge.max()
        if iy >= NY - 1: r = yc[iy]
        else:
            a0, a1 = row[iy], row[iy+1]
            r = yc[iy] if a0 == a1 else yc[iy] + (0.5 - a0) / (a1 - a0) * DY
        rmax = max(rmax, r)
    return rmax / R0

def gammadot(U, NY, NZ, DY, DZ):
    Ux = U[:,0].reshape(NZ, NY); Uy = U[:,1].reshape(NZ, NY); Uz = U[:,2].reshape(NZ, NY)
    dUx_dy = np.gradient(Ux, DY, axis=1); dUx_dz = np.gradient(Ux, DZ, axis=0)
    dUy_dy = np.gradient(Uy, DY, axis=1); dUy_dz = np.gradient(Uy, DZ, axis=0)
    dUz_dy = np.gradient(Uz, DY, axis=1); dUz_dz = np.gradient(Uz, DZ, axis=0)
    Sxy = 0.5*dUx_dy; Sxz = 0.5*dUx_dz; Syz = 0.5*(dUy_dz + dUz_dy)
    g2 = dUy_dy**2 + dUz_dz**2 + 2*(Sxy**2 + Sxz**2 + Syz**2)
    return np.sqrt(2*g2).ravel()

def main():
    case = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    TC = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0/0.9
    M = read_mesh(case); NY, NZ, DY, DZ = M['NY'], M['NZ'], M['DY'], M['DZ']; ncell = NY*NZ
    times = sorted(float(d) for d in os.listdir(case)
                   if os.path.isdir(os.path.join(case, d)) and re.fullmatch(r'[\d.eE+-]+', d)
                   and os.path.exists(os.path.join(case, d, 'U'))
                   and os.path.exists(os.path.join(case, d, 'alpha.mayo')))
    rows = []
    for t in times:
        d = os.path.join(case, ('%d' % int(t)) if t == int(t) else repr(t))
        if not os.path.isdir(d):
            for nm in os.listdir(case):
                if os.path.isdir(os.path.join(case, nm)) and re.fullmatch(r'[\d.eE+-]+', nm) and float(nm) == t:
                    d = os.path.join(case, nm); break
        try:
            alpha = read_field(os.path.join(d, 'alpha.mayo'), 1, ncell)
            U = read_field(os.path.join(d, 'U'), 3, ncell)
        except Exception as e:
            print('  [skip t=%g] %s' % (t, e)); continue
        r_iso = iso_runout(alpha, NY, NZ, DY)
        g = gammadot(U, NY, NZ, DY, DZ)
        yc = int(np.count_nonzero((alpha > ALPHA_THR) & (g > GMIN)))
        rows.append((t, t/TC, r_iso, yc))
    rows.sort()
    with open(os.path.join(case, 'iso_arrest.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['t', 't_bar', 'r_iso', 'yield_count']); w.writerows(rows)
    arr = None; seen = False
    for k, (t, tb, ri, yc) in enumerate(rows):
        if yc > 0: seen = True
        elif seen and arr is None and t > 0 and all(rows[j][3] == 0 for j in range(k, min(k+3, len(rows)))):
            arr = (t, tb, ri)
    base = os.path.basename(case)
    if arr:
        print('%s: ARREST t_bar=%.0f (t=%.0f) r_iso=%.4f | raw_son r_iso=%.4f | mesh %dx%d | tc=%.4f'
              % (base, arr[1], arr[0], arr[2], rows[-1][2], NY, NZ, TC))
    else:
        print('%s: ARREST YOK | son yield=%d | raw_son r_iso=%.4f | mesh %dx%d'
              % (base, rows[-1][3], rows[-1][2], NY, NZ))

if __name__ == '__main__':
    main()
