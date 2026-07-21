#!/bin/bash
# Anlik durum: cap=1.5 Bn sweep
PHD=/home/ismailhos/phdPaper
echo "Bn=0.10  HAZIR    (capsweep cap1p5 kosusundan)"
for c in "01 0.01" "03 0.03" "05 0.05" "07 0.07" "15 0.15" "20 0.20"; do
  set -- $c; TAG=$1; BN=$2
  D=$PHD/cases/2D/bnsweep_cap1p5/2D_dambreak_Bn0p${TAG}_hr1_cap1p5
  if [ -f "$D/log.DONE" ]; then
    printf "Bn=%-5s BITTI    son(t,r,h)=%s\n" "$BN" "$(tail -1 "$D/r_h_transient.csv" 2>/dev/null)"
  elif [ -f "$D/log.interIsoAlgFoam" ]; then
    T=$(grep '^Time = ' "$D/log.interIsoAlgFoam" 2>/dev/null | tail -1 | awk '{print $3}')
    printf "Bn=%-5s KOSUYOR  Time=%s / 1200\n" "$BN" "${T:-?}"
  else
    printf "Bn=%-5s BEKLIYOR\n" "$BN"
  fi
done
[ -f "$PHD/logs/log.BNSWEEP15_DONE" ] && echo "== TUM SWEEP TAMAM =="
