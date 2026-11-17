package Validation {
  attribute def FmuMetadata {
    attribute source : String;
  }
  attribute def ComponentFmu :> FmuMetadata {
    attribute source = "build/fmus/Component.fmu";
  }
  part def System {
    part component : Component;
  }
  part def Component {
    attribute fmu_meta : ComponentFmu;
    attribute gain : Real = 1.0;
  }
}
