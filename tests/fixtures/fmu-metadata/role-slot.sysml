package Example {
  private import PysspCore::*;

  attribute def XFmu :> FmuMetadata {
    attribute source = "build/fmus/X.fmu";
    attribute implementation = "CoSimulation";
  }

  part def X :> FmuModel {
    $part_body
  }
}
