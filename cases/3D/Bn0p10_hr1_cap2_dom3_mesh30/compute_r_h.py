#!/usr/bin/env python3
"""3D cyl quarter-box run-out: r(t)=max sqrt(xc^2+yc^2) (alpha>0.5), h(t)=max zc. R0=H0=1 (valette1to1 hr1).
Mesh: NX x NY x NZ over (LX,LY,LZ); flat i = ix + iy*NX + iz*NX*NY. Cikti: h_transient.csv."""
import os, re, sys
import numpy as np
CASE = os.path.dirname(os.path.abspath(__file__))
NX, NY, NZ = 30, 30, 15
LX, LY, LZ = 3.0, 3.0, 1.5
R0 = H0 = 1.0
ATHR = 0.5
def read_alpha(path, n):
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(\s*", txt)
    if m:
        nn = int(m.group(1)); s = m.end(); e = txt.find(")", s)
        return np.fromstring(txt[s:e], sep="\n")[:nn]
    m = re.search(r"internalField\s+uniform\s+([\-\d\.eE+]+)\s*;", txt)
    if m: return np.full(n, float(m.group(1)))
    raise RuntimeError(f"{path}: internalField okunamadi")
def main():
    n = NX*NY*NZ
    i = np.arange(n); ix = i % NX; iy = (i//NX) % NY; iz = i//(NX*NY)
    xc = (ix+0.5)*(LX/NX); yc = (iy+0.5)*(LY/NY); zc = (iz+0.5)*(LZ/NZ)
    rxy = np.sqrt(xc*xc + yc*yc)
    times = []
    for nm in os.listdir(CASE):
        f = os.path.join(CASE, nm)
        if os.path.isdir(f) and os.path.exists(os.path.join(f, "alpha.mayo")):
            try: times.append((float(nm), f))
            except ValueError: pass
    times.sort()
    rows = []
    for t, d in times:
        a = read_alpha(os.path.join(d, "alpha.mayo"), n)
        mask = a > ATHR
        r = float(rxy[mask].max()) if mask.any() else 0.0
        h = float(zc[mask].max()) if mask.any() else 0.0
        rows.append((t, h/H0))
    with open(os.path.join(CASE, "h_transient.csv"), "w") as fo:
        fo.write("t,h_over_h0\n")
        for t, h in rows: fo.write("%.4f,%.4f\n" % (t, h))
    print("wrote h_transient.csv (%d satir, 3D %dx%dx%d)" % (len(rows), NX, NY, NZ))
if __name__ == "__main__": main()
