package NestedFmuModel {
  private import PysspCore::*;

  attribute def LeafFmu :> FmuMetadata {
    attribute source = "build/fmus/Leaf.fmu";
  }
  part def Leaf :> FmuModel {
    attribute fmu_meta : LeafFmu;
  }
  part def Subsystem :> FmuModel {
    part leaf : Leaf;
  }
  part def System :> SspModel {
    part subsystem : Subsystem;
  }
}
