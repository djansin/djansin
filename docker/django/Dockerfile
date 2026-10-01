# =============================================================================
# Dockerfile for Django Application with Multi-Stage Build
# =============================================================================
# Description: Multi-stage Docker build optimized for Django applications with
#              environment-specific dependency management and minimal image size.
#
# Key Features:
#   - Multi-stage build for optimal image size
#   - Environment-specific dependency management
#   - Development tools and configurations
#
# Usage:
#   Development: docker build --target development-run-stage -t myapp:dev .
#   Production:  docker build --build-arg BUILD_ENVIRONMENT=production -t myapp:prod .
#
# Author: Mohammad Ali Amini
# Date: 2026
# =============================================================================


# =============================================================================
# BUILD ARGUMENTS
# =============================================================================
# These arguments can be overridden at build time using --build-arg
# -----------------------------------------------------------------------------

# Build environment specification (development/production)
ARG BUILD_ENVIRONMENT=development

# Python version with base image (slim-bookworm for smaller footprint)
ARG PYTHON_TAG=3.14-slim-bookworm

# PyPI mirror URL (overrideable for faster regional downloads)
ARG PYPI_MIRROR=https://pypi.org/simple/

# Debian apt mirror (overrideable for faster regional downloads)
ARG APT_MIRROR=http://deb.debian.org/debian

# Working directory inside the container
ARG WORK_DIRECTORY=/app

# Disables APT security expiration checks (true/false). ⚠️ Security risk.
ARG SKIP_SEC_EXPIRY=false


# =============================================================================
# STAGE 1: BASE PYTHON IMAGE
# =============================================================================
# Stage: python-base
# Description: Initial stage providing the Python runtime environment.
#              Serves as the foundation for both build and runtime stages.
# -----------------------------------------------------------------------------
FROM python:${PYTHON_TAG} AS python-base

# -----------------------------------------------------------------------------
# Build Arguments
# -----------------------------------------------------------------------------
ARG APT_MIRROR
ARG PYPI_MIRROR
ARG SKIP_SEC_EXPIRY

# -----------------------------------------------------------------------------
# Configure Container Scripts and Entrypoint
# -----------------------------------------------------------------------------
# Description: Copies maintenance scripts and makes them executable.
#              These scripts handle database migrations, static file collection,
#              and other maintenance tasks.
# -----------------------------------------------------------------------------
COPY ./docker/django/scripts /usr/local/bin/maintenance

# Convert scripts to Unix line endings (fix Windows CRLF issues)
# Remove carriage returns (\r) from Windows line endings
RUN find /usr/local/bin/maintenance -type f -exec sed -i 's/\r$//' {} \;

# Make all scripts executable and move to PATH
# This allows running them as commands from anywhere in the container
RUN chmod +x /usr/local/bin/maintenance/* \
    && mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance

# -----------------------------------------------------------------------------
# Configure APT Mirror for Faster Package Downloads
# -----------------------------------------------------------------------------
# Description: Dynamically configures apt mirrors based on the distribution
#              codename to improve package download speeds.
# -----------------------------------------------------------------------------
RUN CODENAME=$(grep VERSION_CODENAME /etc/os-release | cut -d= -f2) \
    && tee /etc/apt/sources.list > /dev/null <<EOF
deb ${APT_MIRROR} ${CODENAME} main contrib non-free non-free-firmware
deb ${APT_MIRROR} ${CODENAME}-updates main contrib non-free non-free-firmware
deb ${APT_MIRROR} ${CODENAME}-backports main contrib non-free non-free-firmware
deb ${APT_MIRROR}-security ${CODENAME}-security main contrib non-free non-free-firmware
EOF

# -----------------------------------------------------------------------------
# Disable APT Repository Validity Checks (⚠️ SECURITY WARNING)
# -----------------------------------------------------------------------------
# Description: Disables apt's repository expiration and security validation.
#              This is a WORKAROUND for mirrors with outdated Release files,
#              particularly relevant in environments with national network
#              restrictions.
# 
# WARNING: These settings significantly compromise container security:
#   - Allows installation of outdated packages with known vulnerabilities
#   - Disables security update expiration checks
#   - Vulnerable to MITM (Man-in-the-Middle) attacks
#   - May allow installation of compromised/tampered packages
# 
# Use Case: ONLY when no reliable/updated mirror is accessible due to
#           network restrictions. This is a TEMPORARY workaround.
# -----------------------------------------------------------------------------
RUN if [[ ${SKIP_SEC_EXPIRY} == "true" ]]; then \
        echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99-no-check-valid-until \
        && echo 'Acquire::AllowInsecureRepositories "true";' >> /etc/apt/apt.conf.d/99-no-check-valid-until; \
    fi

# -----------------------------------------------------------------------------
# Configure PyPI Mirror for Faster Python Package Downloads
# -----------------------------------------------------------------------------
# Description: Sets up pip to use a custom PyPI mirror for faster package
#              downloads and configures trusted hosts to avoid SSL warnings.
# -----------------------------------------------------------------------------
RUN pip config set global.index ${PYPI_MIRROR} \
    && pip config set global.index-url ${PYPI_MIRROR} \
    && pip config set global.trusted-host $(echo ${PYPI_MIRROR} | sed -E 's|^https?://([^/:]+).*$|\1|') \
    && pip config set global.timeout 60


# =============================================================================
# STAGE 2: DEPENDENCY BUILD STAGE
# =============================================================================
# Stage: python-build-stage
# Description: Compilation stage for Python packages and dependencies.
#              This stage isolates build tools and compiles wheels for faster
#              runtime installation, reducing the final image size.
# -----------------------------------------------------------------------------
FROM python-base AS python-build-stage

# -----------------------------------------------------------------------------
# Build Arguments
# -----------------------------------------------------------------------------
# Build environment specification (development/production)
# This determines which requirements file to use
ARG BUILD_ENVIRONMENT

# -----------------------------------------------------------------------------
# Install System-Level Build Dependencies
# -----------------------------------------------------------------------------
# Description: Copies and executes the system build dependencies script.
#              Includes compilers, headers, and tools required for Python
#              package compilation (gcc, python3-dev, libpq-dev, etc.)
# -----------------------------------------------------------------------------
COPY ./docker/django/dependencies/system/build.sh /dependencies/system/build.sh

RUN chmod +x /dependencies/system/build.sh \
    && /dependencies/system/build.sh

# -----------------------------------------------------------------------------
# Install Python Dependencies (Wheel Compilation)
# -----------------------------------------------------------------------------
# Description: Copies requirements files for the specified environment and
#              compiles them into wheel format for faster installation in
#              the runtime stage.
#
# Benefits:
#   - Wheel files are pre-compiled, no build tools needed in runtime
#   - Faster pip installs in final stage
#   - Consistent and reproducible builds
# -----------------------------------------------------------------------------
COPY ./requirements /requirements

# Compile Python packages into wheel format
# --wheel-dir: Directory to store the compiled wheel files
RUN pip wheel --wheel-dir /usr/src/app/wheels \
    -i ${PYPI_MIRROR} \
    -r /requirements/${BUILD_ENVIRONMENT}.txt


# =============================================================================
# STAGE 3: RUNTIME STAGE (DEVELOPMENT)
# =============================================================================
# Stage: development-run-stage
# Description: Final runtime stage optimized for development environment.
#              Contains only runtime dependencies and application code,
#              excluding build tools for a smaller image size.
# -----------------------------------------------------------------------------
FROM python-base AS development-run-stage

# -----------------------------------------------------------------------------
# Build Arguments
# -----------------------------------------------------------------------------
ARG WORK_DIRECTORY

# -----------------------------------------------------------------------------
# Environment Variables
# -----------------------------------------------------------------------------
# Set environment variables for Python runtime optimization
ENV ENVIRONMENT=development \
    # PYTHONDONTWRITEBYTECODE=1: Prevents Python from writing .pyc files
    # Saves space and prevents permission issues with mounted volumes
    PYTHONDONTWRITEBYTECODE=1 \
    # PYTHONUNBUFFERED=1: Disables output buffering for real-time logging
    # Essential for development to see logs immediately
    PYTHONUNBUFFERED=1 \
    # Working directory for the application
    WORK_DIRECTORY=${WORK_DIRECTORY} \
    # Python path configuration for module resolution
    # Allows importing modules from the project root
    PYTHONPATH=${WORK_DIRECTORY}:$PYTHONPATH

# -----------------------------------------------------------------------------
# Install System-Level Runtime Dependencies (Development)
# -----------------------------------------------------------------------------
# Description: Copies and installs development-specific system dependencies.
#              Includes debugging tools, development headers, and utilities
#              useful during development (git, vim, htop, postgresql-client, etc.)
# -----------------------------------------------------------------------------
COPY ./docker/django/dependencies/system/development.sh /dependencies/system.sh

RUN chmod +x /dependencies/system.sh \
    && /dependencies/system.sh

# -----------------------------------------------------------------------------
# Install Python Dependencies from Pre-Compiled Wheels
# -----------------------------------------------------------------------------
# Description: Copies wheels from the build stage and installs them.
#              This avoids recompilation and significantly reduces build time.
# -----------------------------------------------------------------------------
COPY --from=python-build-stage /usr/src/app/wheels /wheels/

# Install Python dependencies from pre-compiled wheels
# --no-index: Ensures only local wheels are used (no network calls)
# --no-cache-dir: Reduces image size by not caching pip downloads
# --find-links: Specifies where to find wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    # Clean up wheels after installation to save space
    && rm -rf /wheels/

# -----------------------------------------------------------------------------
# Install Python-Level Development Dependencies
# -----------------------------------------------------------------------------
# Description: Initiate Python packages that are only needed in development.
#              Example: playwright install chromium
# -----------------------------------------------------------------------------
COPY ./docker/django/dependencies/python/development.sh /dependencies/python.sh

RUN chmod +x /dependencies/python.sh \
    && /dependencies/python.sh

# -----------------------------------------------------------------------------
# Copy Application Source Code
# -----------------------------------------------------------------------------
# Description: Sets working directory and copies the application code.
#              Note: .dockerignore is used to exclude unnecessary files:
#                - .git/ (version control)
#                - __pycache__/ (Python cache)
#                - .env files (secrets)
#                - logs/, backups/, media/ (runtime data)
#                - tests/ (if not needed in production)
# -----------------------------------------------------------------------------
WORKDIR ${WORK_DIRECTORY}

COPY . .

# -----------------------------------------------------------------------------
# Configure Container Runtime
# -----------------------------------------------------------------------------
# Description: Sets the container entrypoint and default command.
#
# ENTRYPOINT: Custom entrypoint script that handles:
#   - Environment variable substitution in config files
#   - Database migration checks
#   - Static file collection
#   - Waiting for dependent services
#
# CMD: Default command runs Django development server
#   --insecure: Serves static files in development (useful without collectstatic)
#   0.0.0.0:8000: Listens on all interfaces for container networking
# -----------------------------------------------------------------------------
ENTRYPOINT ["entrypoint"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# =============================================================================
# STAGE 4: RUNTIME STAGE (PRODUCTION)
# =============================================================================
# Stage: production-run-stage
# Description: Production-optimized runtime stage with minimal footprint.
#              Excludes development tools and uses production-specific
#              configurations for security and performance.
# -----------------------------------------------------------------------------
FROM python-base AS production-run-stage

# -----------------------------------------------------------------------------
# Build Arguments
# -----------------------------------------------------------------------------
ARG WORK_DIRECTORY

# -----------------------------------------------------------------------------
# Environment Variables (Production Settings)
# -----------------------------------------------------------------------------
ENV ENVIRONMENT=production \
    # Disable bytecode compilation (saves space, improves security)
    PYTHONDONTWRITEBYTECODE=1 \
    # Enable buffered output for better performance in production
    PYTHONUNBUFFERED=0 \
    # Working directory
    WORK_DIRECTORY=${WORK_DIRECTORY} \
    # Python path configuration
    PYTHONPATH=${WORK_DIRECTORY}:$PYTHONPATH

# -----------------------------------------------------------------------------
# Install System-Level Runtime Dependencies (Production Only)
# -----------------------------------------------------------------------------
# Description: Installs only production-required system dependencies.
#              Excludes development packages to minimize attack surface.
# -----------------------------------------------------------------------------
COPY ./docker/django/dependencies /dependencies

RUN chmod +x /dependencies/system/production.sh \
    && /dependencies/system/production.sh

# -----------------------------------------------------------------------------
# Install Python Dependencies from Pre-Compiled Wheels (Production)
# -----------------------------------------------------------------------------
# Description: Copies production wheels from the build stage and installs them.
#              Development dependencies are excluded from this stage.
# -----------------------------------------------------------------------------
COPY --from=python-build-stage /usr/src/app/wheels /wheels/

# Install only production dependencies
# Remove any development packages that might have been included
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

# -----------------------------------------------------------------------------
# Copy Application Source Code (Production)
# -----------------------------------------------------------------------------
# Description: Copies only application code, excluding test files and
#              development configurations to reduce image size.
# -----------------------------------------------------------------------------
WORKDIR ${WORK_DIRECTORY}

COPY . .

# -----------------------------------------------------------------------------
# Security Hardening for Production
# -----------------------------------------------------------------------------
# Description: Creates a non-root user to run the application process,
#              following the principle of least privilege for security.
# -----------------------------------------------------------------------------
RUN groupadd --system --gid 999 django \
    && useradd --system --uid 999 --gid django --no-create-home --shell /bin/bash django

# -----------------------------------------------------------------------------
# Configure Container Runtime (Production)
# -----------------------------------------------------------------------------
# Description: Sets the container entrypoint and switches to non-root user.
#              Uses Gunicorn as production WSGI server instead of Django's
#              development server.
# -----------------------------------------------------------------------------
ENTRYPOINT ["entrypoint"]

# Switch to non-root user for security
USER django

# Use Gunicorn for production WSGI serving
# --workers: Number of worker processes (auto-calculated based on CPU cores)
# --bind: Listen on all interfaces on port 8000
# --access-logfile: Log access logs to stdout for Docker log collection
# --error-logfile: Log error logs to stderr
CMD ["gunicorn", "configs.wsgi:application", "--workers=4", "--bind=0.0.0.0:8000", "--access-logfile=-", "--error-logfile=-"]


# =============================================================================
# STAGE 5: TESTING STAGE
# =============================================================================
# Stage: testing-stage
# Description: Specialized stage for running automated tests in CI/CD pipelines.
#              Includes test dependencies and excludes application code that
#              isn't needed for testing.
# -----------------------------------------------------------------------------
FROM python-base AS testing-stage

# -----------------------------------------------------------------------------
# Build Arguments
# -----------------------------------------------------------------------------
ARG WORK_DIRECTORY

# -----------------------------------------------------------------------------
# Environment Variables (Testing Configuration)
# -----------------------------------------------------------------------------
ENV ENVIRONMENT=testing \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WORK_DIRECTORY=${WORK_DIRECTORY} \
    PYTHONPATH=${WORK_DIRECTORY}:$PYTHONPATH \
    # Disable Django's test parallelization for consistent CI runs
    DJANGO_TEST_PARALLEL=0

# -----------------------------------------------------------------------------
# Install Test Dependencies
# -----------------------------------------------------------------------------
# Description: Installs system and Python dependencies required for testing.
#              This includes test runners, coverage tools, and mock libraries.
# -----------------------------------------------------------------------------
COPY ./docker/django/dependencies /dependencies

RUN chmod +x /dependencies/system/testing.sh \
    && /dependencies/system/testing.sh

# Copy and install test-specific Python dependencies
COPY ./requirements /requirements

# Install testing dependencies from wheels or from requirements file
RUN pip install --no-cache-dir \
    -i ${PYPI_MIRROR} \
    -r /requirements/testing.txt

# -----------------------------------------------------------------------------
# Copy Application Source Code for Testing
# -----------------------------------------------------------------------------
# Description: Copies the entire application including test files.
#              This stage is not used in production, so test files are included.
# -----------------------------------------------------------------------------
WORKDIR ${WORK_DIRECTORY}

COPY . .

# -----------------------------------------------------------------------------
# Default Command for Testing Stage
# -----------------------------------------------------------------------------
# Description: Runs the test suite with coverage reporting.
#              Override in CI/CD pipelines as needed.
# -----------------------------------------------------------------------------
CMD ["python", "manage.py", "test", "--verbosity=2", "--noinput"]
