package Validation {
  private import PysspCore::*;

  attribute def NotFmu {
    attribute source : String;
  }
  part def Component :> FmuModel {
    attribute fmu_meta : NotFmu;
  }
}
