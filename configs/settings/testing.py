"""Testing Environment Settings.

Environment: testing
Inherits: .base
Overrides: Base settings as needed for 'testing' operations

Key Responsibilities:
    1. Environment-specific configuration overrides
    2. Security settings appropriate for 'testing'
    3. Service endpoints and credentials for 'testing'

Configuration Method:
    - Set DJANGO_SETTINGS_MODULE="configs.settings.testing"
    - Use environment variables for sensitive data
    - Extend/override only what's necessary from base settings

Note: This file is auto-generated. Manual edits may be overwritten.
"""

from .base import *  # pylint: disable=unused-wildcard-import, wildcard-import  # noqa

# Testing specific settings
# Add your testing-only settings below
