"""Provides the Django application configuration for the django_ contrib module.

This module defines the AppConfig class for the django_ application,
configuring the default auto field and application metadata.
"""

from django.apps import AppConfig


class Django_Config(AppConfig):
    """Application configuration for the django_ contrib module.

    This class configures the django_ application within the Django project,
    setting the default auto field type for models and providing human-readable
    naming for the application in the admin interface and other areas.

    Attributes:
        default_auto_field: The default auto field type to use for models
            without an explicitly defined primary key.
        name: The Python path to the application module.
        verbose_name: A human-readable name for the application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "contrib.django_"
    verbose_name = "Django_ Application"
