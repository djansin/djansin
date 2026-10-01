#!/usr/bin/env bash

# =============================================================================
# UTILITY FUNCTIONS FOR YARSIN PROJECT
# =============================================================================
# This file contains reusable utility functions used across multiple yarsin
# commands. All functions are designed to be sourced by other scripts.
# =============================================================================


# =============================================================================
# DATABASE UTILITIES
# =============================================================================
# Functions for interacting with PostgreSQL databases.
# =============================================================================

# -----------------------------------------------------------------------------
# Function: list_databases
#
# Lists all available PostgreSQL databases with additional information.
#
# Description:
#   Uses psql to query and display all non-template databases with their
#   table counts. Provides formatted output with colors and icons.
#
# Globals:
#   None
#
# Arguments:
#   None
#
# Returns:
#   0 - Success (databases listed or no databases found)
#   1 - Failed to connect or list databases
#
# Output Format:
#   Name: <database_name> (35 chars max)  Number of tables: <count>
#
# Colors:
#   Name label:    Bold Red
#   Name value:    White
#   Tables label:  Bold Green
#   Tables value:  White
#
# Example:
#   $ list_databases
#   
#       Available Databases:
#         Name: postgres                          Number of tables: 34
#         Name: myapp                             Number of tables: 12
# -----------------------------------------------------------------------------
list_databases() {
    alenaal_newline
    alenaal_format "Available Databases:" --indent 3 --color cyan --bold --icon "🐘"

    # Get list of databases, excluding templates
    local databases
    databases=$(psql -d postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;" 2>/dev/null)

    if [[ -z "$databases" ]]; then
        alenaal_warning "No databases found or unable to connect"
        return 1
    fi

    # Display each database
    local db
    while IFS= read -r db; do
        local num_tables=$(psql -d $db -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" | sed -n 3p)
        if [[ -n "$db" ]]; then
            printf "      \e[1;31mName:\e[0m \e[37m%-35s\e[0m\e[1;32mNumber of tables:\e[0m \e[37m%s\e[0m\n" "$db" "$num_tables"
        fi
    done <<< "$databases"

    alenaal_newline
}

# -----------------------------------------------------------------------------
# Function: database_exists
#
# Checks if a PostgreSQL database exists.
#
# Args:
#   $1 - db_name: Database name to check
#
# Returns:
#   0 if database exists
#   1 if database does not exist or error occurred
#
# Example:
#   if database_exists "myapp"; then
#       echo "Database exists"
#   else
#       echo "Database does not exist"
#   fi
# -----------------------------------------------------------------------------
database_exists() {
    local db_name="$1"

    if [[ -z "$db_name" ]]; then
        return 1
    fi

    psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$db_name'" | grep -q 1
    return $?
}

# -----------------------------------------------------------------------------
# Function: get_database_size
#
# Gets the size of a PostgreSQL database.
#
# Args:
#   $1 - db_name: Database name
#
# Returns:
#   Prints database size in human-readable format
#   Returns 1 if database does not exist
#
# Example:
#   size=$(get_database_size "myapp")
#   echo "Database size: $size"
# -----------------------------------------------------------------------------
get_database_size() {
    local db_name="$1"

    if ! database_exists "$db_name"; then
        echo "unknown"
        return 1
    fi

    psql -d postgres -tAc "SELECT pg_size_pretty(pg_database_size('$db_name'));" 2>/dev/null || echo "unknown"
}

# -----------------------------------------------------------------------------
# Function: get_database_owner
#
# Gets the owner of a PostgreSQL database.
#
# Args:
#   $1 - db_name: Database name
#
# Returns:
#   Prints database owner
#   Returns 1 if database does not exist
#
# Example:
#   owner=$(get_database_owner "myapp")
#   echo "Database owner: $owner"
# -----------------------------------------------------------------------------
get_database_owner() {
    local db_name="$1"

    if ! database_exists "$db_name"; then
        echo "unknown"
        return 1
    fi

    psql -d postgres -tAc "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = '$db_name';" 2>/dev/null || echo "unknown"
}

# -----------------------------------------------------------------------------
# Function: get_database_connection_count
#
# Gets the number of active connections to a database.
#
# Args:
#   $1 - db_name: Database name
#
# Returns:
#   Prints number of active connections
#
# Example:
#   conn=$(get_database_connection_count "myapp")
#   echo "Active connections: $conn"
# -----------------------------------------------------------------------------
get_database_connection_count() {
    local db_name="$1"

    psql -d postgres -tAc "SELECT count(*) FROM pg_stat_activity WHERE datname = '$db_name';" 2>/dev/null || echo "0"
}

# -----------------------------------------------------------------------------
# Function: terminate_connections
#
# Terminates all connections to a database.
#
# Args:
#   $1 - db_name: Database name
#
# Returns:
#   0 - Success (connections terminated)
#   1 - Failed to terminate connections
#
# Example:
#   if terminate_connections "myapp"; then
#       echo "All connections terminated"
#   fi
# -----------------------------------------------------------------------------
terminate_connections() {
    local db_name="$1"

    alenaal_info "Terminating connections to '$db_name'..."

    # Try different methods based on PostgreSQL version
    if psql -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$db_name' AND pid <> pg_backend_pid();" 2>/dev/null; then
        return 0
    else
        # Fallback for older PostgreSQL versions
        psql -d postgres -c "SELECT pg_terminate_backend(procpid) FROM pg_stat_activity WHERE datname = '$db_name' AND procpid <> pg_backend_pid();" 2>/dev/null
        return $?
    fi
}


# =============================================================================
# BACKUP UTILITIES
# =============================================================================
# Functions for listing and managing backup files.
# =============================================================================

# -----------------------------------------------------------------------------
# Function: list_backups
#
# Lists backup files based on a given pattern with detailed information.
#
# Description:
#   Searches for backup files matching a pattern and displays them in a
#   formatted table with file name, modification date, size, and owner.
#   Results are sorted by modification time (newest first).
#
# Features:
#   - Color-coded output for better readability
#   - Shows file name, date, size, and owner
#   - Sorts by modification time (newest first)
#   - Handles both absolute and relative paths
#   - Gracefully falls back to ls -l if stat is unavailable
#
# Args:
#   $1 - pattern: The pattern to search for in backup filenames (e.g., "*.tar.gz", "*_full.tar.gz")
#   $2 - path: Optional directory path to search (default: $BACKUP_ROOT)
#
# Environment Variables:
#   BACKUP_ROOT - Root backup directory (used if path not provided)
#
# Output Format:
#   File: <filename> (55 chars max)  Date: YYYY-MM-DD HH:MM:SS  Size: <size>  Owner: <owner>
#
# Colors:
#   File:   Bold Red
#   Date:   Bold Magenta
#   Size:   Bold Green
#   Owner:  Bold Blue
#
# Returns:
#   0 - Backups listed successfully (or no backups found)
#   1 - Invalid arguments
#   2 - Path does not exist
#
# Example:
#   list_backups "*.tar.gz"                    # List all tar.gz backups in BACKUP_ROOT
#   list_backups "*_full.tar.gz" /custom/path  # List full backups in custom path
#   list_backups "*.sql.gz" "${DATA_BACKUP_PATH}" # List SQL dumps
# -----------------------------------------------------------------------------
list_backups() {
    # -------------------------------------------------------------------------
    # Validate Input Arguments
    # -------------------------------------------------------------------------
    if [[ $# -lt 1 ]]; then
        echo "Error: list_backups requires at least a pattern argument" >&2
        echo "Usage: list_backups <pattern> [path]" >&2
        return 1
    fi

    local pattern="$1"
    local path="${2:-${BACKUP_ROOT:-/backup}}"

    # -------------------------------------------------------------------------
    # Validate Path
    # -------------------------------------------------------------------------
    if [[ ! -d "$path" ]]; then
        echo "Warning: Directory does not exist: $path" >&2
        return 2
    fi

    # -------------------------------------------------------------------------
    # Find and Display Backup Files
    # -------------------------------------------------------------------------
    # Use find to locate files matching pattern, sort by modification time
    # (newest first), and format output with colors
    
    # Check if we have GNU stat or BSD stat
    local use_gnu_stat=false
    if command -v stat >/dev/null 2>&1 && stat --version 2>/dev/null | grep -q "GNU"; then
        use_gnu_stat=true
    fi

    # Find files and process them
    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            # Get file stats
            local filename
            filename=$(basename "$file")
            
            # Get file size
            local size
            if [[ "$(uname)" == "Darwin" ]]; then
                # macOS/BSD
                size=$(stat -f "%z" "$file" 2>/dev/null)
                if command -v numfmt >/dev/null 2>&1; then
                    size=$(echo "$size" | numfmt --to=iec 2>/dev/null)
                else
                    size="${size}B"
                fi
            else
                # Linux/GNU
                size=$(stat -c "%s" "$file" 2>/dev/null)
                if command -v numfmt >/dev/null 2>&1; then
                    size=$(echo "$size" | numfmt --to=iec 2>/dev/null)
                else
                    size="${size}B"
                fi
            fi
            
            # Get file owner
            local owner
            owner=$(ls -ld "$file" 2>/dev/null | awk '{print $3}')
            
            # Get modification date in a consistent format
            local mod_date
            if [[ "$use_gnu_stat" == true ]]; then
                # GNU stat
                mod_date=$(stat -c "%y" "$file" 2>/dev/null | cut -d'.' -f1)
            else
                # BSD stat or fallback
                mod_date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$file" 2>/dev/null)
            fi
            
            # Fallback to ls if stat failed
            if [[ -z "$mod_date" ]]; then
                mod_date=$(ls -l "$file" 2>/dev/null | awk '{print $6, $7, $8}')
            fi
            
            # Truncate filename if too long
            if [[ ${#filename} -gt 50 ]]; then
                filename="${filename:0:47}..."
            fi
            
            # Format and print with colors
            printf "\033[1;31m  File:\033[0m %-50s \033[1;35mDate:\033[0m %-25s \033[1;32mSize:\033[0m %-10s \033[1;34mOwner:\033[0m %s\n" \
                "$filename" "$mod_date" "$size" "$owner"
        fi
    done < <(find "$path" -type f -name "$pattern" -print0 2>/dev/null | xargs -0 ls -lt 2>/dev/null | awk '{print $NF}' | head -20)

    return 0
}

# -----------------------------------------------------------------------------
# Function: list_backups_simple
#
# Simple version of list_backups that just lists filenames.
#
# Description:
#   A simpler alternative to list_backups that only shows filenames,
#   useful for scripts that need to parse the output.
#
# Args:
#   $1 - pattern: The pattern to search for in backup filenames
#   $2 - path: Optional directory path (default: $BACKUP_ROOT)
#
# Returns:
#   0 on success, non-zero on failure
#
# Example:
#   list_backups_simple "*.tar.gz" | while read -r file; do
#       echo "Processing $file"
#   done
# -----------------------------------------------------------------------------
list_backups_simple() {
    local pattern="$1"
    local path="${2:-${BACKUP_ROOT:-/backup}}"

    if [[ ! -d "$path" ]]; then
        return 1
    fi

    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS find doesn't support -printf
        find "$path" -maxdepth 1 -type f -name "$pattern" 2>/dev/null | \
            while read -r file; do
                basename "$file"
            done | sort -r
    else
        # Linux with GNU find
        find "$path" -maxdepth 1 -type f -name "$pattern" -printf "%f\n" 2>/dev/null | sort -r
    fi
}

# -----------------------------------------------------------------------------
# Function: list_backups_with_details
#
# Lists backups with detailed information in a structured format.
#
# Description:
#   Provides machine-readable output with detailed backup information
#   in key=value format, useful for scripting.
#
# Args:
#   $1 - pattern: The pattern to search for in backup filenames
#   $2 - path: Optional directory path (default: $BACKUP_ROOT)
#
# Output Format:
#   filename=<name> size=<bytes> date=<timestamp> owner=<user> permissions=<mode>
#
# Example:
#   list_backups_with_details "*.tar.gz" | while IFS=' ' read -r info; do
#       eval "$info"
#       echo "Restoring $filename ($size bytes)"
#   done
# -----------------------------------------------------------------------------
list_backups_with_details() {
    local pattern="$1"
    local path="${2:-${BACKUP_ROOT:-/backup}}"

    if [[ ! -d "$path" ]]; then
        return 1
    fi

    find "$path" -maxdepth 1 -type f -name "$pattern" -print0 2>/dev/null | while IFS= read -r -d '' file; do
        local filename
        filename=$(basename "$file")
        
        local size
        if [[ "$(uname)" == "Darwin" ]]; then
            size=$(stat -f "%z" "$file" 2>/dev/null)
        else
            size=$(stat -c "%s" "$file" 2>/dev/null)
        fi
        
        local mod_date
        if [[ "$(uname)" == "Darwin" ]]; then
            mod_date=$(stat -f "%m" "$file" 2>/dev/null)
        else
            mod_date=$(stat -c "%Y" "$file" 2>/dev/null)
        fi
        
        local owner
        if [[ "$(uname)" == "Darwin" ]]; then
            owner=$(stat -f "%Su" "$file" 2>/dev/null || echo "unknown")
        else
            owner=$(stat -c "%U" "$file" 2>/dev/null || echo "unknown")
        fi
        
        local perms
        if [[ "$(uname)" == "Darwin" ]]; then
            perms=$(stat -f "%Lp" "$file" 2>/dev/null || echo "???")
        else
            perms=$(stat -c "%a" "$file" 2>/dev/null || echo "???")
        fi
        
        echo "filename=$filename size=$size date=$mod_date owner=$owner permissions=$perms"
    done
}

# -----------------------------------------------------------------------------
# Function: get_latest_backup
#
# Returns the most recent backup file matching a pattern.
#
# Description:
#   Finds the newest backup file matching the given pattern and returns
#   its full path. Useful for automated restore scripts.
#
# Args:
#   $1 - pattern: The pattern to search for in backup filenames
#   $2 - path: Optional directory path (default: $BACKUP_ROOT)
#
# Returns:
#   Prints the full path of the latest backup file
#   Returns 1 if no backups found
#
# Example:
#   latest=$(get_latest_backup "*.tar.gz")
#   if [[ -n "$latest" ]]; then
#       echo "Restoring from $latest"
#   fi
# -----------------------------------------------------------------------------
get_latest_backup() {
    local pattern="$1"
    local path="${2:-${BACKUP_ROOT:-/backup}}"

    if [[ ! -d "$path" ]]; then
        return 1
    fi

    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS: use stat to get modification time
        find "$path" -maxdepth 1 -type f -name "$pattern" -print0 2>/dev/null | \
            xargs -0 stat -f "%m %N" 2>/dev/null | \
            sort -nr | \
            head -n1 | \
            cut -d' ' -f2-
    else
        # Linux with GNU find
        find "$path" -maxdepth 1 -type f -name "$pattern" -printf "%T@ %p\n" 2>/dev/null | \
            sort -nr | \
            head -n1 | \
            cut -d' ' -f2-
    fi
}

# -----------------------------------------------------------------------------
# Function: count_backups
#
# Counts the number of backups matching a pattern.
#
# Args:
#   $1 - pattern: The pattern to search for in backup filenames
#   $2 - path: Optional directory path (default: $BACKUP_ROOT)
#
# Returns:
#   Prints the count of matching backup files
# -----------------------------------------------------------------------------
count_backups() {
    local pattern="$1"
    local path="${2:-${BACKUP_ROOT:-/backup}}"

    if [[ ! -d "$path" ]]; then
        echo 0
        return 1
    fi

    find "$path" -maxdepth 1 -type f -name "$pattern" 2>/dev/null | wc -l | tr -d ' '
}


# =============================================================================
# FILE UTILITIES
# =============================================================================
# Functions for file and path manipulation.
# =============================================================================

# -----------------------------------------------------------------------------
# Function: get_file_name
#
# Extracts filename from a path.
#
# Args:
#   $1 - path: Full path
#
# Returns:
#   Prints the filename (basename)
#
# Example:
#   $ get_file_name "/path/to/file.txt"
#   file.txt
# -----------------------------------------------------------------------------
get_file_name() {
    local path="$1"
    echo "${path##*/}"
}

# -----------------------------------------------------------------------------
# Function: get_file_extension
#
# Extracts file extension from a filename.
#
# Args:
#   $1 - filename: Filename
#
# Returns:
#   Prints file extension (including the dot)
#
# Example:
#   $ get_file_extension "file.tar.gz"
#   .tar.gz
# -----------------------------------------------------------------------------
get_file_extension() {
    local filename="$1"
    echo "${filename#*.}"
}

# -----------------------------------------------------------------------------
# Function: get_file_size
#
# Gets human-readable file size.
#
# Args:
#   $1 - path: File path
#
# Returns:
#   Prints file size in human-readable format
#
# Example:
#   $ get_file_size "backup.tar.gz"
#   1.2G
# -----------------------------------------------------------------------------
get_file_size() {
    local path="$1"
    
    if [[ ! -f "$path" ]]; then
        echo "?"
        return 1
    fi
    
    if [[ "$(uname)" == "Darwin" ]]; then
        stat -f "%z" "$path" 2>/dev/null | numfmt --to=iec 2>/dev/null || echo "?"
    else
        stat -c "%s" "$path" 2>/dev/null | numfmt --to=iec 2>/dev/null || echo "?"
    fi
}
