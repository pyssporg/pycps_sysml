package Plant {
  private import PysspCore::*;

  port def Signal {
    attribute value : Real;
  }

  part def Ball :> FmuModel {
    attribute mass : Real;
    out port y : Signal;
  }

  part def Local {
    attribute gain : Real;
  }

  part def System :> SspModel {
    out port y : Signal;
    part ball : Ball;
    part local : Local;
  }
}
