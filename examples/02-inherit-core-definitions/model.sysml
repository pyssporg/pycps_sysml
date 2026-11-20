package InheritCore {
    private import PysspCore::*;

    // No ssp_meta here: the slot is inherited from SspModel and stays unfilled.
    part def System :> SspModel;

    attribute def BallFmu :> FmuMetadata {
        attribute source = "build/fmus/Ball.fmu";
        attribute implementation = "CoSimulation";
    }

    // The subclass supplies the values the core definition only declares.
    part def Ball :> FmuModel {
        attribute fmu_meta : BallFmu;
    }

    // Experiment supplies startTime/stopTime; the subclass fills three of the
    // four members, so tolerance stays inherited and unfilled.
    attribute def BallExperiment :> Experiment {
        attribute startTime = 0.0;
        attribute stopTime = 5.0;
        attribute stepSize = 0.01;
    }

    part def Simulation :> Analysis {
        attribute experiment : BallExperiment;
        part sut : System;
    }
}
