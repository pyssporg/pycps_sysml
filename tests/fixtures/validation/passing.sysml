package Validation {
  part def FmuModel;
  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }
  attribute def ComponentFmu :> FmuMetadata {
    attribute source = "build/fmus/Component.fmu";
    attribute implementation = "CoSimulation";
  }
  part def Component :> FmuModel {
    attribute fmu_meta : ComponentFmu;
  }
  part def System :> FmuModel {
    part component : Component;
  }
}
