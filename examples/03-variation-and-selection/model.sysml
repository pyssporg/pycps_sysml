// Variation, selection, and constraint evaluation in one workflow.
package Plant {
  private import PysspCore::*;

  part def LightMass {
    attribute mass = 10.0;
  }

  part def HeavyMass {
    attribute mass = 20.0;
  }

  // The variants carry different values; the constraint selects by variant.
  variation part def MassChoice {
    variant part light : LightMass;
    variant part heavy : HeavyMass;
  }

  // Passes only for the light variant.
  constraint def LightOnly {
    chosen == MassChoice::light
  }

  // System binds the constraint to its variation point usage.
  part def System :> SspModel {
    part mass : MassChoice;

    constraint massIsLight : LightOnly {
      in chosen = mass;
    }

    // Assert makes the usage enforceable; without it the status is unasserted.
    assert massIsLight;
  }
}
