// Augmented-Lagrangian momentum equation.
//   ddt(U) + div(phi U) - div((nu + r/2) grad U) = div(lambda - r γ) + f
// where the augmented viscosity (ν + r/2) carries an extra ALG diffusion that
// is exactly compensated by the explicit ∇·(λ - r γ) source at convergence.

dimensionedScalar nu_eff("nu_eff", nu + 0.5*r_alg);

tmp<volVectorField> algSource = fvc::div(lambda - r_alg*gamma);

tmp<fvVectorMatrix> tUEqn
(
    fvm::ddt(U) + fvm::div(phi, U)
  - fvm::laplacian(nu_eff, U)
 ==
    algSource
  + fvOptions(U)
);
fvVectorMatrix& UEqn = tUEqn.ref();

UEqn.relax();
fvOptions.constrain(UEqn);

if (pimple.momentumPredictor())
{
    solve(UEqn == -fvc::grad(p));
    fvOptions.correct(U);
}
