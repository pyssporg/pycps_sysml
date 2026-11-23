package InteropLink {
  private import PysspCore::*;
  private import PyfmiInterop::*;

  part def Link :> FmuInterop {
    out port telemetry : Telemetry;
  }

  port def Telemetry {
    attribute value : Real;
  }
}
