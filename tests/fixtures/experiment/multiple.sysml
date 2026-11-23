package MultipleExperiments {
  private import PysspCore::*;

  attribute def One :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  attribute def Two :> DefaultExperiment {
    attribute startTime = 1.0;
    attribute stopTime = 2.0;
  }

  part def Plant :> SspModel {
    attribute one : One;
    attribute two : Two;
  }
}
