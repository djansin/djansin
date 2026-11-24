"""Application configuration for the ``kasejyan`` app.

Registers the app under the short label ``kasejyan`` and sets the
default primary-key type to ``BigAutoField`` (matching the models).
"""

from django.apps import AppConfig


class KasejyanConfig(AppConfig):
    """Configuration for the ``kasejyan`` application.

    The short ``label`` (``"kasejyan"``) is used in migrations and in
    ``apps.get_model("kasejyan", ...)`` lookups, keeping model
    references stable regardless of the package path.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "djansin.kasejyan"
    label = "kasejyan"
    verbose_name = "Kasejyan Application"

    def ready(self) -> None:
        """Perform application initialization.

        Signal handlers (if any) should be imported here so they are
        registered once the app registry is fully populated. Currently
        no signals are registered by this app; the method is kept as
        an explicit extension point for future needs (e.g. auto-blocking
        a contact after repeated failed attempts).
        """
        # Import signal handlers here if/when needed:
        # from djansin.kasejyan import signals  # noqa: F401
        ...
