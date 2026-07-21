#!/bin/bash
# PURE PAPANASTASIOU valette1to1 (Bn=0.1, 250x80). Stok interIsoFoam +
# libPapanastasiouViscosity.so. SELF-CONTAINED.
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
mkdir -p log
source /opt/openfoam2406/etc/bashrc
echo "[$(date)] blockMesh";      blockMesh > log/blockMesh.log 2>&1
echo "[$(date)] restore0Dir";    rm -rf 0 && cp -r 0.orig 0
echo "[$(date)] setFields";      setFields > log/setFields.log 2>&1
echo "[$(date)] decomposePar";   decomposePar -force > log/decomposePar.log 2>&1
echo "[$(date)] solver (48)";    mpirun -np 48 interIsoFoam -parallel > log/interIsoFoam.log 2>&1
echo "[$(date)] reconstructPar"; reconstructPar -newTimes > log/reconstructPar.log 2>&1
echo "[$(date)] compute_r_h";    python3 "$HERE/compute_r_h.py" "$HERE" > log/compute_r_h.log 2>&1
echo "[$(date)] iso_arrest";     python3 "$HERE/compute_iso_arrest.py" "$HERE" 1.1111 > log/iso_arrest.log 2>&1
echo "[$(date)] DONE"; tail -n 2 h_transient.csv; echo DONE > log/DONE.log
