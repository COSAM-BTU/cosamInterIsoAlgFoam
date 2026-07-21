# 2D hr1 CAP SWEEP (Bn=0.10, dx=0.02, mesh 250x80, mPap=1e4)

**Amac:** mu_cap'in transient ve asimptot (run-out) uzerindeki etkisini sistematik olcmek;
"cap=2 Pa.s nasil/niye secildi" sorusunu makale icin belgelemek (03-cases.tex, Cumle 7).
Hipotez (kullanici hafizasi): cap=1 erken transienti (t_bar<~200) iyi yakalar ama asimptot sapar;
cap=2 hem transient hem asimptotu tutturur. Bu sweep bunu dogrulayacak/duzeltecek.

**Sablon:** ../2D_dambreak_Bn0p10_hr1_cap2_mesh250x80 (uretim vakasi). TEK degisen: muMaxKin.
Fizik: birebir-Valette creeping olcegi (rho=0.001, g=1000, k=1 Pa.s, tau0=0.1 Pa, h0=r0=1 m).
Hepsi ayni mesh (250x80, dx=0.02), ayni endTime=1200 s (t_bar~1080), ayni mPap=1e4 s.

## TAVAN MANTIGI (duzeltilmis)
Eklenen viskozite: mu_hyb = min( tau0*(1-exp(-m*gd))/max(gd,gammaMin), mu_cap ).
(1-exp(-m*gd))/gd AZALAN fonksiyon -> maksimumu gd=gammaMin'de:
  mu_Pap_max = tau0*(1-exp(-m*gammaMin))/gammaMin = 0.1*(1-e^-10)/1e-3 ~= 99.995 ~= 100 Pa.s
m*gammaMin = 10 >> 1 oldugu icin tavani m DEGIL gammaMin belirler (~tau0/gammaMin).
(gammaMin=0 olsaydi tavan tau0*m = 1000 Pa.s olurdu.)
SONUC: cap >= 100 Pa.s olan tum kosullar BIT-OZDES (kapak hicbir hucrede baglamaz).
Ust uc = cap100 = "ALG + uygulanmis haliyle TAM Papanastasiou".
Dogrulama: cap100 logunda "Hybrid: max muHybridKin" ~ 99995 gorulmeli (< 100000).

| case | muMaxKin [m2/s] | cap (dinamik) [Pa.s] | not |
|---|---|---|---|
| cap0    | 0       | 0    | SAF ALG (Papanastasiou kapali) |
| cap1    | 1000    | 1    | hipotez: transient sampiyonu |
| cap1p5  | 1500    | 1.5  | |
| cap2    | 2000    | 2    | KOSULMAYACAK: birebir ayni girdili mevcut uretim kosusu kullanilir (../2D_dambreak_Bn0p10_hr1_cap2_mesh250x80); sonucu master tarafindan results dosyasina otomatik eklenir |
| cap2p5  | 2500    | 2.5  | arsivdeki on-deneme degeri (temiz tekrar) |
| cap3    | 3000    | 3    | |
| cap5    | 5000    | 5    | |
| cap10   | 10000   | 10   | eski kampanya degeri |
| cap30   | 30000   | 30   | log basamak |
| cap100  | 100000  | 100  | UST UC: kapak baglamaz = ALG + tam Papanastasiou |
| cap300  | 300000  | 300  | KOSULMAYACAK (cap100 ile bit-ozdes) |
| cap1000 | 1000000 | 1000 | KOSULMAYACAK (cap100 ile bit-ozdes) |

**Varsayilan liste (9 yeni kosu, cap0 DAHIL; cap2 mevcut kosudan):** 0 1 1p5 2p5 3 5 10 30 100

**DURUM: HENUZ HICBIR CASE KOSULMADI.**

## Kosturma (tek seferde, sirayla)
    cd /home/ismailhos/phdPaper/2D_capsweep_Bn0p10_hr1
    nohup bash run_capsweep_master.sh > log.capsweep_master 2>&1 &
    nohup bash watch_capsweep.sh    > /dev/null            2>&1 &

Farkli liste icin: CAPS="..." ortam degiskeni (master VE watcher'a ayni verilmeli).

## Izleme / cikti
- Anlik durum:            bash status_capsweep.sh
- Case bittikce ozet:     capsweep_watch.txt
- Tum sonuc + Valette kiyasi (DIREKT, Bn=0.1): capsweep_results.txt
- Tamamlanma isaretleri:  log.capN_DONE (her case), log.CAPSWEEP_DONE (hepsi)

Tahmini sure: ~30-40 dk/case x 9 = ~5-6 saat (48 cekirdek, sirayla).
Yuksek cap'lerde (30-100) PIMPLE yakinsamasi yavaslayabilir; sure artabilir,
asiri sonumden dolayi t_bar~1080'de arrest gelmeyebilir (yorum asamasinda dikkat).
