#!/bin/bash
# ============================================================================
# 2D hr1 Bn SWEEP @ cap=1.5 Pa.s (capsweep karari 2026-06-11; eski cap=2 yerine)
# SIRAYLA kosar. Bn=0.10 KOSULMAZ: 2D_capsweep_Bn0p10_hr1/cap1p5 uretim kosusu
# olarak kullanilir ve sonucu basta results dosyasina enjekte edilir.
# KULLANIM:
#   nohup bash /home/ismailhos/phdPaper/scripts/run_bnsweep_cap1p5.sh \
#         > /home/ismailhos/phdPaper/logs/log.bnsweep_cap1p5_master 2>&1 &
# ============================================================================
PHD=/home/ismailhos/phdPaper
SCRIPTS=$PHD/scripts
RES=$PHD/results/bnsweep_cap1p5_results.txt

echo "===== 2D Bn SWEEP (dx=0.02, cap=1.5, mPap=1e4) BASLADI $(date) =====" > "$RES"

# --- Bn=0.10: capsweep'teki uretim-kalitesinde kosudan enjekte ---
D10=$PHD/cases/2D/capsweep_Bn0p10_hr1/cap1p5
{
  echo ""
  echo "--- Bn=0.10 (YENIDEN KOSULMADI; capsweep cap1p5 kosusu) ---"
  cat "$D10/log.iso_arrest"
  echo "cell-center son (t,r/r0,h/h0): $(tail -1 "$D10/r_h_transient.csv")"
  python3 "$SCRIPTS/compare_valette.py" "$D10" 0.10 1.1111
} >> "$RES"
echo "DONE" > "$PHD/logs/log.bnsweep15_Bn10_DONE"

# --- 6 Bn sirayla ---
CASES="01:0.01:1.0101 03:0.03:1.0309 05:0.05:1.0526 07:0.07:1.0753 15:0.15:1.1765 20:0.20:1.2500"
for c in $CASES; do
  TAG=${c%%:*}; rest=${c#*:}; BN=${rest%%:*}; TC=${rest#*:}
  D=$PHD/cases/2D/bnsweep_cap1p5/2D_dambreak_Bn0p${TAG}_hr1_cap1p5
  echo "[$(date)] ===== Bn=$BN BASLIYOR ====="
  bash "$D/run_case.sh"
  python3 "$D/compute_iso_arrest.py" "$D" $TC > "$D/log.iso_arrest" 2>&1
  {
    echo ""
    echo "--- Bn=$BN (tc=$TC) ---"
    cat "$D/log.iso_arrest"
    echo "cell-center son (t,r/r0,h/h0): $(tail -1 "$D/r_h_transient.csv")"
    python3 "$SCRIPTS/compare_valette.py" "$D" $BN $TC
  } >> "$RES"
  echo "DONE" > "$PHD/logs/log.bnsweep15_Bn${TAG}_DONE"
  echo "[$(date)] ===== Bn=$BN BITTI ====="
done

echo "" >> "$RES"; echo "===== TUM SWEEP BITTI $(date) =====" >> "$RES"
echo "DONE" > "$PHD/logs/log.BNSWEEP15_DONE"
