package Validation {
  attribute def FmuMetadata {
    attribute source : String;
  }
  attribute def ComponentFmu :> FmuMetadata {
    attribute source = "build/fmus/Component.fmu";
  }
  part def FmuModel;
  part def Component :> FmuModel {
    attribute fmu_meta : ComponentFmu;
    attribute pyssp_implementation = "CoSimulation";
  }
}
