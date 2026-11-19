package ExperimentTolerance {
  attribute def DefaultExperiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
    attribute tolerance : Real;
  }
  attribute def Experiment :> DefaultExperiment;

  attribute def Tuned :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
    attribute tolerance = 1e-6;
  }

  attribute def Unset :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  attribute def NonPositive :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
    attribute tolerance = 0.0;
  }

  part def tuned {
    attribute experiment : Tuned;
  }

  part def unset {
    attribute experiment : Unset;
  }

  part def invalid {
    attribute experiment : NonPositive;
  }
}
