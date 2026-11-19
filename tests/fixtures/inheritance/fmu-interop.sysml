package FmuInteropInheritance {
  attribute def FmuInteropMetadata {
    attribute network_port : Integer = 5002;
  }

  part def FmuModel { }

  part def FmuInterop :> FmuModel {
    attribute interop_metadata : FmuInteropMetadata;
  }

  port def Command {
    attribute setpoint : Real;
    attribute mode : Integer;
  }

  port def Feedback {
    attribute position : Real;
  }

  part def ActuatorLink :> FmuInterop {
    in port command : Command;
    out port feedback : Feedback;
  }
}
