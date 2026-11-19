package MultipleExperiments {
  attribute def DefaultExperiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }
  attribute def Experiment :> DefaultExperiment;

  attribute def One :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  attribute def Two :> DefaultExperiment {
    attribute startTime = 1.0;
    attribute stopTime = 2.0;
  }

  part def SspModel;

  part def Plant :> SspModel {
    attribute one : One;
    attribute two : Two;
  }
}
