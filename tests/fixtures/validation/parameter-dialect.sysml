package Validation {
  private import PysspCore::*;

  attribute def ComponentFmu :> FmuMetadata {
    attribute source = "build/fmus/Component.fmu";
  }
  part def Component :> FmuModel {
    attribute fmu_meta : ComponentFmu;
    attribute gain : Real = 1.0;
  }
  part def System {
    part component : Component;
  }
}
