// =====================================================================
//  ALG (Uzawa) update for mayonnaise — true Bingham yield.
//
//  Called ONCE per timestep AFTER the PIMPLE outer-corrector loop
//  converges (so U, hence D, is fixed). Inside this scope, run a TRUE
//  inner Uzawa: with D fixed, λ converges to τ_y D/|D| in ~1-3 iters.
//
//  Both the γ projection and the λ update are masked with a
//  smoothstep on alpha1; outside the mask λ is frozen (retains
//  memory across timesteps).
// =====================================================================
{
    const label nUzawaIter = 5;   // inner iterations with U fixed

    // strain rate (fixed during inner loop)
    volSymmTensorField D = symm(fvc::grad(U));

    // smoothstep mask on alpha1
    volScalarField xi = min
    (
        max
        (
            (alpha1 - dimensionedScalar("aT", dimless, alphaAlg))
              / max(scalar(1) - alphaAlg, scalar(1e-6)),
            dimensionedScalar("zero", dimless, 0.0)
        ),
        dimensionedScalar("one", dimless, 1.0)
    );
    volScalarField yieldMask = xi*xi*(scalar(3) - scalar(2)*xi);

    for (label u = 0; u < nUzawaIter; ++u)
    {
        volSymmTensorField T_aux = lambda + r_alg*D;

        volScalarField magT = sqrt
        (
            0.5*(T_aux && T_aux)
          + dimensionedScalar
            ("vSmall", sqr(dimViscosity/dimTime), VSMALL)
        );

        volScalarField yieldFactor = max
        (
            dimensionedScalar("zero", dimless, 0.0),
            scalar(1) - tau_y/magT
        );

        gamma  = yieldMask * yieldFactor * T_aux / r_alg;
        // λ-update masked too: outside mayo (mask=0) λ stays frozen.
        // This prevents λ drift in interface/air cells where D≠0 but γ=0.
        lambda = lambda + yieldMask*r_alg*(D - gamma);
    }

    // Diagnostic
    volSymmTensorField T_final = lambda + r_alg*D;
    volScalarField magTfinal = sqrt
    (
        0.5*(T_final && T_final)
      + dimensionedScalar
        ("vSmall", sqr(dimViscosity/dimTime), VSMALL)
    );
    volScalarField magLambda = sqrt
    (
        0.5*(lambda && lambda)
      + dimensionedScalar
        ("vSmall", sqr(dimViscosity/dimTime), VSMALL)
    );

    Info<< "ALG: max|T| = "      << gMax(magTfinal.field())
        <<     "  max|lambda| = " << gMax(magLambda.field())
        <<     "  mayo cells = "
        << returnReduce
           (
               static_cast<label>(sum(pos(yieldMask.field() - 0.5))),
               sumOp<label>()
           )
        << " / " << returnReduce(mesh.nCells(), sumOp<label>())
        << endl;
}
