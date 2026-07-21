#!/bin/bash
# hr10 cap sweep: cap=1,5,10 sirayla (cap=2 zaten yapildi). tc=1.1111, R0=0.1 (case scriptlerinde).
PHD=/home/ismailhos/phdPaper
RES=$PHD/results/hr10_capsweep_results.txt
echo "===== hr10 CAP SWEEP (Bn=0.1, dx=0.01) $(date) =====" > "$RES"
for CAP in 1 5 10; do
  D=$PHD/cases/2D/hr10_capsweep/2D_dambreak_Bn0p10_hr10_cap${CAP}
  echo "[$(date)] ===== cap=$CAP BASLIYOR ====="
  bash "$D/run_case.sh"
  python3 "$D/compute_iso_arrest.py" "$D" 1.1111 > "$D/log.iso_arrest" 2>&1
  echo "" >> "$RES"; echo "--- cap=$CAP ---" >> "$RES"
  cat "$D/log.iso_arrest" >> "$RES"
  echo "cell-center son (r/r0,h/h0): $(tail -1 $D/r_h_transient.csv)" >> "$RES"
  echo "DONE" > "$PHD/logs/log.hr10_cap${CAP}_DONE"
  echo "[$(date)] ===== cap=$CAP BITTI ====="
done
echo "" >> "$RES"; echo "===== BITTI $(date) =====" >> "$RES"
echo "DONE" > "$PHD/logs/log.HR10_CAPSWEEP_DONE"
