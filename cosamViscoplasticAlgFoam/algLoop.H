// Augmented-Lagrangian Uzawa update — exact Bingham yield projection.
//
//   D       = symm(grad U)
//   T_aux   = lambda + r*D
//   |T|     = sqrt( T:T / 2 )       (von-Mises-like second invariant)
//   gamma   = max(0, 1 - tau_y/|T|) * T / (2*(nu + r))
//   lambda <- lambda + r*(D - gamma)
//
// At cells where |T| <= tau_y the projection sets gamma = 0 (rigid plug).
// Stress is reconstructed implicitly through (lambda - r*gamma) in UEqn.
{
    volSymmTensorField D = symm(fvc::grad(U));
    volSymmTensorField T_aux = lambda + r_alg*D;

    // |T| = sqrt(0.5 T:T).  SMALL keeps the divisor finite in plug.
    volScalarField magT = sqrt(0.5*(T_aux && T_aux) + dimensionedScalar
        (
            "vSmall",
            sqr(dimViscosity/dimTime),
            VSMALL
        ));

    // Yield switch: 0 in plug, (1 - tau_y/|T|) outside.
    volScalarField yieldFactor
    (
        max
        (
            dimensionedScalar("zero", dimless, 0.0),
            scalar(1) - tau_y/magT
        )
    );

    // Projection (Saramito-Roquet): γ = T·max(0, 1 − τ_y/|T|) / r
    // (Not 2·(ν+r) — that is the "energy with 2η|γ|²" variant; with the
    // augmented-viscosity u-step the / r form is the consistent one,
    // verified by steady-state Bingham reduction.)
    gamma = yieldFactor * T_aux / r_alg;

    lambda += r_alg*(D - gamma);

    // Diagnostics
    Info<< "ALG: max|T| = " << gMax(magT.field())
        << "  yielded cells = "
        << returnReduce
           (
               static_cast<label>(sum(pos(yieldFactor.field() - 1e-12))),
               sumOp<label>()
           )
        << " / " << returnReduce(mesh.nCells(), sumOp<label>())
        << endl;
}
