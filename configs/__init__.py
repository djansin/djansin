"""Package initializer for the ``configs`` project.

Exposes the Celery application so that:

* ``@shared_task`` decorators in ``djansin.*``, ``apps.*``, ``contrib.*``
  and any future package apps resolve against the same app instance that
  the worker boots with. Without this re-export, ``shared_task`` would
  fall back to Celery's default app, which has no Django settings loaded
  and therefore no broker URL — tasks would silently be registered
  against the wrong app.
* ``celery -A configs worker`` can locate ``configs.celery.app`` without
  importing every task module explicitly. The ``-A`` flag accepts a
  module path and looks for an ``app`` attribute; this re-export is what
  makes that attribute resolvable at the package level.
* ``autodiscover_tasks()`` in :mod:`configs.celery` can register tasks
  from all ``INSTALLED_APPS`` once Django's app registry is ready. Task
  discovery is deferred until Django is fully configured, so importing
  this module must not trigger it early.

This module is imported **before** Django settings are loaded, so it must
remain importable without side effects beyond importing the Celery app.
Do not add Django model imports, signal registration, or any other
startup logic here — those belong in the app configs' ``ready()``
methods, which run after the app registry is populated.
"""

from .celery import app as celery_app


__all__ = ("celery_app",)
