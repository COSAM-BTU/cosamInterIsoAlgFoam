#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENEL mesh convergence (GCI / Richardson) -- BIRINCIL METRIK: iso-contour YIELD-ARREST-KESIM r_inf.
Her case dirinden iso_arrest.csv okur (arrest = akan hucre ilk stabil sifir; r_iso(arrest)).
dx (refinement) her case'in blockMeshDict'inden (DY) okunur -> oran otomatik.
Kullanim: python3 compute_convergence.py <kaba_dir> <orta_dir> <ince_dir>   (kaba->ince sirayla)
"""
import csv, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from foam_mesh import read_mesh

FS = 1.25  # GCI guvenlik faktoru (3+ seviye)

def arrest_iso(path):
    rows = [r for r in csv.reader(open(path))][1:]
    tb = [float(r[1]) for r in rows]; ri = [float(r[2]) for r in rows]; yc = [int(r[3]) for r in rows]
    arr = None; seen = False
    for k in range(len(yc)):
        if yc[k] > 0: seen = True
        elif seen and arr is None and tb[k] > 0 and all(yc[j] == 0 for j in range(k, min(k+3, len(yc)))):
            arr = (ri[k], tb[k])
    return (arr[0], ri[-1], arr[1]) if arr else (ri[-1], ri[-1], tb[-1])

def main():
    dirs = [os.path.abspath(d) for d in sys.argv[1:]]
    if len(dirs) != 3:
        print('3 case diri gerekli (kaba orta ince).'); return
    print('=== MESH CONVERGENCE: iso-arrest-kesim r_inf ===\n')
    print('%-42s %8s %10s %12s %10s %8s' % ('case', 'dx', 'NYxNZ', 'r_arrest', 'r_raw', 'arr_tb'))
    vals = []; dxs = []; level_rows = []
    for d in dirs:
        M = read_mesh(d); dx = M['DY']
        p = os.path.join(d, 'iso_arrest.csv')
        if not os.path.exists(p):
            print('%-42s  iso_arrest.csv YOK (once kosulmali)' % os.path.basename(d)); return
        a, raw, atb = arrest_iso(p); vals.append(a); dxs.append(dx)
        level_rows.append([os.path.basename(d), dx, M['NY'], M['NZ'], '%.4f' % a, '%.4f' % raw, '%.0f' % atb])
        print('%-42s %8.3f %8dx%-3d %12.4f %10.4f %8.0f'
              % (os.path.basename(d), dx, M['NY'], M['NZ'], a, raw, atb))
    # ---- CSV cikti (ozet) ----
    out_csv = os.path.join(os.path.dirname(dirs[0]), 'convergence_Bn0p10_cap2_summary.csv')
    gci_info = {}
    f1, f2, f3 = vals
    r21 = dxs[0] / dxs[1]; r32 = dxs[1] / dxs[2]   # genelde 2,2
    e21 = f2 - f1; e32 = f3 - f2
    print('\n--- farklar ---  f2-f1=%+.4f  f3-f2=%+.4f' % (e21, e32))
    if abs(e21) < 1e-9 or abs(e32) < 1e-9:
        print('  Fark ~0 -> zaten yakinsamis (metrik cozunurluk tabani).'); return
    Rc = e32 / e21
    print('  yakinsama orani R=e32/e21=%.3f  (%s)'
          % (Rc, 'MONOTON' if 0 < Rc < 1 else ('OSILATUAR' if Rc < 0 else 'IRAKSIYOR')))
    if not (0 < Rc < 1):
        print('  UYARI: monoton degil -> GCI guvenilmez, daha ince seviye (dx=0.005) gerekebilir.')
    try:
        p_ord = math.log(abs(e21 / e32)) / math.log(r32)
        f_ext = f3 + (f3 - f2) / (r32**p_ord - 1)
        gci_f = FS * abs(e32 / f3) / (r32**p_ord - 1)
        gci_m = FS * abs(e21 / f2) / (r21**p_ord - 1)
        d_m = abs(f2 - f_ext) / f_ext * 100; d_f = abs(f3 - f_ext) / f_ext * 100
        decision = ('orta mesh yeterli (<3%)' if d_m < 3 else
                    ('ince mesh gerekli' if d_f < 3 else 'ince bile yakinsamamis -> dx=0.005/c-reset'))
        print('\n--- Richardson / GCI ---')
        print('  gozlenen mertebe p   = %.2f' % p_ord)
        print('  ekstrapolasyon r_inf = %.4f  (dx->0)' % f_ext)
        print('  GCI(ince)  = %.2f%%  -> %.4f +/- %.4f' % (100*gci_f, f3, gci_f*f3))
        print('  GCI(orta)  = %.2f%%  -> %.4f +/- %.4f' % (100*gci_m, f2, gci_m*f2))
        print('\n--- KARAR ---  orta sapma=%.1f%%  ince sapma=%.1f%%  -> %s' % (d_m, d_f, decision))
        gci_info = dict(R=Rc, p=p_ord, f_ext=f_ext, gci_f=100*gci_f, gci_m=100*gci_m, d_m=d_m, d_f=d_f, decision=decision)
    except (ValueError, ZeroDivisionError) as ex:
        print('  GCI hesaplanamadi (%s).' % ex)
        gci_info = dict(R=Rc, hata=str(ex))
    # ---- CSV yaz ----
    with open(out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['# MESH CONVERGENCE: iso-arrest-kesim r_inf (Bn=0.1 cap2 mPap=1e4)'])
        w.writerow(['level', 'dx', 'NY', 'NZ', 'r_arrest', 'r_raw', 'arrest_tbar'])
        w.writerows(level_rows)
        w.writerow([])
        w.writerow(['# GCI / Richardson'])
        for k, v in gci_info.items():
            w.writerow([k, ('%.4f' % v) if isinstance(v, float) else v])
    print('\nCSV yazildi: %s' % out_csv)

if __name__ == '__main__':
    main()
