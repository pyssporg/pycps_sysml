    package Example {
      private import PysspCore::*;

      port def AutopilotParameters $interface_marker {
        $interface_members
      }

      $sets

      part def AutopilotModule {
        in port parameters : AutopilotParameters;
      }

      part def $COMPOSITION_NAME {
        part autopilot : AutopilotModule;
        $composition
      }
    }
