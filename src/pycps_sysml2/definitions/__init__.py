"""Compatibility facade over the installable shared SysML vocabulary.

The dialect markers are ordinary SysML definitions. They now ship with
:mod:`pyssp_sysml_definitions`, so an external application can author against
the same vocabulary without depending on this package. This module keeps the
historical import path and names working.
"""

from __future__ import annotations

from pyssp_sysml_definitions import CORE_FILE, core_definitions

__all__ = ["CORE_FILE", "core_definitions"]
