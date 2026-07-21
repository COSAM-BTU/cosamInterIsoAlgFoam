#!/bin/bash
# 3Dcyl valette1to1 case kosturucu (self-contained).
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
mkdir -p log
source /opt/openfoam2406/etc/bashrc
echo "[$(date)] blockMesh";      blockMesh > log/blockMesh.log 2>&1
echo "[$(date)] restore0Dir";    rm -rf 0 && cp -r 0.orig 0
echo "[$(date)] setFields";      setFields > log/setFields.log 2>&1
echo "[$(date)] decomposePar";   decomposePar -force > log/decomposePar.log 2>&1
echo "[$(date)] solver (48)";    mpirun -np 48 cosamInterIsoAlgFoam -parallel > log/cosamInterIsoAlgFoam.log 2>&1
echo "[$(date)] reconstructPar"; reconstructPar -newTimes > log/reconstructPar.log 2>&1
echo "[$(date)] compute_r_h";    python3 "$HERE/compute_r_h.py" > log/compute_r_h.log 2>&1
echo "[$(date)] compute_iso";    python3 "$HERE/compute_iso_arrest_3D.py" "$HERE" 120 120 60 3 3 1.5 1 1.1111 > log/iso_arrest.log 2>&1
echo "[$(date)] compute_bulk";   python3 "$HERE/compute_bulk_3D.py" > log/compute_bulk.log 2>&1
echo "[$(date)] DONE"; tail -n 2 h_transient.csv; cat log/compute_bulk.log; echo DONE > log/DONE.log
