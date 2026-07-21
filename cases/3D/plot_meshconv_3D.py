#!/usr/bin/env python3
"""3D mesh-convergence figure (r=2: 30/60/120), cap2, Bn=0.10, dom 3x3x1.5.
SOL panel : r(t_bar) iso(α=0.5) vs bulk(H>=2), 3 mesh + Valette cizgisi.
SAG panel : finger = (iso - bulk) vs dx, log-log + O(dx)/O(dx^2) referans.
Cikti     : fig_3D_meshconv.png + meshconv_summary.csv
Valette 3D, h0/r0=1, Bn=0.1 -> r_bar = 1.5477 (valette_fig_11_c digitized)."""
import csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CD = os.path.dirname(os.path.abspath(__file__))
VALETTE = 1.5477
HY = 0.10  # yield kalinligi h_y = Bn*h0 = 0.10
# Valette transient referansi (cases/3D/valetteRef) — tum t_bar'da kiyas (sadece asimptot DEGIL)
REF = os.path.join(CD, "valetteRef", "valette_3D_Bn_0p1_hr1.csv")
def load_ref():
    t, r = [], []
    for row in csv.reader(open(REF)):
        if row and row[0].strip():
            try: t.append(float(row[0])); r.append(float(row[1]))
            except ValueError: pass
    return np.array(t), np.array(r)
ref_t, ref_r = load_ref()
meshes = [
    ("mesh30",  0.100, "coarse 30$^3$", "#d62728"),
    ("med60",   0.050, "med 60$^3$",    "#1f77b4"),
    ("mesh120", 0.025, "fine 120$^3$",  "#2ca02c"),
]

def load(m):
    """iso = r_iso (INTERPOLASYONLU alpha=0.5, Liu/Valette standardi) — iso_arrest.csv.
       bulk = r_bulk2 (H>=2) — bulk_runout.csv. Ortak t_bar'da hizalanir."""
    base = os.path.join(CD, f"Bn0p10_hr1_cap2_dom3_{m}")
    tb, rb2 = [], []
    with open(os.path.join(base, "bulk_runout.csv")) as fh:
        for r in csv.DictReader(fh):
            tb.append(float(r["t_bar"])); rb2.append(float(r["r_bulk2"]))
    tb = np.array(tb); rb2 = np.array(rb2)
    ti, ri = [], []
    with open(os.path.join(base, "iso_arrest.csv")) as fh:
        for r in csv.DictReader(fh):
            ti.append(float(r["t_bar"])); ri.append(float(r["r_iso"]))
    riso = np.interp(tb, np.array(ti), np.array(ri))
    return tb, riso, rb2

fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.0, 5.2))

# ---- SOL: transient ----
rows = []
dxs, fingers = [], []
for m, dx, lab, c in meshes:
    tb, rcc, rb2 = load(m)
    axL.plot(tb, rcc, "-",  color=c, lw=2.0, label=f"{lab}  iso ($\\alpha$=0.5)")
    axL.plot(tb, rb2, "--", color=c, lw=1.5, label=f"{lab}  bulk (H$\\geq$2)")
    fin = rcc[-1] - rb2[-1]
    dxs.append(dx); fingers.append(fin)
    rows.append((lab, dx, rcc[-1], 100*(rcc[-1]/VALETTE-1), rb2[-1], 100*(rb2[-1]/VALETTE-1), fin))
axL.plot(ref_t, ref_r, "k:o", lw=2.2, ms=3.5, label="Valette 3D transient", zorder=10)
axL.axhline(VALETTE, color="gray", ls="-.", lw=1.0, alpha=0.6, label=f"Valette asimptot {VALETTE:.4f}")
axL.set_xlim(0, 1080); axL.set_ylim(0.95, 1.75)
axL.set_xlabel(r"dimensionless time  $\bar{t}$", fontsize=11)
axL.set_ylabel(r"run-out  $\bar{r}=r/r_0$", fontsize=11)
axL.set_title("(a) Run-out transient: iso vs bulk vs Valette", fontsize=11)
axL.grid(True, which="both", alpha=0.3)
axL.legend(fontsize=7.5, loc="upper left", framealpha=0.9)

# ---- SAG: finger vs dx ----
dxs = np.array(dxs); fingers = np.array(fingers)
axR.loglog(dxs, fingers, "o-", color="purple", ms=10, lw=2.2, label="finger = iso $-$ bulk", zorder=5)
ref1 = fingers[-1]*(dxs/dxs[-1])**1
ref2 = fingers[-1]*(dxs/dxs[-1])**2
axR.loglog(dxs, ref1, "k--", lw=1.2, label=r"$O(\Delta x)$ ref")
axR.loglog(dxs, ref2, "k:",  lw=1.2, label=r"$O(\Delta x^2)$ ref")
for dx, fg in zip(dxs, fingers):
    axR.annotate(f"{fg:.3f}", (dx, fg), textcoords="offset points", xytext=(7,7), fontsize=9)
axR.set_xlabel(r"cell size  $\Delta x$", fontsize=11)
axR.set_ylabel(r"finger length  $\bar{r}_{\rm iso}-\bar{r}_{\rm bulk}$", fontsize=11)
axR.set_title("(b) Finger vanishes with refinement (numerical)", fontsize=11)
axR.grid(True, which="both", alpha=0.3)
axR.legend(fontsize=9, loc="upper left")

plt.tight_layout()
out = os.path.join(CD, "fig_3D_meshconv.png")
plt.savefig(out, dpi=160); print("wrote", out)

# ---- ozet CSV ----
with open(os.path.join(CD, "meshconv_summary.csv"), "w") as fo:
    fo.write("mesh,dx,iso_runout,iso_vs_valette_pct,bulk_runout,bulk_vs_valette_pct,finger\n")
    for lab, dx, iso, isop, blk, blkp, fin in rows:
        lab2 = lab.replace("$^3$", "^3")
        fo.write(f"{lab2},{dx},{iso:.4f},{isop:+.2f},{blk:.4f},{blkp:+.2f},{fin:.4f}\n")
print("wrote meshconv_summary.csv")
print(f"Valette 3D ref = {VALETTE}")
for lab, dx, iso, isop, blk, blkp, fin in rows:
    print(f"  {lab.replace('$^3$','^3'):12s} dx={dx:.3f}  iso={iso:.4f}({isop:+.2f}%)  bulk={blk:.4f}({blkp:+.2f}%)  finger={fin:.4f}")
