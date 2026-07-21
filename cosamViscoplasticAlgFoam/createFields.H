Info<< "Reading field p\n" << endl;
volScalarField p
(
    IOobject
    (
        "p", runTime.timeName(), mesh,
        IOobject::MUST_READ, IOobject::AUTO_WRITE
    ),
    mesh
);

Info<< "Reading field U\n" << endl;
volVectorField U
(
    IOobject
    (
        "U", runTime.timeName(), mesh,
        IOobject::MUST_READ, IOobject::AUTO_WRITE
    ),
    mesh
);

#include "createPhi.H"

label pRefCell = 0;
scalar pRefValue = 0.0;
setRefCell(p, pimple.dict(), pRefCell, pRefValue);
mesh.setFluxRequired(p.name());

// ---------------------------------------------------------------- //
// Bingham + ALG parameters
// ---------------------------------------------------------------- //
IOdictionary transportProperties
(
    IOobject
    (
        "transportProperties", runTime.constant(), mesh,
        IOobject::MUST_READ, IOobject::NO_WRITE
    )
);

dimensionedScalar nu("nu", dimViscosity, transportProperties);
dimensionedScalar tau_y
(
    "tau_y",
    dimViscosity/dimTime,           // [m^2/s^2] = kinematic yield "stress"/rho
    transportProperties
);
dimensionedScalar r_alg
(
    "r_alg",
    dimViscosity,                   // [m^2/s]  — augmentation, kinematic
    transportProperties
);

Info<< "Bingham:  nu = "    << nu.value()
    << "  tau_y/rho = "    << tau_y.value()
    << "  r_alg = "        << r_alg.value() << endl;

// ---------------------------------------------------------------- //
// ALG fields:  gamma (target rate), lambda (multiplier).
// Stored as kinematic (i.e. divided by rho).
// ---------------------------------------------------------------- //
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

#include "createFvOptions.H"
