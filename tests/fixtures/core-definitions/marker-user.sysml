package MarkerUser {
  private import ScalarValues::*;
  private import PysspCore::*;

  // Inherits the ssp_meta slot from SspModel; authors no metadata.
  part def System :> SspModel;

  // Authors a concrete SspMetadata subtype in the inherited slot name.
  part def LegacySystem :> SspModel {
    attribute ssp_meta : LegacySsp;
  }

  // Authors a concrete FmuMetadata subtype in the inherited slot name.
  part def Ball :> FmuModel {
    attribute fmu_meta : BallFmu;
  }

  // Inherits the fmu_meta slot from FmuModel; authors no metadata.
  part def UnconfiguredBall :> FmuModel;

  part def SystemAnalysis :> Analysis;

  port def BallParameters :> ParameterInterface {
    attribute g : Real;
  }

  attribute def LegacySsp :> SspMetadata {
    attribute source = "models/ssp/legacy";
  }

  attribute def BallFmu :> FmuMetadata {
    attribute source = "models/fmu/Ball/fmu";
    attribute implementation = "CoSimulation";
  }
}
