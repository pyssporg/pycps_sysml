package Validation {
  private import PysspCore::*;

  attribute def ComponentFmu :> FmuMetadata {
    attribute source = "build/fmus/Component.fmu";
  }
  part def Component :> FmuModel {
    attribute fmu_meta : ComponentFmu;
    attribute pyssp_implementation = "CoSimulation";
  }
}
