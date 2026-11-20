package Validation {
  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }
  attribute def ComponentFmu :> FmuMetadata {
    attribute source = "build/fmus/Component.fmu";
    attribute implementation = "ModelExchange";
  }
  part def FmuModel;
  part def Component :> FmuModel {
    attribute fmu_meta : ComponentFmu;
  }
}
