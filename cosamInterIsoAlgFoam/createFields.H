#include "createRDeltaT.H"

Info<< "Reading field p_rgh\n" << endl;
volScalarField p_rgh
(
    IOobject
    (
        "p_rgh",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

Info<< "Reading field U\n" << endl;
volVectorField U
(
    IOobject
    (
        "U",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

#include "createPhi.H"


Info<< "Reading transportProperties\n" << endl;
immiscibleIncompressibleTwoPhaseMixture mixture(U, phi);

volScalarField& alpha1(mixture.alpha1());
volScalarField& alpha2(mixture.alpha2());

const dimensionedScalar& rho1 = mixture.rho1();
const dimensionedScalar& rho2 = mixture.rho2();


// Need to store rho for ddt(rho, U)
volScalarField rho
(
    IOobject
    (
        "rho",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT
    ),
    alpha1*rho1 + alpha2*rho2
);
rho.oldTime();


// Mass flux
surfaceScalarField rhoPhi
(
    IOobject
    (
        "rhoPhi",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::NO_WRITE
    ),
    fvc::interpolate(rho)*phi
);


typedef incompressibleInterPhaseTransportModel
    <
        immiscibleIncompressibleTwoPhaseMixture
    > transportModelType;

autoPtr<transportModelType> turbulence
(
    new transportModelType
    (
        rho, U, phi, rhoPhi, mixture
    )
);


#include "readGravitationalAcceleration.H"
#include "readhRef.H"
#include "gh.H"


volScalarField p
(
    IOobject
    (
        "p",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    p_rgh + rho*gh
);

label pRefCell = 0;
scalar pRefValue = 0.0;
setRefCell
(
    p,
    p_rgh,
    pimple.dict(),
    pRefCell,
    pRefValue
);

if (p_rgh.needReference())
{
    p += dimensionedScalar
    (
        "p",
        p.dimensions(),
        pRefValue - getRefCellValue(p, pRefCell)
    );
    p_rgh = p - rho*gh;
}

mesh.setFluxRequired(p_rgh.name());
mesh.setFluxRequired(alpha1.name());

#include "createMRF.H"
#include "createFvOptions.H"
#include "createPorosity.H"

isoAdvection advector(alpha1, phi, U);


// ====================================================================== //
//  Augmented-Lagrangian Bingham (mayonnaise / heavy phase only)
// ====================================================================== //
//
// Reads Bingham/ALG parameters as top-level entries of transportProperties:
//
//   nuMayo        kinematic plastic viscosity of the heavy phase     [m²/s]
//   tau_y         kinematic yield stress      (= τ_y / ρ_mayo)        [m²/s²]
//   r_alg         augmentation parameter      (≈ nuMayo · 10–100)     [m²/s]
//   alphaAlg      threshold; ALG enforced only where alpha1 > this   [-]
//
// γ, λ are kinematic (per ρ_mayo). Source on momentum is multiplied by
// rho_mayo · alpha1 below in UEqn.H.

IOdictionary algProperties
(
    IOobject
    (
        "transportProperties", runTime.constant(), mesh,
        IOobject::MUST_READ, IOobject::NO_WRITE
    )
);

dimensionedScalar nuMayo
(
    "nuMayo",
    dimViscosity,
    algProperties
);

dimensionedScalar tau_y
(
    "tau_y",
    dimViscosity/dimTime,
    algProperties
);

dimensionedScalar r_alg
(
    "r_alg",
    dimViscosity,
    algProperties
);

scalar alphaAlg = algProperties.lookupOrDefault<scalar>("alphaAlg", 0.5);

// ---------- Sub-yield Papanastasiou stabilisation (hybrid) ----------
// Extra kinematic viscosity in cells where |T| < τ_y, capped at muMax.
// Smoothly weighted by (1 - |T|/τ_y) so yielded bulk gets pure ALG.

dimensionedScalar mPap
(
    "mPap",
    dimTime,
    algProperties.lookupOrDefault<scalar>("mPap", 100.0)
);
dimensionedScalar muMaxKin
(
    "muMaxKin",
    dimViscosity,
    algProperties.lookupOrDefault<scalar>("muMaxKin", 0.01)
);
dimensionedScalar gammaMin
(
    "gammaMin",
    dimless/dimTime,
    algProperties.lookupOrDefault<scalar>("gammaMin", 1e-3)
);

Info<< "ALG-Bingham:  nuMayo="    << nuMayo.value()
    <<           "  tau_y/rho="   << tau_y.value()
    <<           "  r_alg="       << r_alg.value()
    <<           "  alphaAlg="    << alphaAlg
    <<           "  mPap="        << mPap.value()
    <<           "  muMaxKin="    << muMaxKin.value()
    <<           "  gammaMin="    << gammaMin.value() << endl;

Info<< "Reading/initialising field gamma\n" << endl;
volSymmTensorField gamma
(
    IOobject
    (
        "gamma", runTime.timeName(), mesh,
        IOobject::READ_IF_PRESENT, IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedSymmTensor("0", dimless/dimTime, symmTensor::zero)
);

Info<< "Reading/initialising field lambda\n" << endl;
volSymmTensorField lambda
(
    IOobject
    (
        "lambda", runTime.timeName(), mesh,
        IOobject::READ_IF_PRESENT, IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedSymmTensor("0", dimViscosity/dimTime, symmTensor::zero)
);
