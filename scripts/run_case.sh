#!/bin/bash
# GENEL case kosturucu: blockMesh -> restore0 -> setFields -> decomposePar -> solver -> reconstruct -> compute_r_h
# Kullanim: bash run_case.sh <case_dir> [ncores]
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
CASE="$(cd "$1" && pwd)"
NP="${2:-48}"
cd "$CASE"
source /opt/openfoam2406/etc/bashrc
echo "[$(date)] blockMesh";      blockMesh > log.blockMesh 2>&1
echo "[$(date)] restore0Dir";    rm -rf 0 && cp -r 0.orig 0
echo "[$(date)] setFields";      setFields > log.setFields 2>&1
echo "[$(date)] decomposePar";   decomposePar -force > log.decomposePar 2>&1
echo "[$(date)] solver (np=$NP)"; mpirun -np $NP interIsoAlgFoam -parallel > log.interIsoAlgFoam 2>&1
echo "[$(date)] reconstructPar"; reconstructPar -newTimes > log.reconstructPar 2>&1
echo "[$(date)] compute_r_h";    python3 "$SCRIPTS/compute_r_h.py" "$CASE" > log.compute_r_h 2>&1
echo "[$(date)] DONE"; tail -n 2 r_h_transient.csv; echo DONE > log.DONE
