#!/usr/bin/env bash

# =============================================================================
# YARSIN - PostgreSQL Container Manager
# =============================================================================
# Description: Yarsin is a comprehensive command-line tool for managing
#              PostgreSQL databases in containerized environments with
#              advanced backup, restore, and maintenance capabilities.
#
# Author: Mohammad Ali Amini
# Date: 2026
# =============================================================================


# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================
# These variables define the default behavior of Yarsin commands.
# They can be overridden by environment variables or command-line options.
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Command Routing Configuration
# -----------------------------------------------------------------------------
# DEFAULT_SUBCOMMAND: The default command to execute when no specific
#                     subcommand is provided. Defaults to psql for interactive
#                     database access.
# -----------------------------------------------------------------------------
: "${DEFAULT_SUBCOMMAND:=psql}"


# -----------------------------------------------------------------------------
# Backup Configuration
# -----------------------------------------------------------------------------
# These variables define backup paths and naming conventions.
# They can be overridden by environment variables.
# -----------------------------------------------------------------------------

# PostgreSQL data directory (inside container)
: "${POSTGRESQL_DATA:=${PGDATA:-/var/lib/postgresql/data}}"

# Backup root directory
: "${BACKUP_ROOT:=/backups}"


# -----------------------------------------------------------------------------
# DBMS Backup Configuration (Full PostgreSQL Data Directory)
# -----------------------------------------------------------------------------
# These variables control full database cluster backups.
# -----------------------------------------------------------------------------

# DBMS backup directory and settings
: "${DBMS_BACKUP_PATH:=${BACKUP_ROOT}/full}"
: "${DBMS_BACKUP_FILE_PREFIX:=postgresql}"
: "${DBMS_BACKUP_FILE_SUFFIX:=dbms}"
: "${DBMS_BACKUP_GLOB:="*.tar.gz"}"

# DBMS backup filename pattern (for regex extraction)
# Pattern: postgresql___2024_01_15__02_30_00___dbms.tar.gz
: "${DBMS_BACKUP_PATTERN:="^([a-zA-Z0-9_]+)___[0-9_]+__[0-9_]+___${DBMS_BACKUP_FILE_SUFFIX}.sql.gz$"}"

# Source for DBMS backup (PostgreSQL data directory)
: "${DBMS_BACKUP_SOURCE:=${POSTGRESQL_DATA}}"


# -----------------------------------------------------------------------------
# Database Backup Configuration (Individual Database Dumps)
# -----------------------------------------------------------------------------
# These variables control individual database backups using pg_dump.
# -----------------------------------------------------------------------------

# Data backup directory and settings
: "${DATA_BACKUP_PATH:=${BACKUP_ROOT}/databases}"
: "${DATA_BACKUP_FILE_PREFIX:=database}"
: "${DATA_BACKUP_FILE_SUFFIX:=data}"
: "${DATA_BACKUP_GLOB:="*.sql.gz"}"

# Data backup filename pattern (for regex extraction)
# Pattern: database___2024_01_15__02_30_00___data.sql.gz
: "${DATA_BACKUP_PATTERN:="^([a-zA-Z0-9_]+)___[0-9_]+__[0-9_]+___${DATA_BACKUP_FILE_SUFFIX}.sql.gz$"}"


# -----------------------------------------------------------------------------
# User Configuration
# -----------------------------------------------------------------------------
# USERNAME: The username used when creating a new user inside the container.
#           Used by run-as command for privilege escalation.
# -----------------------------------------------------------------------------
: "${USERNAME:=djansin}"
