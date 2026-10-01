#!/usr/bin/env bash

# =============================================================================
# Script: System Dependencies Installer (Production)
# =============================================================================
# Description: Installs runtime dependencies required for production environment.
#              Includes database client libraries, WeasyPrint PDF rendering
#              dependencies, fonts, and internationalization support.
#
# Target: Debian-based images (python:3.14-slim-bookworm and derivatives)
# Platform: Container images (Docker)
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
# PACKAGE INSTALLATION
# =============================================================================

# -----------------------------------------------------------------------------
# Step 1: Update APT Package Index
# -----------------------------------------------------------------------------
# Description: Updates the APT package index to get latest package information.
#              This ensures we install the most recent available versions.
# -----------------------------------------------------------------------------
apt-get update

# -----------------------------------------------------------------------------
# Step 2: Database Client Libraries
# -----------------------------------------------------------------------------
# Description: Installs runtime libraries required for database connectivity.
#
# Packages:
#   - libpq5: PostgreSQL client runtime library
#     Required by psycopg2 and Django PostgreSQL database backends
#
#   - gettext: GNU gettext utilities
#     Used by Django for message extraction, compilation, and runtime
#     translation (internationalization/localization)
# -----------------------------------------------------------------------------
apt-get install -y --no-install-recommends \
    libpq5 \
    gettext

# -----------------------------------------------------------------------------
# Step 3: WeasyPrint PDF Rendering Dependencies
# -----------------------------------------------------------------------------
# Description: Installs system libraries required for WeasyPrint to render
#              HTML/CSS to PDF. These are the core native dependencies for
#              the WeasyPrint PDF generation engine.
#
# Reference: Official WeasyPrint documentation recommends installing Pango,
#            Cairo, and related libraries before pip install weasyprint.
#
# Packages:
#   - libcairo2: 2D graphics library for drawing operations
#   - libpango-1.0-0: Text layout engine for international text rendering
#   - libpangoft2-1.0-0: Pango FreeType integration for font rendering
#   - libharfbuzz0b: Text shaping engine for complex scripts (Arabic/Persian)
#   - libharfbuzz-subset0: Font subsetting support for HarfBuzz
#   - libgdk-pixbuf2.0-0: Image support for PNG, SVG, and other formats
#   - libffi-dev: Required by CFFI at build time for WeasyPrint compilation
#   - shared-mime-info: MIME type database for file detection
# -----------------------------------------------------------------------------
apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libharfbuzz-subset0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

# -----------------------------------------------------------------------------
# Step 4: Unicode Font Packages
# -----------------------------------------------------------------------------
# Description: Installs comprehensive font packages for proper rendering of
#              international text, especially Arabic and Persian scripts.
#
# Packages:
#   - fonts-dejavu-core: High-quality fallback fonts with wide Unicode coverage
#   - fonts-liberation: Metric-compatible substitutes for common fonts
#   - fonts-noto-core: Google's Noto font family providing broad multilingual
#     coverage including Arabic and Persian scripts
# -----------------------------------------------------------------------------
apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    fonts-liberation \
    fonts-noto-core

# -----------------------------------------------------------------------------
# Step 5: SSL/TLS Certificates
# -----------------------------------------------------------------------------
# Description: Installs CA certificates required for TLS/HTTPS connections
#              when downloading packages with pip or making HTTPS requests.
# -----------------------------------------------------------------------------
apt-get install -y --no-install-recommends \
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
