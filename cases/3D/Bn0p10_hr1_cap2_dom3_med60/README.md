# 3Dcyl Bn=0.10 hr1 cap2 — DOMAIN-3 MEDIUM (sweep-ready taslak)

Valette1to1 creeping (rho=0.001, g=1000, k=1 Pa·s, tau0=0.1, h0=r0=1), Bn=0.10, cap=2 (muMaxKin=2000),
çeyrek-silindir (xMin/yMin symmetryPlane). `capsweep_Bn0p10_hr1/cap2`'den uyarlandı — TEK fark domain+mesh.

## Domain + mesh (YENİ)
- **Domain 3×3×1.5** (önceki 4×4×1.6 yerine). Bn=0.01 (en çok yayılan, Valette 3D r_inf≈2.60) için
  boyutlandırıldı; yanal 3 = 3·r0 → asimptot 2.60'a ~0.40 marji (Bn=0.01'de finger ile sınırda; gerekirse
  3.3-3.5'e çık). Bn=0.10 için (r_inf≈1.5) fazlasıyla yeterli.
- **Mesh 60×60×30 = 108.000 hücre, dx=dy=dz=0.05 → 20 hücre/r0** (kaba 12.5 ↔ 2D-ince 50 arası "medium",
  kübik). Kolon r0=h0=1 değişmedi (setFields radius=1, p2 z=1).

## Metrikler
- `compute_r_h.py` (cell-center r,h; NX,NY,NZ=60,60,30, LX,LY,LZ=3,3,1.5).
- `compute_iso_arrest_3D.py . 60 60 30 3 3 1.5 1 1.1111` (iso radyal + yield-arrest).
- `compute_bulk_3D.py` (**kalınlık-eşikli BULK**: H≥2 hücre → 1-hücre Liu VOF-finger'ı dışlar → plato).

## Koşu
`bash run_case.sh` (blockMesh→0.orig→setFields→decomposePar(48)→solver→reconstruct→compute_r_h+iso+bulk).
endTime=1200 (t̄≈1080). Tahmini ~3-4 saat (108k hücre, finer dt).

## Beklenti (doğrulanacak)
Bulk metrik (H≥2) Valette 3D (1.5477) civarı vermeli; medium mesh bulk profilini daha temiz çözmeli.
Ham iso/cc'nin finger yüzünden yine bir miktar süründürmesi BEKLENİR (mesh inceltme finger'ı SİLMEZ — bkz
`results/MESH_CONVERGENCE.md`); düzeltme bulk metriğiyle.

**DURUM: KURULDU, HENÜZ KOŞULMADI — onay bekleniyor.**
