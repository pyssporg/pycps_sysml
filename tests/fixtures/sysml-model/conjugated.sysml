package Conjugated {
          port def FluidState {
            in attribute pressure : Real;
            out attribute flowRate : Real;
            inout attribute st : Real;
            attribute tag : Real;
          }

          port def 'Flu-id' {
            in attribute level : Real;
          }

          part def Source {
            in port fluid : FluidState;
          }

          part def Sink {
            in port fluid : ~FluidState;
            port odd : ~'Flu-id';
          }

          part def System {
            part source : Source;
            part sink : Sink;
            connect source.fluid to sink.fluid;
          }
        }
