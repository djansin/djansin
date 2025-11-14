#!/usr/bin/env sh

: "${WORK_DIRECTORY:=/app}" # The root directory of the Django project inside the container.
: "${PROJECT_NAME:=config}" # The name used to create and identify the directory for Django configuration files.
: "${APPS_DIRECTORY:=apps}" # The directory that contains the project’s custom apps.
: "${STATIC_ROOT:=/assets/static}" # The root directory for static files.
: "${MEDIA_ROOT:=/assets/media}"   # The root directory for media files.

: "${SERVER_PORT:=8000}"    # The port on which the Django server runs.

: "${USERNAME:=djansin}"    # The username used when creating a new user inside the container.
