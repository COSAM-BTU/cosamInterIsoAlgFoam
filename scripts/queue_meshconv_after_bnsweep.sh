#!/bin/bash
# KUYRUK: Bn sweep (cap=1.5) bitince mesh ailesini otomatik baslatir.
# Calisma mantigi: log.BNSWEEP15_DONE belirene kadar 5 dk arayla bekler
# (en fazla 8 saat), sonra run_meshconv_cap1p5.sh'i kosar.
PHD=/home/ismailhos/phdPaper
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
i=0
until [ -f "$PHD/logs/log.BNSWEEP15_DONE" ]; do
  sleep 300; i=$((i+1))
  if [ $i -gt 96 ]; then echo "[$(date)] TIMEOUT: Bn sweep 8 saatte bitmedi, kuyruk iptal"; exit 1; fi
done
echo "[$(date)] Bn sweep bitti -> mesh ailesi basliyor"
bash "$SCRIPTS/run_meshconv_cap1p5.sh"
