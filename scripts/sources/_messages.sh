#!/usr/bin/env bash

# =============================================================================
# MESSAGE FUNCTIONS LIBRARY
# 
# A collection of colorized, icon-based message functions for bash scripts.
# Provides consistent styling for different types of user feedback.
# =============================================================================

#!/bin/bash
###############################################################################
# MESSAGE UTILITY FUNCTION
# 
# A comprehensive messaging utility for creating beautifully formatted console
# output with support for indentation, colors, icons, and semantic message types.
# 
# Author: [Your Name/Team]
# Version: 1.0.0
# License: MIT
###############################################################################

# -----------------------------------------------------------------------------
# ANSI COLOR CODE DEFINITIONS
# 
# These are standardized ANSI escape codes for terminal text formatting.
# Using 'readonly' ensures they cannot be accidentally modified elsewhere.
# 
# Color Format: \033[STYLE;COLORm
#   - \033[     : Escape sequence start
#   - 1;        : Style (1 = bold/bright)
#   - 31        : Color code (31 = red)
#   - m         : Escape sequence end
# 
# Reference: https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
# -----------------------------------------------------------------------------
COLOR_RESET='\033[0m'      # Reset all formatting (style, color, etc.)
COLOR_RED='\033[1;31m'     # Bright red for errors and critical alerts
COLOR_GREEN='\033[1;32m'   # Bright green for success and positive status
COLOR_YELLOW='\033[1;33m'  # Bright yellow for warnings and cautions
COLOR_BLUE='\033[1;34m'    # Bright blue for informational messages
COLOR_MAGENTA='\033[1;35m' # Bright magenta for special highlights
COLOR_CYAN='\033[1;36m'    # Bright cyan for secondary information
COLOR_WHITE='\033[1;37m'   # Bright white for normal text output
# Standard color scheme
COLOR_ADVICE='\033[1;97m'  # Bight bold white for suggestions
COLOR_SUCCESS='\033[1;32m' # Bright green
COLOR_ERROR='\033[1;31m'   # Bright red  
COLOR_WARNING='\033[1;33m' # Bright yellow
COLOR_INFO='\033[1;34m'    # Bright blue
COLOR_DEBUG='\033[3;37m'   # Gray (dim) - doesn't compete

# -----------------------------------------------------------------------------
# FUNCTION: message
# 
# DESCRIPTION:
#   Prints formatted messages to standard output with configurable appearance.
#   Supports hierarchical indentation, semantic coloring (success/error/warning/info),
#   custom colors, and optional icon prefixes. Ideal for creating user-friendly
#   CLI applications with consistent visual feedback.
# 
# FEATURES:
#   • Hierarchical indentation (level-based)
#   • Semantic message types (success, error, warning, info)
#   • Custom color selection
#   • Optional icon prefixes
#   • Proper ANSI code handling
#   • Error checking for invalid input
# 
# USAGE EXAMPLES:
#   message "Simple text message"                 # Plain text, no formatting
#   message -l 2 "Indented message"               # Level 2 indentation (2 spaces)
#   message -s "Operation successful"             # Green success with checkmark
#   message -e "Failed to process request"        # Red error with cross
#   message -w "Disk space running low"           # Yellow warning with alert icon
#   message -i "Processing data..."               # Blue info with arrow
#   message -c magenta "Custom color message"     # Magenta colored text
#   message -l 3 -s "Indented success message"    # Combined indentation + semantic
#   message -p "▶ " "Custom prefix message"       # Custom prefix icon
# 
# PARAMETERS:
#   -l, --level LEVEL     : Indentation level (integer). Level 1 = 0 spaces,
#                           Level 2 = 2 spaces, Level 3 = 4 spaces, etc.
#                           Formula: (LEVEL - 1) × 2 spaces
#   -c, --color COLOR     : Apply specific color (red, green, yellow, blue,
#                           magenta, cyan, white, or any valid ANSI code)
#   -s, --success         : Format as success message (green with ✓ icon)
#   -e, --error           : Format as error message (red with ✗ icon)
#   -w, --warning         : Format as warning message (yellow with ⚠ icon)
#   -i, --info            : Format as info message (blue with → icon)
#   -p, --prefix PREFIX   : Custom text/icon to prepend to message
#   MESSAGE               : Text content to display (required)
# 
# RETURN VALUES:
#   0  : Message printed successfully
#   1  : Invalid parameters or usage error
# 
# NOTES:
#   • Color support depends on terminal capabilities
#   • Icons require UTF-8 compatible terminal
#   • Always resets color formatting after each message
#   • Use semantic options (-s, -e, -w, -i) for consistent UI
# -----------------------------------------------------------------------------
message() {
    # -------------------------------------------------------------------------
    # LOCAL VARIABLE DECLARATIONS
    # 
    # indent_level : User-specified indentation level (default: 0 = no indent)
    # text         : The message content to display
    # color        : ANSI color code to apply (default: COLOR_RESET)
    # prefix       : Optional text/icon to prepend before message
    # suffix       : Optional text/icon to append after message (reserved)
    # -------------------------------------------------------------------------
    local indent_level=0
    local text=""
    local color="$COLOR_RESET"
    local prefix=""
    local suffix=""
    
    # -------------------------------------------------------------------------
    # PARSE COMMAND-LINE OPTIONS
    # 
    # Uses while-loop pattern to handle both short (-l) and long (--level) forms.
    # Shift positional parameters as they are consumed to isolate message text.
    # 
    # Pattern: while [[ $# -gt 0 ]]; do ... shift ... done
    # -------------------------------------------------------------------------
    while [[ $# -gt 0 ]]; do
        case "$1" in
            # -----------------------------------------------------------------
            # INDENTATION LEVEL OPTION
            # 
            # Accepts: -l, --level, --indent
            # Requires: Numeric argument (positive integer)
            # Behavior: Sets indent_level to specified value
            # Error: Returns 1 if argument is missing or non-numeric
            # -----------------------------------------------------------------
            -l|--level|--indent)
                if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
                    indent_level="$2"
                    shift 2  # Consume both option and its argument
                else
                    # Invalid or missing level argument
                    echo "Error: -l requires a numeric level" >&2  # STDERR
                    return 1  # Exit function with error code
                fi
                ;;
            
            # -----------------------------------------------------------------
            # CUSTOM COLOR OPTION
            # 
            # Accepts: -c, --color
            # Requires: Color name (red, green, yellow, blue, magenta, cyan, white)
            # Behavior: Maps color name to corresponding ANSI code
            # Default: COLOR_RESET for unrecognized color names
            # -----------------------------------------------------------------
            -c|--color)
                case "$2" in
                    red) color="$COLOR_RED";;
                    green) color="$COLOR_GREEN";;
                    yellow) color="$COLOR_YELLOW";;
                    blue) color="$COLOR_BLUE";;
                    magenta) color="$COLOR_MAGENTA";;
                    cyan) color="$COLOR_CYAN";;
                    white) color="$COLOR_WHITE";;
                    *) color="$COLOR_RESET";;  # Graceful fallback
                esac
                shift 2  # Consume both option and its argument
                ;;
            
            # -----------------------------------------------------------------
            # SEMANTIC MESSAGE TYPE: SUCCESS
            # 
            # Accepts: -s, --success
            # Behavior: Applies green color and checkmark (✓) prefix
            # Use case: Operation completed successfully
            # -----------------------------------------------------------------
            -s|--success)
                color="$COLOR_SUCCESS"
                prefix="✓ "  # UTF-8 checkmark symbol
                shift  # Consume only the option flag
                ;;
            
            # -----------------------------------------------------------------
            # SEMANTIC MESSAGE TYPE: ERROR
            # 
            # Accepts: -e, --error
            # Behavior: Applies red color and cross (✗) prefix
            # Use case: Operation failed or error condition
            # -----------------------------------------------------------------
            -e|--error)
                color="$COLOR_ERROR"
                prefix="✗ "  # UTF-8 cross symbol
                shift  # Consume only the option flag
                ;;
            
            # -----------------------------------------------------------------
            # SEMANTIC MESSAGE TYPE: WARNING
            # 
            # Accepts: -w, --warning
            # Behavior: Applies yellow color and warning (⚠) prefix
            # Use case: Potential issues or cautionary notes
            # -----------------------------------------------------------------
            -w|--warning)
                color="$COLOR_WARNING"
                prefix="⚠ "    # UTF-8 warning symbol
                shift   # Consume only the option flag
                ;;
            
            # -----------------------------------------------------------------
            # SEMANTIC MESSAGE TYPE: INFORMATION
            # 
            # Accepts: -i, --info
            # Behavior: Applies info color and arrow (→) prefix
            # Use case: General information or progress updates
            # -----------------------------------------------------------------
            -i|--info)
                color="$COLOR_INFO"
                prefix="→ " # UTF-8 right arrow symbol
                shift   # Consume only the option flag
                ;;
            
            # -----------------------------------------------------------------
            # SEMANTIC MESSAGE TYPE: DEBUG
            # Accepts: -d, --debug
            # Applies: Gray color with magnifying glass icon
            # Use: For development and diagnostic messages
            # -----------------------------------------------------------------
            -d|--debug)
                color="$COLOR_DEBUG"
                prefix="🪲 " # Bug icon
                shift   # Consume only the option flag
                ;;
            # -----------------------------------------------------------------
            # SEMANTIC MESSAGE TYPE: ADVICE
            # Accepts: -a, --advice
            # Applies: Cyan color with light bulb icon
            # Use: For helpful suggestions and recommendations
            # -----------------------------------------------------------------
            -a|--advice)
                color="$COLOR_ADVICE"
                prefix="> "  # Greater than symbol
                shift
                ;;
            
            # -----------------------------------------------------------------
            # CUSTOM PREFIX OPTION
            # 
            # Accepts: -p, --prefix
            # Requires: String argument (any text/icon)
            # Behavior: Sets custom prefix text (overrides semantic prefixes)
            # Use case: Application-specific icons or numbering
            # -----------------------------------------------------------------
            -p|--prefix)
                prefix="$2"
                shift 2  # Consume both option and its argument
                ;;
            
            # -----------------------------------------------------------------
            # MESSAGE TEXT (DEFAULT CASE)
            # 
            # Assumes any non-option argument is the message content.
            # This must be the last positional parameter after all options.
            # 
            # Note: Does not support messages starting with hyphen (-)
            #       For that case, use -- to separate options: message -- "-text"
            # -----------------------------------------------------------------
            *)
                text="$1"
                shift  # Consume the message text
                ;;
        esac
    done
    
    # -------------------------------------------------------------------------
    # CALCULATE INDENTATION SPACES
    # 
    # Implements formula: (indent_level - 1) × 2
    # 
    # Level  Examples:
    #   0  → 0 spaces  (special case, treated as no indentation)
    #   1  → 0 spaces  (1-1=0, ×2=0)
    #   2  → 2 spaces  (2-1=1, ×2=2)
    #   3  → 4 spaces  (3-1=2, ×2=4)
    #   4  → 6 spaces  (4-1=3, ×2=6)
    # 
    # Why (level-1)? Level 1 represents "no indentation" as base case.
    # -------------------------------------------------------------------------
    local indent_spaces=0
    if [[ $indent_level -gt 0 ]]; then
        indent_spaces=$(( (indent_level - 1) * 2 ))
    fi
    
    # -------------------------------------------------------------------------
    # CONSTRUCT FINAL FORMATTED MESSAGE
    # 
    # Order of components: [COLOR][PREFIX][TEXT][SUFFIX][RESET]
    # 
    # Important: Always end with COLOR_RESET to prevent "color bleed"
    #            where color affects subsequent terminal output.
    # -------------------------------------------------------------------------
    local full_message="${color}${prefix}${text}${suffix}${COLOR_RESET}"
    
    # -------------------------------------------------------------------------
    # OUTPUT THE MESSAGE WITH INDENTATION
    # 
    # Uses printf for precise control over indentation.
    #   %${indent_spaces}s  : Creates indentation padding
    #   %b                  : Interpret backslash escapes (for ANSI codes)
    #   \n                  : Newline after message
    # 
    # Alternative: echo -e interprets escapes but less precise for spacing.
    # -------------------------------------------------------------------------
    if [[ $indent_spaces -gt 0 ]]; then
        # Indented output using printf
        printf "%${indent_spaces}s%b\n" "" "$full_message"
    else
        # Non-indented output using echo -e
        echo -e "$full_message"
    fi
}

# -----------------------------------------------------------------------------
# Function: message_newline
# Description: Prints a blank line for better text formatting and readability
# Usage: message_newline
# Parameters: None
# Returns: Empty line in output
# -----------------------------------------------------------------------------
message_newline() {
    echo
}

# -----------------------------------------------------------------------------
# Function: message_welcome
# Description: Displays a welcoming message with warm styling and heart icon
# Usage: message_welcome "Welcome message text"
# Parameters: $@ - The message text to display
# Returns: Formatted welcome message to stdout
# -----------------------------------------------------------------------------
message_welcome() {
    message -c red "\n\e[1;31m─────────────────────────────────────────────────────────────────\e[0m"
    message -c red "  \e[1;31m❤\e[0m \e[1;97m${@}\e[0m"
    message -c red "\e[1;31m─────────────────────────────────────────────────────────────────\e[0m\n"
}

# -----------------------------------------------------------------------------
# Function: message_debug
# Description: Shows debug information with subtle styling for technical details
# Usage: message_debug "Debug information"
# Parameters: $@ - Debug message content
# Returns: Formatted debug message to stdout
# -----------------------------------------------------------------------------
message_debug() {
    message -d "$@"
}

# -----------------------------------------------------------------------------
# Function: message_warning
# Description: Presents warning messages with high visibility and caution icon
# Usage: message_warning "Warning message text"
# Parameters: $@ - Warning content requiring user attention
# Returns: Formatted warning message to stdout
# -----------------------------------------------------------------------------
message_warning() {
    message -w "$@"
}

# -----------------------------------------------------------------------------
# Function: message_error
# Description: Displays error messages with urgent styling and clear failure icon
# Usage: message_error "Error description"
# Parameters: $@ - Error message content
# Returns: Formatted error message to stdout
# -----------------------------------------------------------------------------
message_error() {
    message -e "$@"
}

# -----------------------------------------------------------------------------
# Function: message_info
# Description: Shows informational messages with neutral styling and info icon
# Usage: message_info "Information text"
# Parameters: $@ - Informational content
# Returns: Formatted info message to stdout
# -----------------------------------------------------------------------------
message_info() {
    message -i "$@"
}

# -----------------------------------------------------------------------------
# Function: message_suggestion
# Description: Offers suggestions with friendly styling and idea bulb icon
# Usage: message_suggestion "Suggestion text"
# Parameters: $@ - Suggested action or advice
# Returns: Formatted suggestion message to stdout
# -----------------------------------------------------------------------------
message_suggestion() {
    message -a "$@"
}

# -----------------------------------------------------------------------------
# Function: message_success
# Description: Announces successful operations with positive green styling
# Usage: message_success "Success message"
# Parameters: $@ - Success description
# Returns: Formatted success message to stdout
# -----------------------------------------------------------------------------
message_success() {
    message -s "$@"
}

# -----------------------------------------------------------------------------
# Function: message_note
# Description: Displays important notes with attention-grabbing yellow styling
# Usage: message_note "Note content"
# Parameters: $@ - Note text
# Returns: Formatted note message to stdout
# -----------------------------------------------------------------------------
message_note() {
    message -p "! " -c yellow "$@"
}

# -----------------------------------------------------------------------------
# Function: message_ask
# Description: Prompts user for input with question icon and inviting blue color
# Usage: message_ask "Question to ask user"
# Parameters: $@ - Question text
# Returns: Formatted question prompt to stdout
# -----------------------------------------------------------------------------
message_ask() {
    echo -e "\e[1;94m?\e[0m \e[0;97m${@}\e[0m"
}

# -----------------------------------------------------------------------------
# Function: confirm_action
# Description: Interactive confirmation dialog for dangerous or irreversible actions
#              Displays warning message and action description, then prompts for confirmation
# Usage: confirm_action "Warning message" "Action description"
# Parameters: 
#   $1 - Warning message explaining the risk
#   $2 - Detailed description of the action to be performed
# Returns: Exits script with success code if user confirms, exits with error if denied
# -----------------------------------------------------------------------------
confirm_action() {
    local message="$1"
    local action_description="$2"
    
    message_newline
    message_warning "⚠️  ${message}"
    message_info "   Action: ${action_description}"
    message_newline
    
    message_ask "Are you sure you want to continue?"
    read -p "  Type 'yes' to confirm or anything else to cancel: " confirmation
    
    if [[ ! "${confirmation}" =~ ^[Yy][Ee][Ss]$ ]]; then
        message_error "Operation cancelled by user."
        exit 0
    fi
    message_newline
}

# -----------------------------------------------------------------------------
# Function: message_table
# Description: Displays formatted tables with headers, content, and borders
# Supports three modes: header, row, or separator
# 
# Usage Examples:
#   Header:    message_table header "User Management" "System Users"
#   Row:       message_table row "Username" "Email" "Role"
#   Separator: message_table separator
#   Full table: message_table header "User List"
#               message_table row "john" "john@email.com" "Admin"
#               message_table row "jane" "jane@email.com" "User"
#               message_table separator
#
# Parameters:
#   $1 - Mode: 'header', 'row', 'separator', or 'footer'
#   $@ - Content (for header/row modes)
# -----------------------------------------------------------------------------
message_table() {
    local mode="$1"
    shift
    
    # Color definitions
    local border_color='\e[1;95m'      # Bright magenta for borders
    local header_color='\e[1;97m'      # Bright white for header text
    local row_color='\e[0;37m'         # Light gray for row text
    local reset_color='\e[0m'          # Reset colors
    
    # Table width (adjust as needed)
    local table_width=62
    
    case "$mode" in
        header|h)
            # -----------------------------------------------------------------
            # HEADER MODE: Creates a top border with centered header text
            # Multiple header lines are supported
            # -----------------------------------------------------------------
            local top_border="${border_color}┌"
            local bottom_border="${border_color}├"
            
            # Create top border
            for ((i=0; i<table_width-2; i++)); do
                top_border+="─"
            done
            top_border+="┐${reset_color}"
            echo -e "$top_border"
            
            # Add header lines (centered)
            if [ $# -gt 0 ]; then
                for line in "$@"; do
                    local line_length=${#line}
                    local padding_left=$(( (table_width - line_length - 4) / 2 ))
                    local padding_right=$(( table_width - line_length - padding_left - 4 ))
                    
                    printf "${border_color}│${header_color}"
                    printf "%${padding_left}s" ""
                    printf " %s " "$line"
                    printf "%${padding_right}s" ""
                    printf "${border_color}│${reset_color}\n"
                done
                
                # Add separator after header
                bottom_border=""
                for ((i=0; i<table_width-2; i++)); do
                    bottom_border+="─"
                done
                echo -e "${border_color}├${bottom_border}┤${reset_color}"
            fi
            ;;
        
        row|r)
            # -----------------------------------------------------------------
            # ROW MODE: Creates table rows with multiple columns
            # Columns are left-aligned with consistent spacing
            # -----------------------------------------------------------------
            if [ $# -eq 0 ]; then
                return
            fi
            
            printf "${border_color}│${reset_color}${row_color}"
            
            # Calculate column widths (simple equal distribution)
            local col_count=$#

            local col_width=$(( (table_width - 2) / $col_count - 3 ))
            
            local first=1
            for item in "$@"; do
                if [ $first -eq 1 ]; then
                    first=0
                else
                    printf "${border_color}│${reset_color}${row_color}"
                fi
                
                # Truncate if too long, add ellipsis
                if [ ${#item} -gt $col_width ]; then
                    printf " %-${col_width}.${col_width}s…" "$item"
                else
                    printf " %-${col_width}s " "$item"
                fi
            done
            
            printf " ${border_color}│${reset_color}\n" 
            ;;
        
        separator|s)
            # -----------------------------------------------------------------
            # SEPARATOR MODE: Creates horizontal separator lines
            # Used between sections or at the bottom of tables
            # -----------------------------------------------------------------
            local separator="${border_color}├"
            for ((i=0; i<table_width-2; i++)); do
                separator+="─"
            done
            separator+="┤${reset_color}"
            echo -e "$separator"
            ;;
        
        footer|f)
            # -----------------------------------------------------------------
            # FOOTER MODE: Creates bottom border for the table
            # Use after all content is displayed
            # -----------------------------------------------------------------
            local footer="${border_color}└"
            for ((i=0; i<table_width-2; i++)); do
                footer+="─"
            done
            footer+="┘${reset_color}"
            echo -e "$footer"
            ;;
        
        double|d)
            # -----------------------------------------------------------------
            # DOUBLE LINE MODE: Creates a double-line separator
            # Useful for major section breaks
            # -----------------------------------------------------------------
            local double_sep="${border_color}╞"
            for ((i=0; i<table_width-2; i++)); do
                double_sep+="═"
            done
            double_sep+="╡${reset_color}"
            echo -e "$double_sep"
            ;;
        
        *)
            echo "Usage: message_table [header|row|separator|footer|double] [content...]" >&2
            return 1
            ;;
    esac
}

# -----------------------------------------------------------------------------
# Function: spinner
# Description: Displays a rotating spinner animation while a background process
#              is running, accompanied by an informational message
# Usage: (long_running_command &) ; spinner "Processing data"
# Parameters:
#   $1 - Informational message to display next to spinner (string)
# Dependencies: Requires a background process to be running before calling
# Notes: Uses ANSI backspaces for animation. Ensure terminal supports escape sequences
#        Call with & to run command in background before invoking spinner
# -----------------------------------------------------------------------------
spinner() {
    # Accepts a message as input
    local info="$1"           # Store the informational message in a local variable

    # Get the process ID of the background process
    local pid=$!              # $! contains PID of most recent background command

    # Set the delay for the spinner animation
    local delay=0.5           # Time in seconds between spinner frame updates

    # Define the spinner characters
    local spinstr='|/-\'      # Four-character sequence for spinner animation

    # Loop until the background process is running
    while kill -0 $pid 2>/dev/null; do
        # Rotate the spinner characters
        local temp=${spinstr#?}                # Extract all but first character
        printf " [%c]  %s" "$spinstr" "$info"  # Display current spinner frame with message

        # Calculate the length of the message
        local msg_length=$(printf "%s" "$info" | wc -c)

        # Add backspace characters to reset the cursor position
        sleep $delay                       # Pause before next animation frame
        local reset="\b\b\b\b\b\b"         # Backspaces for "[X]  " part (6 chars)

        i=1
        while [ $i -le $msg_length ]; do
            reset+="\b"
            i=$((i + 1))
        done

        # Reset the cursor position for the next spinner update
        printf $reset                      # Move cursor back to start position
    done

    # Clear the spinner and message once the process is complete
    printf "    \b\b\b\b"                  # Overwrite spinner with spaces and backspace
}
