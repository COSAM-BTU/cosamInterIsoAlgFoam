#!/usr/bin/env python3
"""2D mesh-convergence figure (cap1.5, Bn=0.10, hr1), notIncluded dahil.
SOL : r_iso(alpha=0.5, interpolasyon) vs t_bar, 3 mesh + Valette 2D transient (TUM t_bar).
SAG : son r_iso vs dx -> YAKINSAMA KALITESI (monoton mu? en ince ASIYOR mu?).
iso = r_iso (iso_arrest.csv). Valette ref: cases/2D/valetteRef/. Cikti: fig_2D_meshconv.png + ozet."""
import csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CD = os.path.dirname(os.path.abspath(__file__))
REF = "/home/ismailhos/phdPaper/cases/2D/valetteRef/valette_2D_Bn_0p1_hr1.csv"
meshes = [
    ("mesh125x40",              0.040, "125$\\times$40",   "#d62728"),
    ("mesh500x160",             0.010, "500$\\times$160",  "#1f77b4"),
    ("mesh1000x320_notIncluded",0.005, "1000$\\times$320 (notIncl.)", "#2ca02c"),
]

def load_iso(nm):
    f = os.path.join(CD, f"2D_dambreak_Bn0p10_hr1_cap1p5_{nm}", "iso_arrest.csv")
    tb, ri = [], []
    for r in csv.DictReader(open(f)):
        tb.append(float(r["t_bar"])); ri.append(float(r["r_iso"]))
    return np.array(tb), np.array(ri)

def load_ref():
    t, r = [], []
    for row in csv.reader(open(REF)):
        if row and row[0].strip():
            try: t.append(float(row[0])); r.append(float(row[1]))
            except ValueError: pass
    return np.array(t), np.array(r)

ref_t, ref_r = load_ref()
VAL = ref_r[-1]  # Valette 2D plato (~1.782)

fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.2, 5.3))

# --- SOL: transient (tum t_bar) ---
finals, dxs = [], []
print(f"Valette 2D ref son = {VAL:.4f}")
print(f"  {'mesh':>26} {'dx':>6} {'son r_iso':>10} {'vs Val%':>8} {'RMS(t>=10)':>11}")
for nm, dx, lab, c in meshes:
    tb, ri = load_iso(nm)
    axL.plot(tb, ri, "-", color=c, lw=2.0, label=f"{lab}  (dx={dx})")
    finals.append(ri[-1]); dxs.append(dx)
    m = tb >= 10
    rms = np.sqrt(np.mean((ri[m] - np.interp(tb[m], ref_t, ref_r))**2))
    print("  %-26s dx=%.3f  son r_iso=%.4f  vs Val=%+.1f%%  RMS=%.4f" % (nm, dx, ri[-1], 100*(ri[-1]/VAL-1), rms))
axL.plot(ref_t, ref_r, "k:o", lw=2.4, ms=4, label="Valette 2D transient", zorder=10)
axL.axhline(VAL, color="gray", ls="-.", lw=1.0, alpha=0.6)
axL.set_xlim(0, 1080); axL.set_ylim(0.95, 2.00)
axL.set_xlabel(r"boyutsuz zaman  $\bar{t}$", fontsize=11)
axL.set_ylabel(r"run-out  $\bar{r}=r/r_0$  (iso, $\alpha$=0.5)", fontsize=11)
axL.set_title("(a) 2D run-out transient: mesh inceltme vs Valette", fontsize=11)
axL.grid(True, alpha=0.3); axL.legend(fontsize=8.5, loc="lower right")

# --- SAG: son r_iso vs dx (yakinsama kalitesi) ---
dxs = np.array(dxs); finals = np.array(finals)
order = np.argsort(dxs)
axR.plot(dxs[order], finals[order], "o-", color="purple", ms=11, lw=2.2, zorder=5)
for dx, fv in zip(dxs, finals):
    axR.annotate(f"{fv:.3f}", (dx, fv), textcoords="offset points", xytext=(8,6), fontsize=9.5)
axR.axhline(VAL, color="k", ls=":", lw=2.0, label=f"Valette 2D = {VAL:.4f}")
axR.axhspan(VAL*0.98, VAL*1.02, color="green", alpha=0.10, label="Valette ±2%")
axR.annotate("en ince mesh\nAŞIYOR (finger)", (0.005, 1.9107), fontsize=9, color="#2ca02c",
             ha="left", xytext=(0.0065, 1.93), arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=0.9))
axR.set_xscale("log"); axR.invert_xaxis()
axR.set_xlabel(r"hücre boyutu  $\Delta x$  (sağa doğru $\rightarrow$ inceliyor)", fontsize=11)
axR.set_ylabel(r"son run-out  $\bar{r}_{\rm iso}$  ($\bar{t}$=1080)", fontsize=11)
axR.set_title("(b) Yakınsama YOK: en ince mesh Valette'i aşıyor", fontsize=11)
axR.grid(True, which="both", alpha=0.3); axR.legend(fontsize=9, loc="upper left")

plt.tight_layout()
out = os.path.join(CD, "fig_2D_meshconv.png")
plt.savefig(out, dpi=160); print("wrote", out)
