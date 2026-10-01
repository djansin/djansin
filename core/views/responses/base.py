"""Provide a project-local DRF ``Response`` subclass.

Re-exports DRF's ``Response`` under the project's own module path so
call sites import from a single, stable location and can be retargeted
to a custom subclass without touching every view.
"""

from rest_framework.response import Response as DrfResponse


class Response(DrfResponse):
    """Project-local subclass of DRF's ``Response``.

    Currently a pass-through with no behavioral changes. Exists as a
    single import target for the project's responses, allowing shared
    behavior to be added later without updating call sites.
    """
