#!/bin/bash
# KUYRUK: Mesh ailesi (cap=1.5) bitince fig11 sekil-karsilastirma figuru icin
# iki mini-restart kosusunu SIRAYLA calistirir (serial, ~dakikalar):
#   tbar10 : t=8'den restart, t=11.111'de yazim (t_bar=10)
#   tbar100: t=104'ten restart, t=111.111'de yazim (t_bar=100)
# log.MESHCONV15_DONE belirene kadar 5 dk arayla bekler (en fazla 12 saat).
PHD=/home/ismailhos/phdPaper
i=0
until [ -f "$PHD/logs/log.MESHCONV15_DONE" ]; do
  sleep 300; i=$((i+1))
  if [ $i -gt 144 ]; then echo "[$(date)] TIMEOUT: mesh ailesi 12 saatte bitmedi, kuyruk iptal"; exit 1; fi
done
echo "[$(date)] Mesh ailesi bitti -> snapshot mini-restartlari basliyor"
source /opt/openfoam2406/etc/bashrc
for NAME in tbar10 tbar100; do
  C=$PHD/cases/2D/snapshots/2D_snapshot_Bn0p10_hr1_cap1p5_$NAME
  echo "[$(date)] ===== $NAME BASLIYOR (serial) ====="
  (cd "$C" && interIsoAlgFoam > log.interIsoAlgFoam 2>&1)
  echo "[$(date)] ===== $NAME BITTI ====="
  ls "$C" | grep -E "^11?1?\.1" || true
done
echo "DONE" > "$PHD/logs/log.SNAPSHOTS_DONE"
echo "[$(date)] ===== SNAPSHOT KUYRUGU TAMAM ====="
