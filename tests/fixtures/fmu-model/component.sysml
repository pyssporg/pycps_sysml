package Fmu {
  private import PysspCore::*;

  attribute def CompFmu :> FmuMetadata {
    attribute source = "build/fmus/Comp.fmu";
  }
  part def Comp :> FmuModel {
    attribute fmu_meta : CompFmu;
  }
  part def Unmarked {
    attribute fmu_meta : CompFmu;
  }
  part def Nested :> FmuModel {
    attribute fmu_meta : CompFmu;
    part inner : Comp;
  }
}
