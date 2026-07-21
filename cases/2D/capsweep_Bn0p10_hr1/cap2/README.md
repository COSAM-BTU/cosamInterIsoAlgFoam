# cap2 (2D hr1 cap sweep uyesi)

2D dam-break, Bn=0.10, h0/r0=1, birebir-Valette creeping olcegi.
SABLON: ../../2D_dambreak_Bn0p10_hr1_cap2_mesh250x80 (uretim vakasi, dx=0.02, 250x80).
TEK FARK: muMaxKin = 2000 m2/s -> dinamik cap = 2 Pa.s.
Diger her sey ayni: mPap=1e4, gammaMin=1e-3, alphaAlg=0.3, r_alg=1000, endTime=1200 (t_bar~1080).


Kosturma: master script kullanin (../run_capsweep_master.sh). HENUZ KOSULMADI.

## VERI PROVENANSI (2026-06-12)
Bu case yeniden kosulmadi; cap=2 sweep noktasinin verisi uretim kosusu
2D_dambreak_Bn0p10_hr1_cap2_mesh250x80'den geldi (capsweep_results.txt'te
"YENIDEN KOSULMADI" notuyla kayitli). Makale icin cap=1.5 secildigi icin
cap2 mesh-convergence klasorleri 2026-06-12'de silindi; silinmeden once o
kosunun turetilmis ciktilari buraya kopyalandi:
  - iso_arrest.csv      (iso yield-arrest zaman serisi, mesh 250x80)
  - h_transient.csv   (yukseklik h(t), mesh 250x80)
Ozet metrikler ayrica ../capsweep_results.txt ve kok dizindeki
convergence_Bn0p10_cap2_* dosyalarinda durmaktadir.
