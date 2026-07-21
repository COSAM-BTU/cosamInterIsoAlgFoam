#!/usr/bin/env python3
"""
Compute h_over_h0 transient curve for a 2D Bn dam-break case.

Geometry (blockMesh): 1 cell in x, ny in y (lateral spread), nz in z (vertical, gravity).
Initial dam: alpha.mayo = 1 in y in [0, 0.1], z in [0, 0.1].

r(t) = max y over ALL cells where alpha.mayo > 0.5  (canonical run-out)
h(t) = max z over ALL cells where alpha.mayo > 0.5
h_over_h0 = h(t) / 0.1

Cell ordering for blockMesh hex (1, ny, nz): index i = iy + iz*ny.
"""
import os, re, sys

CASE = os.path.dirname(os.path.abspath(__file__))
NY, NZ = 400, 200
LY, LZ = 0.8, 0.4
DY = LY / NY
DZ = LZ / NZ
R0 = 0.1
H0 = 0.1
ALPHA_THRESHOLD = 0.5


def read_internal_field(path):
    """Read OpenFOAM internalField scalar list. Supports ascii and 'uniform' values."""
    with open(path, "r") as f:
        text = f.read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(\s*", text)
    if m:
        n = int(m.group(1))
        start = m.end()
        end = text.find(")", start)
        chunk = text[start:end]
        vals = [float(x) for x in chunk.split()]
        if len(vals) != n:
            raise RuntimeError(f"{path}: expected {n} values, got {len(vals)}")
        return vals
    m = re.search(r"internalField\s+uniform\s+([\-\d\.eE+]+)\s*;", text)
    if m:
        v = float(m.group(1))
        return [v] * (NY * NZ)
    raise RuntimeError(f"{path}: cannot parse internalField")


def list_time_dirs():
    out = []
    for name in os.listdir(CASE):
        full = os.path.join(CASE, name)
        if not os.path.isdir(full):
            continue
        try:
            t = float(name)
        except ValueError:
            continue
        if not os.path.exists(os.path.join(full, "alpha.mayo")):
            continue
        out.append((t, full))
    out.sort(key=lambda x: x[0])
    return out


def main():
    times = list_time_dirs()
    if not times:
        print("no reconstructed time dirs found", file=sys.stderr)
        sys.exit(1)
    rows = []
    for t, d in times:
        path = os.path.join(d, "alpha.mayo")
        try:
            vals = read_internal_field(path)
        except Exception as e:
            print(f"skip t={t}: {e}", file=sys.stderr)
            continue
        # canonical: max over ALL cells with alpha > threshold
        # index = iy + iz*NY  ->  iy = i % NY,  iz = i // NY
        iy_max = -1
        iz_max = -1
        for i, v in enumerate(vals):
            if v > ALPHA_THRESHOLD:
                iy = i % NY
                iz = i // NY
                if iy > iy_max:
                    iy_max = iy
                if iz > iz_max:
                    iz_max = iz
        r = (iy_max + 0.5) * DY if iy_max >= 0 else 0.0
        h = (iz_max + 0.5) * DZ if iz_max >= 0 else 0.0
        rows.append((t, h / H0))
    out = os.path.join(CASE, "h_transient.csv")
    with open(out, "w") as f:
        f.write("t,h_over_h0\n")
        for t, h in rows:
            f.write(f"{t:.4f},{h:.4f}\n")
    print(f"wrote {out} with {len(rows)} rows")
    print("first/last:")
    if rows:
        print(rows[0])
        print(rows[-1])


if __name__ == "__main__":
    main()
