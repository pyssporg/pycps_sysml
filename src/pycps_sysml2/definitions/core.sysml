package PysspCore {
  part def SspModel;
  part def Analysis;
  part def FmuModel;

  port def ParameterInterface;

  attribute def ParameterSet;

  // Shared base for containers that name an external artifact.
  attribute def SourcedMetadata {
    attribute source : String;
  }

  attribute def FmuMetadata :> SourcedMetadata {
    attribute implementation : String;
  }

  attribute def SspMetadata :> SourcedMetadata;

  attribute def DefaultExperiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
    attribute tolerance : Real;
  }

  attribute def Experiment :> DefaultExperiment;
}
