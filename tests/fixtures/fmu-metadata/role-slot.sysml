package Example {
  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def XFmu :> FmuMetadata {
    attribute source = "build/fmus/X.fmu";
    attribute implementation = "CoSimulation";
  }

  part def FmuModel {
    attribute fmu_meta : FmuMetadata;
  }

  part def X :> FmuModel {
    $part_body
  }
}
