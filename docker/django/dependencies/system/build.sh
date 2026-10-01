#!/usr/bin/env bash

# =============================================================================
# Docker Build Script - Install System Dependencies for Python Packages
# =============================================================================
# Description: Installs system-level build dependencies required to compile
#              Python packages with native extensions (e.g., psycopg, Pillow,
#              lxml) on Debian-based Docker images.
#
# Target base image: python:3.xx-slim-bookworm
#
# Author: Mohammad Ali Amini
# Date: 2026
# =============================================================================


# =============================================================================
# STRICT MODE CONFIGURATION
# =============================================================================
# Enforces strict error handling to prevent silent failures.
#   - set -e:  Exit immediately if any command fails
#   - set -u:  Treat unset variables as errors
# -----------------------------------------------------------------------------
set -e
set -u


# =============================================================================
# SYSTEM PACKAGE INSTALLATION
# =============================================================================

# -----------------------------------------------------------------------------
# Update APT Package Index
# -----------------------------------------------------------------------------
# Description:
#   Updates the APT package index to ensure access to the latest security
#   fixes and available package metadata. This is necessary before installing
#   any packages to ensure we get the latest versions.
# -----------------------------------------------------------------------------
apt-get update

# -----------------------------------------------------------------------------
# Install Core Build Dependencies
# -----------------------------------------------------------------------------
# Description:
#   Installs essential build tools and development libraries required for
#   compiling Python packages with native extensions.
#
# Packages installed:
#   - build-essential: Standard C/C++ toolchain (gcc, make, libc headers)
#     Required to compile Python packages with native extensions.
#
#   - libpq-dev: PostgreSQL client development headers and libraries
#     Needed to build psycopg/psycopg2 from source for PostgreSQL support.
#
#   - ca-certificates: System CA bundle enabling secure TLS/HTTPS
#     connections for package downloads and API calls.
#
# Note: --no-install-recommends avoids pulling in unnecessary suggested
#       packages, reducing final Docker image size.
# -----------------------------------------------------------------------------
apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    ca-certificates


# =============================================================================
# CLEANUP
# =============================================================================

# -----------------------------------------------------------------------------
# Clean APT Cache
# -----------------------------------------------------------------------------
# Description:
#   Removes cached APT package lists to reduce final Docker image size.
#   Since packages are already installed, the cached lists are no longer needed
#   and would only waste space in the final image layer.
# -----------------------------------------------------------------------------
rm -rf /var/lib/apt/lists/*


# =============================================================================
# PIP UPGRADE
# =============================================================================

# -----------------------------------------------------------------------------
# Upgrade Pip
# -----------------------------------------------------------------------------
# Description:
#   Upgrades pip to the latest stable version for improved security,
#   better dependency resolution, and enhanced wheel compatibility.
#   This ensures that subsequent pip install commands use the latest
#   features and security patches.
# -----------------------------------------------------------------------------
pip install --upgrade pip
