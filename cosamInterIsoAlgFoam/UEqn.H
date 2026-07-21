    MRF.correctBoundaryVelocity(U);

    // -----------------------------------------------------------
    //  ALG (mayonnaise / heavy phase) augmentation
    //
    //  Mask  : ALG enforced where alpha1 > alphaAlg (≈ 0.5–0.9)
    //  μ_alg : 0.5 · ρ_mayo · α_mask · r_alg   (extra dynamic visc)
    //  src   : ρ_mayo · α_mask · ∇·(λ − r γ)   (force/volume)
    // -----------------------------------------------------------
    volScalarField algMask
    (
        "algMask",
        max
        (
            dimensionedScalar("zero", dimless, 0.0),
            (alpha1 - dimensionedScalar("aT", dimless, alphaAlg))
          / (scalar(1) - alphaAlg)
        )
    );

    volScalarField muAlg
    (
        "muAlg",
        0.5 * rho1 * algMask * r_alg
    );

    // -----------------------------------------------------------
    //  Hybrid global Papanastasiou stabilisation (capped, mayo-only)
    //
    //  No sub-yield gate: extra viscosity active everywhere inside mayo
    //  to damp inertial transient (the dominant problem). Capped at
    //  muMaxKin to avoid full regularisation regime; ALG λ still enforces
    //  true yield ceiling.
    // -----------------------------------------------------------
    {
        volSymmTensorField D_now = symm(fvc::grad(U));
        volScalarField gammaDot = sqrt
        (
            scalar(2)*(D_now && D_now)
          + dimensionedScalar("vS", sqr(dimless/dimTime), VSMALL)
        );

        volScalarField muPapKin = tau_y
            * (scalar(1) - exp(-mPap*gammaDot))
            / max(gammaDot, gammaMin);

        volScalarField muHybridKin = min(muPapKin, muMaxKin);

        muAlg = muAlg + rho1 * algMask * muHybridKin;

        Info<< "Hybrid: max muHybridKin = " << gMax(muHybridKin.field())
            <<       "  cap = "              << muMaxKin.value() << endl;
    }

    tmp<volVectorField> algSource
    (
        rho1 * fvc::div(algMask * (lambda - r_alg*gamma))
    );

    fvVectorMatrix UEqn
    (
        fvm::ddt(rho, U) + fvm::div(rhoPhi, U)
      + MRF.DDt(rho, U)
      + turbulence->divDevRhoReff(rho, U)
      - fvm::laplacian(muAlg, U)
     ==
        fvOptions(rho, U)
      + algSource
    );

    #include "UEqnAddPorosity.H"

    UEqn.relax();

    fvOptions.constrain(UEqn);

    if (pimple.momentumPredictor())
    {
        solve
        (
            UEqn
         ==
            fvc::reconstruct
            (
                (
                    mixture.surfaceTensionForce()
                  - ghf*fvc::snGrad(rho)
                  - fvc::snGrad(p_rgh)
                ) * mesh.magSf()
            )
        );

        fvOptions.correct(U);
    }
