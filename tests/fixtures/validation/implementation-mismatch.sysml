package Validation {
  private import PysspCore::*;

  attribute def ComponentFmu :> FmuMetadata {
    attribute source = "build/fmus/Component.fmu";
    attribute implementation = "ModelExchange";
  }
  part def Component :> FmuModel {
    attribute fmu_meta : ComponentFmu;
  }
}
