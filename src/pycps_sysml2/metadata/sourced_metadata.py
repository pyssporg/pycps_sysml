"""The build-metadata family base shared by every typed-metadata container.

``core.sysml`` declares::

    attribute def SourcedMetadata {
      attribute source : String;
    }

A family container extends it, so ``FmuMetadata`` and ``SspMetadata`` carry a
``source`` by inheritance, and a family that is neither an FMI nor an SSP
artifact can declare its own container the same way::

    attribute def InteropMetadata :> SourcedMetadata {
      attribute serialization : String;
      attribute version : String;
    }

    part def FmuInterop :> FmuModel {
      attribute interop_meta : InteropMetadata;
    }

Recognizing ``SourcedMetadata`` is the generic build-metadata test. It says an
attribute is a typed metadata container, not a runtime signal, a flat
parameter, or a wire field. It never says which slot records the values: the
FMU and SSP dialects have reserved slots, a family container has none. Callers
therefore check ``FmuMetadata`` and ``SspMetadata`` first, because both reach
this base too.
"""

from __future__ import annotations

from pycps_sysml2.metadata.helpers import specializes_marker_deep
from pycps_sysml2.model import Architecture, AttributeDefinition

SOURCED_METADATA_MARKER = "SourcedMetadata"


def is_sourced_metadata_definition(
    architecture: Architecture, definition: AttributeDefinition | None
) -> bool:
    """True when ``definition`` is ``SourcedMetadata`` or specializes it."""
    return specializes_marker_deep(
        architecture, definition, SOURCED_METADATA_MARKER
    )
