package Plant {
  private import PysspCore::*;

  port def ControllerParams :> ParameterInterface {
    attribute kp : Real;
    attribute ki : Real;
    attribute enable : Boolean;
  }

  attribute def NominalGains :> ParameterSet {
    attribute kp_value = 1.5;
  }

  part def Controller {
    in port parameters : ControllerParams;
  }

  part def System :> SspModel {
    part controller : Controller;
    attribute nominal : NominalGains;
    bind controller.parameters.kp = nominal.kp_value;
  }
}
