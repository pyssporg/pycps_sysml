// Two variation points and a cross-point constraint: only two pairs survive.
package Plant {
  private import PysspCore::*;

  part def StepSource;
  part def SineSource;
  part def SingleStage;
  part def TwoStage;

  variation part def SourceChoice {
    variant part step : StepSource;
    variant part sine : SineSource;
  }

  variation part def GainChoice {
    variant part single : SingleStage;
    variant part two : TwoStage;
  }

  // Typed parameters document the intent; each usage binds them by name.
  constraint def SourceDeterminesGain {
    in chosenSource : SourceChoice;
    in chosenGain : GainChoice;

    (chosenSource == SourceChoice::sine implies
        chosenGain == GainChoice::single)
    and
    (chosenSource == SourceChoice::step implies
        chosenGain == GainChoice::two)
  }

  part def System :> SspModel {
    part source : SourceChoice;
    part gain : GainChoice;

    constraint sourceDeterminesGain : SourceDeterminesGain {
      in chosenSource = source;
      in chosenGain = gain;
    }

    assert sourceDeterminesGain;
  }

  // A pure selection: a derived configuration pins the points with :>>.
  part def StepTwoSystem :> System {
    part :>> source = SourceChoice::step;
    part :>> gain = GainChoice::two;
  }
}
