"""Application Configuration for Kasejyan App.

This module defines the AppConfig class that registers this Django app
with the project. It controls how Django discovers, initializes, and
references the application throughout the project lifecycle.

The configuration handles critical app metadata:
    - Python import path for the app (name attribute)
    - Human-readable display name (verbose_name)
    - Default primary key field type
    - App initialization logic (ready() method)

Attributes:
    default_auto_field: Default primary key type for models
    name: Python import path (auto-configured for your structure)
    verbose_name: Human-readable app name for admin display

Note:
    - The 'name' attribute is automatically set to 'djansin.kasejyan'
    - Override ready() method for signal registration
    - Keep configuration minimal unless app initialization is needed
"""

from django.apps import AppConfig


class KasejyanConfig(AppConfig):
    """Django AppConfig for Kasejyan application.

    This class configures how Django interacts with this app, including
    its Python path, display name, and initialization behavior.

    Attributes:
        default_auto_field: Model primary key field type (BigAutoField)
        name: Python import path (e.g., 'djansin.kasejyan')
        verbose_name: Display name in admin interface
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "djansin.kasejyan"
    verbose_name = "Kasejyan Application"
