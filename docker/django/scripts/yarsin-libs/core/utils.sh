#!/usr/bin/env bash

# =============================================================================
# UTILITY FUNCTIONS FOR YARSIN PROJECT
# =============================================================================
# This file contains reusable utility functions used across multiple yarsin
# commands. All functions are designed to be sourced by other scripts.
# =============================================================================


# =============================================================================
# DJANGO UTILITIES
# =============================================================================
# Functions for interacting with Django projects and configurations.
# =============================================================================

# -----------------------------------------------------------------------------
# Function: get_django_version
#
# Retrieves the Django version without the patch version.
#
# Description:
#   Calls Django's version command and extracts the major and minor version
#   numbers, omitting the patch version. Useful for generating documentation
#   links and compatibility checks.
#
# Usage:
#   django_version=$(get_django_version)
#
# Returns:
#   Prints Django version number without the patch version (e.g., "4.2")
#
# Example:
#   $ get_django_version
#   4.2
# -----------------------------------------------------------------------------
get_django_version() {
    local version
    version=$(python -m django --version 2>/dev/null) || {
        echo "Error: Django not found or not installed" >&2
        return 1
    }
    
    # Extract major.minor version
    local django_version
    django_version=$(echo "$version" | cut -d '.' -f 1,2)
    
    # Validate that we got a reasonable version
    if [[ -z "$django_version" || ! "$django_version" =~ ^[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Could not parse Django version: $version" >&2
        return 1
    fi
    
    echo "$django_version"
    return 0
}


# -----------------------------------------------------------------------------
# Function: check_settings_file
#
# Verifies that the Django settings module file exists.
#
# Description:
#   Constructs the full path to the settings module file by combining the
#   working directory with the converted settings module path and checks
#   for its existence. This is a critical check before running Django
#   management commands to ensure the project is properly configured.
#
# Globals:
#   WORK_DIRECTORY          - Base working directory
#   DJANGO_SETTINGS_MODULE  - Dotted path to Django settings module
#
# Returns:
#   0 if settings file exists
#   1 if settings file does not exist or required variables are not set
#
# Example:
#   if check_settings_file; then
#       echo "Settings file found"
#   else
#       echo "Settings file not found"
#   fi
# -----------------------------------------------------------------------------
check_settings_file() {
    # Validate required environment variables
    if [[ -z "${WORK_DIRECTORY:-}" ]]; then
        echo "Error: WORK_DIRECTORY environment variable is not set" >&2
        return 1
    fi
    
    if [[ -z "${DJANGO_SETTINGS_MODULE:-}" ]]; then
        echo "Error: DJANGO_SETTINGS_MODULE environment variable is not set" >&2
        return 1
    fi
    
    # Convert dotted path to filesystem path
    local settings_rel_path
    settings_rel_path=$(convert_dotted_path_to_slash "${DJANGO_SETTINGS_MODULE}")
    
    # Construct full path
    local settings_path="${WORK_DIRECTORY}/${settings_rel_path}"
    
    # Check if file exists (with .py extension)
    if [[ -f "${settings_path}.py" ]]; then
        return 0
    fi
    
    # Debug output for troubleshooting
    echo "Debug: Settings file not found at: ${settings_path}.py" >&2
    return 1
}


# =============================================================================
# PATH CONVERSION UTILITIES
# =============================================================================
# Functions for converting between different path formats.
# =============================================================================

# -----------------------------------------------------------------------------
# Function: convert_dotted_path_to_slash
#
# Converts a dotted path to a path with slashes.
#
# Description:
#   Transforms Python-style dotted module paths to filesystem paths.
#   Useful for converting Django settings module paths to actual file paths.
#
# Args:
#   $1 - dotted_path: Dotted path to convert (e.g., "apps.blog.models")
#
# Returns:
#   Prints path with slashes (e.g., "apps/blog/models")
#
# Example:
#   $ convert_dotted_path_to_slash "configs.settings.production"
#   configs/settings/production
#
#   $ convert_dotted_path_to_slash "apps.blog.models"
#   apps/blog/models
# -----------------------------------------------------------------------------
convert_dotted_path_to_slash() {
    local dotted_path="$1"
    
    # Validate input
    if [[ -z "$dotted_path" ]]; then
        echo "Error: No dotted path provided" >&2
        return 1
    fi
    
    # Remove any leading/trailing dots
    dotted_path="${dotted_path#.}"
    dotted_path="${dotted_path%.}"
    
    # Convert dots to slashes
    echo "$dotted_path" | tr '.' '/'
    
    return 0
}

# -----------------------------------------------------------------------------
# Function: convert_slashed_path_to_dot
#
# Converts a filesystem path to a dotted module path.
#
# Description:
#   Transforms filesystem paths to Python-style dotted module paths.
#   Useful for generating Python import paths from directory structures.
#
# Args:
#   $1 - slashed_path: Filesystem path to convert (e.g., "apps/blog/models")
#
# Returns:
#   Prints dotted module path (e.g., "apps.blog.models")
#
# Example:
#   $ convert_slashed_path_to_dot "configs/settings/production"
#   configs.settings.production
#
#   $ convert_slashed_path_to_dot "apps/blog/models"
#   apps.blog.models
# -----------------------------------------------------------------------------
convert_slashed_path_to_dot() {
    local slashed_path="$1"
    
    # Validate input
    if [[ -z "$slashed_path" ]]; then
        echo "Error: No slashed path provided" >&2
        return 1
    fi
    
    # Remove leading/trailing slashes
    slashed_path="${slashed_path#/}"
    slashed_path="${slashed_path%/}"
    
    # Convert slashes to dots
    echo "$slashed_path" | tr '/' '.'
    
    return 0
}


# =============================================================================
# USER AND SYSTEM UTILITIES
# =============================================================================
# Functions for querying user and system information.
# =============================================================================

# -----------------------------------------------------------------------------
# Function: get_user_default_shell
#
# Retrieves the default shell for a given user.
#
# Description:
#   Attempts to determine the user's default shell by checking the passwd
#   database. Falls back to system defaults if not found. This is useful
#   for scripts that need to execute commands with the user's preferred shell.
#
# Args:
#   $1 - username: Username to query
#
# Returns:
#   Prints the path to the user's default shell
#
# Example:
#   $ get_user_default_shell "www-data"
#   /usr/sbin/nologin
#
#   $ get_user_default_shell "$USER"
#   /bin/bash
# -----------------------------------------------------------------------------
get_user_default_shell() {
    local username="$1"
    
    # Validate input
    if [[ -z "$username" ]]; then
        echo "Error: No username provided" >&2
        return 1
    fi
    
    local shell=""
    
    # Try to get from passwd database
    if command -v getent >/dev/null 2>&1; then
        shell=$(getent passwd "$username" 2>/dev/null | cut -d: -f7)
    elif [[ -f /etc/passwd ]]; then
        shell=$(grep "^${username}:" /etc/passwd | cut -d: -f7)
    fi
    
    # If not found or invalid, try system defaults
    if [[ -z "$shell" || ! -x "$shell" ]]; then
        # Check useradd defaults
        if [[ -f /etc/default/useradd ]]; then
            shell=$(awk -F= '/^SHELL=/ {print $2}' /etc/default/useradd 2>/dev/null)
        fi
        
        # Check if shell is valid
        if [[ -n "$shell" && -x "$shell" ]]; then
            echo "$shell"
            return 0
        fi
        
        # Ultimate fallback
        echo "/bin/bash"
        return 0
    fi
    
    echo "$shell"
    return 0
}

# -----------------------------------------------------------------------------
# Function: user_exists
#
# Checks if a user exists in the system.
#
# Args:
#   $1 - username: Username to check
#
# Returns:
#   0 if user exists, 1 otherwise
#
# Example:
#   if user_exists "www-data"; then
#       echo "User exists"
#   fi
# -----------------------------------------------------------------------------
user_exists() {
    local username="$1"
    
    if [[ -z "$username" ]]; then
        return 1
    fi
    
    if command -v id >/dev/null 2>&1; then
        id "$username" >/dev/null 2>&1
        return $?
    elif command -v getent >/dev/null 2>&1; then
        getent passwd "$username" >/dev/null 2>&1
        return $?
    else
        # Fallback to checking /etc/passwd
        grep -q "^${username}:" /etc/passwd
        return $?
    fi
}

# -----------------------------------------------------------------------------
# Function: group_exists
#
# Checks if a group exists in the system.
#
# Args:
#   $1 - groupname: Group name to check
#
# Returns:
#   0 if group exists, 1 otherwise
#
# Example:
#   if group_exists "www-data"; then
#       echo "Group exists"
#   fi
# -----------------------------------------------------------------------------
group_exists() {
    local groupname="$1"
    
    if [[ -z "$groupname" ]]; then
        return 1
    fi
    
    if command -v getent >/dev/null 2>&1; then
        getent group "$groupname" >/dev/null 2>&1
        return $?
    else
        # Fallback to checking /etc/group
        grep -q "^${groupname}:" /etc/group
        return $?
    fi
}


# =============================================================================
# STRING UTILITIES
# =============================================================================
# Functions for string manipulation and formatting.
# =============================================================================

# -----------------------------------------------------------------------------
# Function: to_lower
#
# Converts a string to lowercase.
#
# Args:
#   $1 - input: String to convert
#
# Returns:
#   Prints lowercase version of the input string
#
# Example:
#   $ to_lower "HelloWorld"
#   helloworld
# -----------------------------------------------------------------------------
to_lower() {
    local input="$1"
    echo "$input" | tr '[:upper:]' '[:lower:]'
}

# -----------------------------------------------------------------------------
# Function: to_upper
#
# Converts a string to uppercase.
#
# Args:
#   $1 - input: String to convert
#
# Returns:
#   Prints uppercase version of the input string
#
# Example:
#   $ to_upper "HelloWorld"
#   HELLOWORLD
# -----------------------------------------------------------------------------
to_upper() {
    local input="$1"
    echo "$input" | tr '[:lower:]' '[:upper:]'
}

# -----------------------------------------------------------------------------
# Function: capitalize
#
# Capitalizes the first letter of a string.
#
# Args:
#   $1 - input: String to capitalize
#
# Returns:
#   Prints string with first letter capitalized
#
# Example:
#   $ capitalize "hello"
#   Hello
#
#   $ capitalize "hello world"
#   Hello world
# -----------------------------------------------------------------------------
capitalize() {
    local input="$1"
    echo "$(echo "${input:0:1}" | tr '[:lower:]' '[:upper:]')${input:1}"
}


# =============================================================================
# FILE SYSTEM UTILITIES
# =============================================================================
# Functions for safe file and path operations.
# =============================================================================

# -----------------------------------------------------------------------------
# Function: ensure_directory
#
# Ensures a directory exists, creating it if necessary.
#
# Args:
#   $1 - directory: Directory path to ensure
#   $2 - permissions: Optional permissions (default: 755)
#
# Returns:
#   0 on success, 1 on failure
#
# Example:
#   ensure_directory "/path/to/dir" 750
# -----------------------------------------------------------------------------
ensure_directory() {
    local directory="$1"
    local permissions="${2:-755}"
    
    if [[ -z "$directory" ]]; then
        echo "Error: No directory specified" >&2
        return 1
    fi
    
    if [[ ! -d "$directory" ]]; then
        mkdir -p "$directory" || {
            echo "Error: Failed to create directory: $directory" >&2
            return 1
        }
        chmod "$permissions" "$directory" 2>/dev/null || true
    fi
    
    return 0
}

# -----------------------------------------------------------------------------
# Function: join_path
#
# Joins path components safely.
#
# Args:
#   $@ - Path components to join
#
# Returns:
#   Prints joined path
#
# Example:
#   $ join_path "/base" "dir" "file.txt"
#   /base/dir/file.txt
# -----------------------------------------------------------------------------
join_path() {
    local path=""
    
    for component in "$@"; do
        if [[ -z "$component" ]]; then
            continue
        fi
        
        if [[ -z "$path" ]]; then
            path="$component"
        else
            # Remove trailing slash from path and leading slash from component
            path="${path%/}/${component#/}"
        fi
    done
    
    echo "$path"
}


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================
# Functions for validating input and configuration.
# =============================================================================

# -----------------------------------------------------------------------------
# Function: is_numeric
#
# Checks if a string is numeric.
#
# Args:
#   $1 - value: String to check
#
# Returns:
#   0 if numeric, 1 otherwise
#
# Example:
#   if is_numeric "123"; then
#       echo "Is numeric"
#   fi
# -----------------------------------------------------------------------------
is_numeric() {
    local value="$1"
    [[ "$value" =~ ^[0-9]+$ ]]
}

# -----------------------------------------------------------------------------
# Function: is_valid_port
#
# Checks if a value is a valid port number (1-65535).
#
# Args:
#   $1 - port: Port number to check
#
# Returns:
#   0 if valid, 1 otherwise
#
# Example:
#   if is_valid_port 8080; then
#       echo "Valid port"
#   fi
# -----------------------------------------------------------------------------
is_valid_port() {
    local port="$1"
    
    if ! is_numeric "$port"; then
        return 1
    fi
    
    [[ "$port" -ge 1 && "$port" -le 65535 ]]
}
