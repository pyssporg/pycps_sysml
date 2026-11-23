package ExperimentBaseline {
  private import PysspCore::*;

  attribute def Baseline :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  part def baseline :> Analysis {
    attribute experiment_baseline : Baseline;
  }
}
