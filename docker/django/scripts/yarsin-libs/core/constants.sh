#!/usr/bin/env bash

# =============================================================================
# YARSIN - Django Project Management Tool
# =============================================================================
# Description: Yarsin is a comprehensive command-line tool for managing Django
#              projects with advanced features like multi-environment settings,
#              health checks, and container orchestration support.
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
#                     subcommand is provided. Defaults to django-admin for
#                     backward compatibility with standard Django workflows.
# -----------------------------------------------------------------------------
: "${DEFAULT_SUBCOMMAND:=django-admin}"


# -----------------------------------------------------------------------------
# Directory Structure Configuration
# -----------------------------------------------------------------------------
# These paths define the project's directory layout. All paths are relative
# to WORK_DIRECTORY unless specified otherwise.
# -----------------------------------------------------------------------------

# WORK_DIRECTORY: The root directory of the Django project inside the container.
#                 This is where the project and all its components live.
: "${WORK_DIRECTORY:=/app}"

# PROJECT_NAME: The name used to create and identify the directory for Django
#               configuration files. Typically contains settings, URLs, and
#               WSGI/ASGI configuration.
: "${PROJECT_NAME:=configs}"

# APP_DIRECTORY: The directory subpath that contains the project's custom apps.
#                Standard location for reusable Django applications.
: "${APP_DIRECTORY:=apps}"

# PACK_DIRECTORY: The directory subpath that contains custom packages.
#                 For reusable code that isn't Django-specific or for
#                 third-party package management.
: "${PACK_DIRECTORY:=djansin}"

# EXTRAS_DIRECTORY: The directory subpath that contains the project's auxiliary apps.
#                   Used for auxiliary django apps that doesn't fit in
#                   standard apps (e.g., management commands, add-ons, utilities).
: "${EXTRAS_DIRECTORY:=extras}"

# STATIC_ROOT: The root directory for static files collected via collectstatic.
#              Used in production to serve static assets efficiently.
: "${STATIC_ROOT:=/assets/static}"

# MEDIA_ROOT: The root directory for user-uploaded media files.
#             Should be persisted and backed up appropriately.
: "${MEDIA_ROOT:=/assets/media}"


# -----------------------------------------------------------------------------
# Documentation Configuration
# -----------------------------------------------------------------------------
# These paths define where Sphinx documentation source and output are located.
# Used by the sphinx-build command for generating project documentation.
# -----------------------------------------------------------------------------

# DOC_SOURCE: Source directory containing reStructuredText/markdown files
#             for Sphinx documentation. Defaults to ${WORK_DIRECTORY}/docs/source.
: "${DOC_SOURCE:=${WORK_DIRECTORY:-$(pwd)}/docs/source}"

# DOC_OUTPUT: Output directory for built HTML documentation.
#             This is where the generated documentation is written.
: "${DOC_OUTPUT:=${WORK_DIRECTORY:-$(pwd)}/docs/build/html}"

# DOC_BUILDER: Default builder type for Sphinx documentation.
#              Common values: html, dirhtml, singlehtml, latex, epub, json.
: "${DOC_BUILDER:=html}"


# -----------------------------------------------------------------------------
# Server Configuration
# -----------------------------------------------------------------------------
# SERVER_PORT: The port on which the Django development server runs.
#              Used by runserver and healthcheck commands.
# -----------------------------------------------------------------------------

# SERVER_PORT: Development server port (default: 8000 for Django)
: "${SERVER_PORT:=8000}"

# DEV_SERVER_HOST: Development server host (0.0.0.0 allows external access)
: "${SERVER_HOST:=0.0.0.0}"


# -----------------------------------------------------------------------------
# User Configuration
# -----------------------------------------------------------------------------
# USERNAME: The username used when creating a new user inside the container.
#           Used by run-as command for privilege escalation.
# -----------------------------------------------------------------------------
: "${USERNAME:=djansin}"


# -----------------------------------------------------------------------------
# Package Mirror Configuration
# -----------------------------------------------------------------------------
# These mirrors improve download speeds and reliability in different regions.
# Override with environment variables for your specific needs.
# -----------------------------------------------------------------------------

# PYPI_MIRROR: PyPI package index URL for pip installations.
#             Used in Docker builds and pip scripts.
: "${PYPI_MIRROR:=https://pypi.org/simple/}"

# APT_MIRROR: APT package mirror URL for system package installations.
#             Used in Docker builds and system setup scripts.
: "${APT_MIRROR:=http://deb.debian.org/debian}"


# -----------------------------------------------------------------------------
# isort Configuration
# -----------------------------------------------------------------------------
# These variables define default behavior for isort.
# They can be overridden by environment variables.
# -----------------------------------------------------------------------------

# ISORT_OPTIONS: Default options to pass to isort
# --skip envs: Skip environment/virtual environment directories
# --skip migrations: Skip Django migration files (auto-generated code)
: "${ISORT_OPTIONS:=--skip envs --skip migrations}"

# ISORT_TARGET: Default target to sort when no arguments provided
# Defaults to WORK_DIRECTORY or current directory
: "${ISORT_TARGET:=${WORK_DIRECTORY:-$(pwd)}}"

# ISORT_PROFILE: Default import profile (black, django, google, etc.)
: "${ISORT_PROFILE:=black}"


# -----------------------------------------------------------------------------
# Flake8 Configuration
# -----------------------------------------------------------------------------
# These variables define default behavior for Flake8.
# They can be overridden by environment variables.
# -----------------------------------------------------------------------------

# FLAKE8_OPTIONS: Default options to pass to Flake8
# --count: Show total error count
# --statistics: Show statistics about each error type
: "${FLAKE8_OPTIONS:=--count --statistics}"

# FLAKE8_TARGET: Default target to lint when no arguments provided
# Defaults to WORK_DIRECTORY or current directory
: "${FLAKE8_TARGET:=${WORK_DIRECTORY:-$(pwd)}}"

# FLAKE8_CONFIG: Path to Flake8 configuration file
# If not set, Flake8 will search for .flake8, tox.ini, or setup.cfg
: "${FLAKE8_CONFIG:=}"

# FLAKE8_EXCLUDE: Patterns to exclude from linting
# Default: .git,__pycache__,migrations,env,venv,.venv
: "${FLAKE8_EXCLUDE:=.git,__pycache__,migrations,env,venv,.venv}"
