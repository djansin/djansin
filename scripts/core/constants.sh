#!/usr/bin/env bash

# =============================================================================
# YARSIN - Command Dispatcher for Containerized Development
# =============================================================================
# Description: Intelligent command dispatcher that routes commands to the
#              appropriate container services. Provides seamless integration
#              with Docker Compose and handles user permissions automatically.
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
#                     subcommand is provided. Defaults to dsm for
#                     intelligently route commands to appropriate containers.
# -----------------------------------------------------------------------------
: "${DEFAULT_SUBCOMMAND:=dsm}"
