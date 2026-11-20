package DesignSpace {
  part def SspModel;
  part def Analysis;

  part def StepSource;
  part def SineSource;
  part def SingleStage;
  part def TwoStage;

  variation part def SourceChoice {
    variant part step : StepSource;
    variant part sine : SineSource;
    variant part blocked : StepSource;
  }

  variation part def GainChoice {
    variant part single : SingleStage;
    variant part two : TwoStage;
  }

  constraint def SourceDeterminesGain {
    in chosenSource : SourceChoice;
    in chosenGain : GainChoice;

    (chosenSource == SourceChoice::sine implies
        chosenGain == GainChoice::single)
    and
    (chosenSource == SourceChoice::step implies
        chosenGain == GainChoice::two)
    and
    chosenSource != SourceChoice::blocked
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

  /* Pins the source only; the constraint derives the gain. */
  part def StepSystem :> System {
    part :>> source = SourceChoice::step;
  }

  part def SineSystem :> System {
    part :>> source = SourceChoice::sine;
  }

  /* No asserted constraint, so both gains are valid completions. */
  part def UnconstrainedSystem :> SspModel {
    part source : SourceChoice;
    part gain : GainChoice;
  }

  /* Pins the one source the family forbids: no gain completion survives. */
  part def ContradictorySystem :> System {
    part :>> source = SourceChoice::blocked;
  }

  /* Fully pinned illegal pair: derivation returns it and does not evaluate. */
  part def PinnedIllegalSystem :> System {
    part :>> source = SourceChoice::sine;
    part :>> gain = GainChoice::two;
  }

  part def step_derived :> Analysis {
    part sut : StepSystem;
  }

  part def sine_derived :> Analysis {
    part sut : SineSystem;
  }

  part def unconstrained :> Analysis {
    part sut : UnconstrainedSystem;
  }

  part def contradictory :> Analysis {
    part sut : ContradictorySystem;
  }

  part def pinned_illegal :> Analysis {
    part sut : PinnedIllegalSystem;
  }
}
