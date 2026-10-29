"""Django management command that blocks execution until the default database is ready.

This command is intended to be used as a startup gate (e.g., in a Docker
entrypoint or CI pipeline) to ensure the database accepts connections
before the application attempts to use it. It repeatedly probes the
default database connection and exits only once the connection succeeds.
"""

import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    """Wait for the default database to become available.

    Polls the database connection once per second, indefinitely, until it
    can be established. Both Django's and psycopg2's ``OperationalError``
    are treated as "database not ready" signals and are swallowed, so the
    command only terminates when the connection succeeds.

    Attributes:
        RETRY_DELAY: Seconds to wait between consecutive connection attempts.
    """

    RETRY_DELAY = 1

    def handle(self, *args, **options):
        """Run the polling loop until the default database is reachable.

        Args:
            *args: Positional arguments forwarded by Django's command
                dispatcher. Unused.
            **options: Keyword arguments parsed from the command line.
                Unused.

        Returns:
            None. The command exits once the database connection succeeds.
        """
        self.stdout.write("Waiting for database...")
        db_up = False

        while not db_up:
            try:
                self.check(databases=["default"])
                db_up = True
            except (OperationalError, Psycopg2Error):
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(self.RETRY_DELAY)

        self.stdout.write(self.style.SUCCESS("Database available!"))
