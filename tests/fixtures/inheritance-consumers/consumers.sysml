package InheritanceConsumers {
  part def Analysis;
  part def SspModel;
  part def FmuModel;

  attribute def DefaultExperiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }
  attribute def Experiment :> DefaultExperiment;

  attribute def Baseline :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 2.0;
    attribute stepSize = 0.01;
  }

  attribute def SspMetadata {
    attribute source : String;
  }
  attribute def LegacySsp :> SspMetadata {
    attribute source = "models/ssp/inherited";
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }
  attribute def InheritedFmu :> FmuMetadata {
    attribute source = "build/fmus/Inherited.fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def ParameterSet;
  attribute def NominalSet :> ParameterSet {
    attribute n_waypoints = 10;
  }

  port def ParameterInterface;
  port def MarkerBase :> ParameterInterface;
  port def MarkerDerived :> MarkerBase;
  port def BaseParameters :> ParameterInterface {
    attribute base_member : Real;
  }
  port def DerivedParameters :> BaseParameters, ParameterInterface {
    attribute derived_member : Integer;
  }

  part def ExperimentBase :> Analysis {
    attribute experiment_baseline : Baseline;
  }
  part def DerivedAnalysis :> ExperimentBase { }

  part def SspBase :> SspModel {
    attribute ssp_meta : LegacySsp;
  }
  part def DerivedSsp :> SspBase { }

  part def FmuBase :> FmuModel {
    attribute fmu_meta : InheritedFmu;
  }
  part def DerivedFmuPart :> FmuBase { }

  part def PortOwner {
    in port parameters : DerivedParameters;
  }
  part def ParameterPortBase {
    in port parameters : DerivedParameters;
  }
  part def InheritedPortOwner :> ParameterPortBase { }

  part def LeafPart { }
  part def CompositionBase {
    part inherited_child : LeafPart;
  }
  part def DerivedComposition :> CompositionBase { }

  attribute def InheritedSet :> ParameterSet {
    attribute base_member = 1.0;
    attribute derived_member = 2;
  }
  part def MappingComponent {
    in port parameters : DerivedParameters;
  }
  part def MappingOwner {
    attribute inherited : InheritedSet;
    part component : MappingComponent;
    bind component.parameters = inherited;
  }

  part def SetOwner :> SspModel {
    attribute nominal : NominalSet;
  }
  part def DerivedSetOwner :> SetOwner { }

  part def NestedFmuBase :> FmuModel {
    attribute fmu_meta : InheritedFmu;
    part nested_child : LeafPart;
  }
  part def DerivedNestedFmu :> NestedFmuBase { }

  part def ModelUsageModel :> SspModel { }
  part def ModelUsageBase :> Analysis {
    part sut : ModelUsageModel;
  }
  part def DerivedModelUsageAnalysis :> ModelUsageBase { }

  part def VariationModel :> SspModel {
    variation part source : LeafPart;
  }
  part def VariationBase :> Analysis {
    part sut : VariationModel;
  }
  part def DerivedVariationAnalysis :> VariationBase { }

  port def SignalPort {
    attribute value : Real;
  }
  part def SignalSource {
    out port y : SignalPort;
  }
  port def ComponentParameters :> ParameterInterface {
    attribute p : Real;
  }
  part def ComponentParametersBase {
    in port parameters : ComponentParameters;
  }
  part def InheritedParametersComponent :> ComponentParametersBase { }

  variation part def InheritedPortChoice {
    variant part directPath {
      part source : SignalSource;
      part sink : InheritedParametersComponent;
      connect source.y to sink.parameters;
    }
  }
  part def InheritedPortSystem :> SspModel {
    part path : InheritedPortChoice;
  }
}
