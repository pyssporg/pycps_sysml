package Precedence {
  private import PysspCore::*;

  attribute def CompFmu :> FmuMetadata {
    attribute source = "build/fmus/Comp.fmu";
  }
  attribute def CompSsp :> SspMetadata;
  attribute def Notes {
    attribute text : String;
  }
  part def Holder {
    attribute fmu_meta : CompFmu;
    attribute ssp_meta : CompSsp;
    attribute note : Notes;
  }
}
