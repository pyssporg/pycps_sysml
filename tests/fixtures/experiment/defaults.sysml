package ExperimentDefaults {
  attribute def DefaultExperiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }
  attribute def Experiment :> DefaultExperiment;

  attribute def OnlyDefaults :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 2.0;
  }

  attribute def MissingStep :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 2.0;
  }

  part def SspModel;

  part def Plant :> SspModel {
    attribute defaults : OnlyDefaults;
  }

  part def Analysis;

  part def baseline :> Analysis {
    attribute defaults : OnlyDefaults;
  }

  part def missing :> Analysis {
    attribute defaults : MissingStep;
  }
}
