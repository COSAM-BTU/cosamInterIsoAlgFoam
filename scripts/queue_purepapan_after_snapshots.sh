#!/bin/bash
# KUYRUK: snapshot mini-restartlari bitince (log.SNAPSHOTS_DONE) pure
# Papanastasiou valette1to1 kosusunu baslatir. Method-comparison (fig06)
# yeni verisi: pureALG(cap0, mevcut) - hybrid(cap1.5, mevcut) - purePapan(bu).
PHD=/home/ismailhos/phdPaper
i=0
until [ -f "$PHD/logs/log.SNAPSHOTS_DONE" ]; do
  sleep 300; i=$((i+1))
  if [ $i -gt 288 ]; then echo "[$(date)] TIMEOUT: snapshots 24 saatte bitmedi, kuyruk iptal"; exit 1; fi
done
echo "[$(date)] Snapshots bitti -> purePapan valette1to1 basliyor"
bash "$PHD/cases/2D/method_comparison/2D_dambreak_Bn0p10_hr1_purePapan/run_case.sh"
echo "DONE" > "$PHD/logs/log.PUREPAPAN_DONE"
echo "[$(date)] ===== PUREPAPAN TAMAM ====="
