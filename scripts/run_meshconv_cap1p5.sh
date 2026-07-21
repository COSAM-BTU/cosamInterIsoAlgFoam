#!/bin/bash
# ============================================================================
# Bn=0.1 cap=1.5 MESH AILESI: 3 yeni seviye sirayla (125x40 ~5dk, 500x160 ~2sa,
# 1000x320 ~7sa); dx=0.02 seviyesi = 2D_capsweep_Bn0p10_hr1/cap1p5 (HAZIR).
# Sonra Celik ucluleriyle GCI analizi (kaba-orta-ince ve orta-ince-enince).
# Normalde queue_meshconv_after_bnsweep.sh tarafindan otomatik baslatilir.
# ============================================================================
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
PHD=/home/ismailhos/phdPaper
TC=1.1111
L020=$PHD/cases/2D/capsweep_Bn0p10_hr1/cap1p5
RES=$PHD/results/convergence_Bn0p10_cap1p5_result.txt

for M in 125x40 500x160 1000x320; do
  L=$PHD/cases/2D/meshconv_cap1p5/2D_dambreak_Bn0p10_hr1_cap1p5_mesh$M
  echo "[$(date)] ===== mesh$M BASLIYOR ====="
  bash "$L/run_case.sh"
  python3 "$L/compute_iso_arrest.py" "$L" $TC > "$L/log.iso_arrest" 2>&1
  echo "DONE" > "$PHD/logs/log.meshconv15_${M}_DONE"
  echo "[$(date)] ===== mesh$M BITTI ====="
done

echo "[$(date)] ===== GCI ANALIZI ====="
{
  echo "===== MESH AILESI cap=1.5 (Bn=0.1, dx=0.02 seviyesi: capsweep/cap1p5) $(date) ====="
  echo ""
  echo "### Uclu 1: dx = 0.04 / 0.02 / 0.01 ###"
  python3 "$SCRIPTS/compute_convergence.py" \
      "$PHD/cases/2D/meshconv_cap1p5/2D_dambreak_Bn0p10_hr1_cap1p5_mesh125x40" "$L020" \
      "$PHD/cases/2D/meshconv_cap1p5/2D_dambreak_Bn0p10_hr1_cap1p5_mesh500x160"
  echo ""
  echo "### Uclu 2: dx = 0.02 / 0.01 / 0.005 ###"
  python3 "$SCRIPTS/compute_convergence.py" \
      "$L020" "$PHD/cases/2D/meshconv_cap1p5/2D_dambreak_Bn0p10_hr1_cap1p5_mesh500x160" \
      "$PHD/cases/2D/meshconv_cap1p5/2D_dambreak_Bn0p10_hr1_cap1p5_mesh1000x320"
} > "$RES" 2>&1
echo "DONE" > "$PHD/logs/log.MESHCONV15_DONE"
echo "[$(date)] ===== TAMAM ====="
