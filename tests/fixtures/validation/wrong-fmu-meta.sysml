package Validation {
  attribute def NotFmu {
    attribute source : String;
  }
  part def Component {
    attribute fmu_meta : NotFmu;
  }
}
