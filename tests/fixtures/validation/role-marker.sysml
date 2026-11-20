package Validation {
  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }
  attribute def ComponentFmu :> FmuMetadata {
    attribute source = "build/fmus/Component.fmu";
    attribute implementation = "CoSimulation";
  }
  part def FmuModel;
  part def System :> SspModel {
    part component : Component;
  }
  part def Component :> FmuModel {
    attribute fmu_meta : ComponentFmu;
  }
}
