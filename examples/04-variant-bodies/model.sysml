// The forms a variant can take: typed, a body, and a usage-level point.
package Plant {
  private import PysspCore::*;

  port def Signal {
    attribute value : Real;
  }

  part def Gain {
    in port u : Signal;
    out port y : Signal;
    attribute gain : Real = 2.0;
  }

  part def Attenuate {
    in port u : Signal;
    out port y : Signal;
    attribute factor : Real = 0.5;
  }

  part def StageBase {
    in port u : Signal;
    out port y : Signal;
  }

  part def Step {
    in port u : Signal;
    out port y : Signal;
  }

  part def SignalSource {
    out port y : Signal;
  }

  // A typed variant names a definition; a body variant carries its own members.
  variation part def PathChoice {
    in port u : Signal;
    out port y : Signal;

    variant part directPath : Gain;

    variant part nestedPath {
      part gain : Gain;

      // A nested point takes a dotted selection key: path.stage.
      variation part stage : StageBase {
        variant part attenuateStage : Attenuate;
      }

      connect u to gain.u;
      connect gain.y to stage.u;
      connect stage.y to y;
    }
  }

  part def System :> SspModel {
    part path : PathChoice;

    // This point sits on a part usage, not on a definition.
    variation part source : SignalSource {
      variant part stepSource : Step;
    }
  }
}
