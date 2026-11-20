// A 100% configuration binds variation points with :>>; analyses compose it.
package Plant {
  private import PysspCore::*;

  part def Step;
  part def Sine;

  variation part def SourceChoice {
    variant part step : Step;
    variant part sine : Sine;
  }

  attribute def EarlyScenario;
  attribute def LateScenario;

  variation attribute def ScenarioChoice {
    variant attribute early : EarlyScenario;
    variant attribute late : LateScenario;
  }

  // The root composition owns both variation points, unbound.
  part def System :> SspModel {
    part source : SourceChoice;
    attribute scenario : ScenarioChoice;
  }

  // A configuration binds both points structurally, not at call time.
  part def SineLate :> System {
    part :>> source = SourceChoice::sine;
    attribute :>> scenario = ScenarioChoice::late;
  }

  // This configuration binds only the part point, leaving the attribute point open.
  part def Unbound :> System {
    part :>> source = SourceChoice::step;
  }

  // Analyses compose a configuration through their sut usage.
  part def sine_late :> Analysis {
    part sut : SineLate;
  }

  part def unbound_plan :> Analysis {
    part sut : Unbound;
  }
}
