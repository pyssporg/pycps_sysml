package ValidationReportBroken {
  private import PysspCore::*;

  attribute def PumpFmu :> FmuMetadata {
    attribute source = "build/fmus/Pump.fmu";
    attribute implementation = "CoSimulation";
  }

  part def Pump {
    attribute fmu_meta : PumpFmu;
  }

  part def System :> SspModel {
    part pump : Pump;
  }
}
