package InheritanceEdges {
  port def Signal {
    attribute value : Real;
  }

  constraint def Always {
    true
  }

  part def Leaf {
    out port emit : Signal;
  }

  part def Base {
    attribute root : Integer;
    out port boundary : Signal;
    part child : Leaf;
    connect child.emit to boundary;
    bind child.emit.value = boundary.value;
    constraint inheritedRule : Always { }
  }

  part def Derived :> Base {
    attribute own : Integer;
    part extra : Leaf;
    constraint ownRule : Always { }
  }

  part def Left :> Base {
    attribute left : Integer;
  }

  part def Right :> Base {
    attribute right : Integer;
  }

  part def Diamond :> Left, Right {
    attribute bottom : Integer;
  }

  part def OverrideChild :> Base {
    attribute root : Real;
  }

  part def ValueBase {
    attribute sample : Integer = 7;
  }

  part def ValueChild :> ValueBase {
    attribute sample : Integer[2];
  }

  part def SubsettingChild :> ValueBase {
    attribute narrowed :> ValueBase::sample;
  }

  part def Orphan :> Missing {
    attribute own : Integer;
  }

  part def CycleA :> CycleB {
    attribute a : Integer;
  }

  part def CycleB :> CycleA {
    attribute b : Integer;
  }

  port def BasePort {
    attribute base_member : Real;
  }

  port def DerivedPort :> BasePort {
    attribute derived_member : Integer;
  }

  attribute def BaseAttr {
    attribute base_member : Integer;
  }

  attribute def DerivedAttr :> BaseAttr {
    attribute derived_member : Real;
  }

  part def RedefinitionBase {
    out port y : Signal;
  }

  part def RedefinitionChild :> RedefinitionBase {
    out port :>> y : Signal;
  }
}
