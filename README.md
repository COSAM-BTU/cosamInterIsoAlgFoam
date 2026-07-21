# cosamInterIsoAlgFoam

An open-source OpenFOAM solver for viscoplastic free-surface flows. The solver extends `interIsoFoam` by coupling the geometric isoAdvector Volume of Fluid (VOF) method with a time-split augmented Lagrangian (ALG) implementation of the Bingham constitutive law and a novel hybrid Papanastasiou stabilisation confined to the heavy phase.

The repository also contains `cosamViscoplasticAlgFoam`, the single-phase precursor solver derived from `pimpleFoam`, together with all OpenFOAM cases and post-processing scripts of the accompanying paper.

## Features

- Geometric isoAdvector VOF interface capturing for immiscible two-phase flows
- Time-split Saramito–Roquet augmented Lagrangian iteration with a symmetric tensor Lagrange multiplier that saturates exactly at the yield stress in plug regions
- Hybrid stabilisation: a capped Papanastasiou-type viscosity contribution, active only inside the heavy phase, that damps the inertial transient without altering the asymptotic yield enforcement
- Smoothstep phase masking that confines the ALG updates to the yield-stress phase
- Single-phase precursor solver (`cosamViscoplasticAlgFoam`) verified against the analytical Bingham Poiseuille solution

## Requirements

- OpenFOAM v2406 or compatible

## Installation

```bash
# Clone the repository
git clone https://github.com/COSAM-BTU/cosamInterIsoAlgFoam.git
cd cosamInterIsoAlgFoam

# Compile the two-phase solver
cd cosamInterIsoAlgFoam
wmake

# Compile the single-phase solver
cd ../cosamViscoplasticAlgFoam
wmake
```

The executables are placed in `$FOAM_USER_APPBIN/cosamInterIsoAlgFoam` and `$FOAM_USER_APPBIN/cosamViscoplasticAlgFoam`.

## Method

The Bingham stress is reconstructed through auxiliary symmetric tensor fields (the target rate-of-deformation `gamma` and the Lagrange multiplier `lambda`):

```
tau = 2 (eta_p + r/2) D + lambda - r gamma
```

Once per time step, after the PIMPLE loop has converged, `gamma` is updated by the Saramito–Roquet projection and `lambda` by the Uzawa ascent step. In the two-phase solver both updates are weighted by a smoothstep mask on the volume fraction so that the multiplier lives only in the heavy phase.

The hybrid stabilisation adds a capped Papanastasiou-type viscosity inside the heavy phase,

```
mu_hyb = xi(alpha) * min( tau_y (1 - exp(-m gammaDot)) / gammaDot , mu_cap )
```

whose single free parameter `mu_cap` is calibrated once on the canonical dam-break case (see the paper, Section 3.3).

### Solver parameters (`constant/transportProperties`)

All viscoplastic quantities are stored in kinematic units (divided by the heavy-phase density); the values below are the production dam-break settings of the paper, where `rho_mayo = 0.001` so that the dynamic values `tau0 = 0.1 Pa`, `r = 1 Pa.s`, `mu_cap = 1.5 Pa.s` are recovered.

| Keyword | Meaning | Paper value |
|---|---|---|
| `tau_y` | kinematic yield stress [m2/s2] | `100` (dynamic 0.1 Pa, Bn = 0.10) |
| `r_alg` | ALG augmentation parameter, kinematic [m2/s] | `1000` (dynamic 1 Pa.s) |
| `muMaxKin` | hybrid viscosity cap, kinematic [m2/s] | `1500` (dynamic 1.5 Pa.s) |
| `mPap` | Papanastasiou exponent [s] | `10000` |
| `gammaMin` | strain-rate floor [1/s] | `1e-3` |
| `alphaAlg` | ALG mask threshold on alpha | `0.3` |

The number of inner Uzawa passes per time step is hard-coded in the solver (`nUzawaIter = 5` in `algLoop.H`).

## Repository structure

```
cosamInterIsoAlgFoam/
  cosamInterIsoAlgFoam/         Two-phase hybrid ALG solver (from interIsoFoam)
  cosamViscoplasticAlgFoam/     Single-phase ALG solver (from pimpleFoam)
  cases/
    validation/                 Poiseuille (Bn = 0.10-0.70) and lid-driven cavity
    2D/
      capsweep_Bn0p10_hr1/      Cap calibration sweep (10 values) + dt/2 sensitivity
      bnsweep_cap1p5/           Bingham-number sweep (Bn = 0.01-0.20)
      meshconv_cap1p5/          Mesh convergence (125x40, 500x160)
      method_comparison/        Split-ALG and pure Papanastasiou baselines
      snapshots/                Free-surface shape stations (tbar = 10, 100)
      valetteRef/               Digitised reference transients (Valette et al., 2021)
    3D/                         Cylindrical dam-break mesh convergence (30/60/120)
  scripts/                      Post-processing (front tracking, arrest, convergence)
```

The 2D production case of the paper (Bn = 0.10, `mu_cap = 1.5`, 250x80 mesh) is `cases/2D/capsweep_Bn0p10_hr1/cap1p5/`.

## Running a case

Each case directory contains the complete OpenFOAM setup (`0.orig/` or `0/`, `constant/`, `system/`) and a `run_case.sh` script. A typical sequence:

```bash
cd cases/2D/capsweep_Bn0p10_hr1/cap1p5
blockMesh
cp -r 0.orig 0
setFields
cosamInterIsoAlgFoam
```

Front position, column height and yield-arrest diagnostics are extracted from the saved fields with the scripts in `scripts/` (`compute_r_h.py`, `compute_iso_arrest.py`, `compute_iso_height.py`).

The digitised reference data in `cases/*/valetteRef/` are numerical values read from the published figures of Valette et al. (2021), J. Non-Newtonian Fluid Mech. 287:104447, and are provided for comparison purposes only; please cite the original paper when using them.

## Note on the porosity scaffolding

The two-phase solver retains an optional porous-drag scaffolding (`createPorosity.H`, `UEqnAddPorosity.H`, `porousCourantNo.H`, `porousAlphaCourantNo.H`) inherited from its development lineage. It is disabled by default (`porosityEnabled false`; no `porosityProperties` dictionary is present in any released case) and was not used in any simulation of the accompanying paper.

## Citation

If you use this solver in your research, please cite the accompanying paper:

> Hos, I., Aydinbakar, L. (2026). A hybrid augmented Lagrangian–Papanastasiou VOF solver for viscoplastic free-surface flows: an open-source OpenFOAM implementation validated on dam-break collapse. *Submitted.*

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
