"""Tests for the ``wait_for_db`` management command.

These tests verify that the command correctly polls the default database
connection until it becomes available, and that it retries with the
expected back-off behaviour when the database is temporarily unreachable.
"""

import pytest
from django.core.management import call_command
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


CHECK_PATH = "contrib.django_.management.commands.wait_for_db.Command.check"


@pytest.mark.django_db
class TestWaitForDbCommand:
    """Test suite for the ``wait_for_db`` management command."""

    def test_wait_for_db_ready(self, mocker):
        """Command exits immediately when the database is already available.

        Verifies that a single successful ``check`` call is performed
        against the default database and that no retries occur.

        Args:
            mocker: Pytest-mock fixture used to patch the command's
                ``check`` method.
        """
        patched_check = mocker.patch(CHECK_PATH)
        patched_check.return_value = True

        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])

    def test_wait_for_db_delay(self, mocker):
        """Command retries until the database becomes available after delays.

        Simulates two psycopg2 errors, three Django operational errors, and
        a final success. Verifies that the command retries six times in
        total and sleeps between each failed attempt.

        Args:
            mocker: Pytest-mock fixture used to patch both the command's
                ``check`` method and ``time.sleep``.
        """
        patched_check = mocker.patch(CHECK_PATH)
        patched_sleep = mocker.patch("time.sleep")

        patched_check.side_effect = (
            [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        assert patched_check.call_count == 6
        patched_check.assert_called_with(databases=["default"])
        assert patched_sleep.call_count == 5
