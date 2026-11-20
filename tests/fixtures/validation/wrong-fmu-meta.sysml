package Validation {
  attribute def NotFmu {
    attribute source : String;
  }
  part def FmuModel;
  part def Component :> FmuModel {
    attribute fmu_meta : NotFmu;
  }
}
