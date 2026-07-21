# cap0 (2D hr1 cap sweep uyesi)

2D dam-break, Bn=0.10, h0/r0=1, birebir-Valette creeping olcegi.
SABLON: ../../2D_dambreak_Bn0p10_hr1_cap2_mesh250x80 (uretim vakasi, dx=0.02, 250x80).
TEK FARK: muMaxKin = 0 m2/s -> dinamik cap = 0 Pa.s.
Diger her sey ayni: mPap=1e4, gammaMin=1e-3, alphaAlg=0.3, r_alg=1000, endTime=1200 (t_bar~1080).
NOT: cap=0 -> Papanastasiou terimi tamamen kapali = SAF ALG kontrol vakasi (varsayilan listede DEGIL).

Kosturma: master script kullanin (../run_capsweep_master.sh). HENUZ KOSULMADI.
