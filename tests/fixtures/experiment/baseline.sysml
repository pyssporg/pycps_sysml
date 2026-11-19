package ExperimentBaseline {
  attribute def DefaultExperiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }
  attribute def Experiment :> DefaultExperiment;

  attribute def Baseline :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  part def Analysis;

  part def baseline :> Analysis {
    attribute experiment_baseline : Baseline;
  }
}
