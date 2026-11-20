package ValidationReport {
  private import PysspCore::*;

  attribute def PumpFmu :> FmuMetadata {
    attribute source = "build/fmus/Pump.fmu";
    attribute implementation = "CoSimulation";
  }

  part def Pump :> FmuModel {
    attribute fmu_meta : PumpFmu;
  }

  part def System :> SspModel {
    part pump : Pump;
  }
}
