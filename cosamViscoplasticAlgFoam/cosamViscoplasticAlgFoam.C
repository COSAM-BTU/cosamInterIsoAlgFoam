/*---------------------------------------------------------------------------*\
  Augmented-Lagrangian Bingham solver (single phase, incompressible, laminar).
  Forked from pimpleFoam. Time-split Uzawa update after pEqn loop.

  Refs:
    Vinay, Wachs, Agassant (2005) JNNFM 128, 53-65.
    Saramito & Roquet (2001) Numer. Math. 89, 367-390.
\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "pimpleControl.H"
#include "fvOptions.H"

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "Augmented-Lagrangian Bingham solver"
        " (single-phase, incompressible, laminar)."
    );

    #include "postProcess.H"
    #include "addCheckCaseOptions.H"
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createControl.H"
    #include "createFields.H"
    #include "initContinuityErrs.H"

    Info<< "\nStarting time loop\n" << endl;

    while (runTime.loop())
    {
        Info<< "Time = " << runTime.timeName() << nl << endl;

        while (pimple.loop())
        {
            #include "UEqn.H"

            while (pimple.correct())
            {
                #include "pEqn.H"
            }
        }

        // --- ALG (Uzawa) update: after PIMPLE convergence each timestep
        #include "algLoop.H"

        runTime.write();

        runTime.printExecutionTime(Info);
    }

    Info<< "End\n" << endl;
    return 0;
}
