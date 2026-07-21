#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bizim Bn case'imizi Valette referansiyla karsilastir.
- r_inf: Valette fullsweep (0.01,0.03,0.1 DIREKT); diger Bn icin log-log interp/extrap (FLAG).
- transient: yalniz Bn=0.01/0.03/0.1 icin direkt ref (timeseries); o t_bar'larda bizim r_iso ile kiyas.
Kullanim: python3 compare_valette.py <case_dir> <Bn> <tc>
"""
import csv, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VR = '/scratch/ismailhos/cosamInterIsoAlgFoam_updated/paperEditIH/valetteRefDigitized'
SWEEP = [(0.01, 3.8389), (0.03, 2.8331), (0.1, 1.7817)]   # Valette fullsweep (direkt)
TS = {0.01: 'fig_case4timeseries_Bn001_ref.csv', 0.03: 'fig_case4timeseries_Bn003_ref.csv', 0.1: 'fig_case4timeseries_Bn01_ref.csv'}

def valette_rinf(Bn):
    for b, r in SWEEP:
        if abs(b - Bn) < 1e-9:
            return r, 'DIREKT'
    xs = [math.log10(b) for b, _ in SWEEP]; ys = [math.log10(r) for _, r in SWEEP]
    lb = math.log10(Bn)
    # bracketing iki nokta (yoksa en yakin ikiyle extrap)
    if lb < xs[0]:
        i, j = 0, 1; kind = 'EXTRAP(<0.01)'
    elif lb > xs[-1]:
        i, j = 1, 2; kind = 'EXTRAP(>0.1)'
    else:
        i = max(k for k in range(len(xs)) if xs[k] <= lb); j = i + 1; kind = 'INTERP'
    slope = (ys[j] - ys[i]) / (xs[j] - xs[i])
    return 10 ** (ys[i] + slope * (lb - xs[i])), kind

def our_arrest(case):
    rows = [r for r in csv.reader(open(os.path.join(case, 'iso_arrest.csv')))][1:]
    tb = [float(r[1]) for r in rows]; ri = [float(r[2]) for r in rows]; yc = [int(r[3]) for r in rows]
    arr = None; seen = False
    for k in range(len(yc)):
        if yc[k] > 0: seen = True
        elif seen and arr is None and tb[k] > 0 and all(yc[j] == 0 for j in range(k, min(k+3, len(yc)))):
            arr = (ri[k], tb[k])
    return (arr[0] if arr else ri[-1]), ri[-1], tb, ri, (arr is not None)

def main():
    case, Bn, tc = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    r_arr, r_raw, tb, ri, arrested = our_arrest(case)
    v_rinf, kind = valette_rinf(Bn)
    print('############ VALETTE KIYAS: Bn=%g ############' % Bn)
    print('r_inf:')
    print('  bizim (iso yield-arrest) = %.3f %s' % (r_arr, '' if arrested else '(arrest YOK -> raw son)'))
    print('  bizim (iso raw @ son)    = %.3f' % r_raw)
    print('  Valette r_inf            = %.3f  [%s]' % (v_rinf, kind))
    print('  sapma (arrest vs Valette)= %+.1f%%' % (100*(r_arr - v_rinf)/v_rinf))
    print('  sapma (raw vs Valette)   = %+.1f%%' % (100*(r_raw - v_rinf)/v_rinf))
    # transient (yalniz direkt ref olan Bn)
    key = next((k for k in TS if abs(k - Bn) < 1e-9), None)
    if key is not None:
        vr = [(float(a), float(b)) for a, b in csv.reader(open(os.path.join(VR, TS[key]))) if a.strip()]
        tbv = [p[0] for p in vr]; rv = [p[1] for p in vr]
        def our_at(x):
            k = min(range(len(tb)), key=lambda i: abs(tb[i] - x)); return ri[k]
        def val_at(x):
            for i in range(1, len(tbv)):
                if tbv[i] >= x:
                    return rv[i-1] + (rv[i]-rv[i-1])*(x-tbv[i-1])/(tbv[i]-tbv[i-1])
            return rv[-1]
        print('\ntransient (DIREKT ref):  t_bar | bizim r_iso | Valette | fark')
        for x in [50, 100, 200, 300, 500, 700, 1000]:
            if x <= max(tb) and x <= max(tbv):
                print('  %5d | %10.3f | %7.3f | %+.3f' % (x, our_at(x), val_at(x), our_at(x)-val_at(x)))
    else:
        print('\ntransient: Bn=%g icin DIREKT Valette ref YOK (sadece r_inf interp).' % Bn)

if __name__ == '__main__':
    main()
