#!/usr/bin/env bash

# =============================================================================
# ALENAAL - Terminal Notification and Formatting Library
# =============================================================================
# A comprehensive bash library for beautiful terminal output with semantic
# colors, icons, dividers, tables, and formatted notifications.
# =============================================================================

# =============================================================================
# ICON DEFINITIONS
# =============================================================================

# Associative array mapping semantic names to Unicode icon characters.
# These icons provide visual cues for different types of content.
declare -rA ICONS=(
    [guide]="🏆"          # Guide or tutorial content
    [description]="💠"    # Descriptive text
    [usage]="🔧"          # Usage instructions
    [info]="🔔"           # Informational content
    [example]="🚀"        # Example commands or code
    [subcommand]="📦"     # Subcommand name
    [option]="⚙️"         # Command option or flag
    [list]="☆"            # Regular list item
    [list-bold]="★"       # Highlighted list item
    [tip]="💡"             # Helpful tip or suggestion
    [note]="📌"            # Important note
    [warning]="⚠️"         # Warning message
    [error]="❌"           # Error message
    [success]="✅"         # Success message
    [complete]="🏅"        # Success message
    [divider]="━"          # Thick divider line
    [separator]="─"        # Thin separator line
    # Step/Progress indicators
    [step]="🏃"           # Current step/position
    [step-1]="①"          # Step 1
    [step-2]="②"          # Step 2
    [step-3]="③"          # Step 3
    [step-4]="④"          # Step 4
    [step-5]="⑤"          # Step 5
)


# =============================================================================
# COLOR SCHEME DEFINITIONS
# =============================================================================

# Maps semantic content types to color names for consistent theming.
# Colors reference the COLOR_CODES array below.
declare -rA COLORS=(
    [default]="default"              # Default terminal color
    [header]="cyan"                  # Main headers
    [section]="cyan"                 # Section headers
    [subsection]="cyan"              # Subsection headers
    [item]="white"                   # Regular list items
    [success]="green"                # Success notifications
    [warning]="yellow"               # Warning notifications
    [error]="red"                    # Error notifications
    [debug]="italic_white"           # Debug messages (dimmed)
    [info]="blue"                    # Information notifications
    [complete]="green"               # Complete notifications
    [cancel]="magenta"               # Cancel notifications
    [alarm]="yellow"                 # Alarm notifications
    [suggestion]="bright_white"      # Suggestions and advice
    [note]="white"
    [ask]="white"
    # Alenaal Table Colors
    [tb_border]="bright_magenta"     # Bright magenta for borders
    [tb_header_txt]="bright_white"   # Bright white for header text
    [tb_row]="white"                 # Light gray for row text
)


# =============================================================================
# INDENTATION LEVELS
# =============================================================================

# Defines default indentation levels (in indentation units) for different
# content types. Actual spaces = (level - 1) * INDENT_SPACES.
declare -rA INDENTS=(
    [default]=1          # Default indentation level
    [header]=1           # Header indentation
    [section]=2          # Section title indentation
    [subsection]=3       # Subsection title indentation
    [item]=3             # List item indentation
)


# =============================================================================
# DIVIDER CHARACTERS
# =============================================================================

# Collection of Unicode characters for creating visual separators.
# Used by alenaal_divider function for customizable dividers.
declare -rA DIVIDERS=(
    [single]="─"      # Light horizontal line
    [double]="═"      # Double horizontal line
    [thick]="━"       # Heavy horizontal line
    [dotted]="┄"      # Triple dotted line
    [dashed]="╌"      # Double dashed line
    [wave]="∼"        # Wave separator
    [hash]="#"        # Hash separator
    [dot]="•"         # Dot separator
    [star]="✧"        # Star separator
    [diamond]="◆"     # Diamond separator
    [arrow]="➤"       # Arrow separator
    [heart]="♥"       # Heart separator
)


# =============================================================================
# ANSI COLOR CODES
# =============================================================================

# Raw ANSI escape sequences for terminal colors.
# Used as building blocks for styled text with get_color_code().
declare -rA COLOR_CODES=(
    # Reset and default
    [reset]="\033[0m"       # Reset all attributes to terminal default
    [default]="\033[39m"    # Default foreground color (respects terminal theme)

    # Standard colors (normal intensity)
    [black]="\033[30m"      # Black
    [red]="\033[31m"        # Red
    [green]="\033[32m"      # Green
    [yellow]="\033[33m"     # Yellow
    [blue]="\033[34m"       # Blue
    [magenta]="\033[35m"    # Magenta
    [cyan]="\033[36m"       # Cyan
    [white]="\033[37m"      # White (light gray)

    # Bright/Bold colors (high intensity)
    [bright_black]="\033[90m"   # Bright black (dark gray)
    [bright_red]="\033[91m"     # Bright red
    [bright_green]="\033[92m"   # Bright green
    [bright_yellow]="\033[93m"  # Bright yellow
    [bright_blue]="\033[94m"    # Bright blue
    [bright_magenta]="\033[95m" # Bright magenta
    [bright_cyan]="\033[96m"    # Bright cyan
    [bright_white]="\033[97m"   # Bright white

    # Italic colors
    [italic_white]="\033[3;37m" # Italic white
)


# =============================================================================
# SEMANTIC PREFIX SYMBOLS
# =============================================================================

# Simple ASCII/Unicode symbols used as prefixes for different message types.
# These provide quick visual recognition of message importance/type.
declare -rA PREFIXES=(
    [success]="✓"
    [warning]="⚠"
    [error]="✗"
    [debug]="🪲"
    [info]="→"
    [complete]="◉"
    [cancel]="✖"
    [alarm]="!"
    [note]="✼"
    [suggestion]=">"
    [ask]="▶"
)


# =============================================================================
# GLOBAL CONSTANTS
# =============================================================================

# Number of spaces per indentation level
readonly INDENT_SPACES=2


# =============================================================================
# COLOR UTILITY FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
# Retrieves the color name associated with a semantic key.
#
# Args:
#   $1: color_key - Semantic key from COLORS array
#
# Returns:
#   Color name string (e.g., "red", "bright_white") or "default" if not found
# -----------------------------------------------------------------------------
get_color_name() {
    local color_key="$1"
    local color_name="${COLORS[$color_key]:-${COLORS[default]:-"default"}}"
    echo -n "$color_name"
}

# -----------------------------------------------------------------------------
# Retrieves the ANSI color code for a semantic key.
#
# Args:
#   $1: color_key - Semantic key from COLORS array
#
# Returns:
#   ANSI escape sequence for the color
# -----------------------------------------------------------------------------
get_color_code_by_key() {
    local color_key="$1"
    local color_name="${COLORS[$color_key]:-${COLORS[default]:-"default"}}"
    local color_code="${COLOR_CODES[$color_name]:-${COLOR_CODES[default]}}"
    echo -n "$color_code"
}

# -----------------------------------------------------------------------------
# Builds ANSI color code with optional text styles.
#
# This function creates proper ANSI escape sequences by combining a base color
# with bold and/or italic styling. It extracts the color number from the base
# code and constructs a new code with the requested style attributes.
#
# Args:
#   $1: color_name - Base color name from COLOR_CODES keys
#   $2: is_bold    - Optional: "true" to apply bold style (default: false)
#   $3: is_italic  - Optional: "true" to apply italic style (default: false)
#
# Returns:
#   ANSI escape sequence string (e.g., "\033[1;31m" for bold red)
#
# Example:
#   get_color_code "red" "true" "false"  # Returns "\033[1;31m"
# -----------------------------------------------------------------------------
get_color_code() {
    local color_name="$1"           # Base color name from COLOR_CODES
    local is_bold="${2:-false}"     # Apply bold style (1)
    local is_italic="${3:-false}"   # Apply italic style (3)

    # Validate and retrieve base color code
    local base_code="${COLOR_CODES[$color_name]:-}"

    if [[ -z "$base_code" ]]; then
        alenaal_warning "Invalid color name: '${color_name}'. Using default color."
        base_code="${COLOR_CODES[default]:-\033[39m}"
    fi

    # Extract color number from ANSI code
    # Remove the prefix "\033[" and suffix "m"
    local code_content="${base_code#\\033\[}"
    code_content="${code_content%m}"
    
    # Get the color number (everything after the last ';')
    local color_number="${code_content##*;}"
    
    # If color_number is empty (shouldn't happen), use a default
    if [[ -z "$color_number" ]]; then
        color_number="39"  # Default color
    fi

    # Build style part based on requested styles
    local style_parts=()
    local style_part=""

    [[ "$is_bold" == true ]] && style_parts+=("1")     # Bold style
    [[ "$is_italic" == true ]] && style_parts+=("3")   # Italic style

    # Construct final ANSI code
    local final_code

    if [[ ${#style_parts[@]} -gt 0 ]]; then
        # Join style parts with ';' separator
        printf -v style_part "%s;" "${style_parts[@]}"
        style_part="${style_part%;}"  # Remove trailing ';'
        
        # Format: \033[STYLE;COLOR_NUMBERm
        final_code="\033[${style_part};${color_number}m"
    else
        # No styles requested - use color number directly
        final_code="\033[${color_number}m"
    fi

    echo -n "$final_code"
    return 0
}


# =============================================================================
# ICON AND FORMATTING UTILITIES
# =============================================================================

# -----------------------------------------------------------------------------
# Retrieves an icon by its semantic key.
#
# Args:
#   $1: style - Semantic key from ICONS array
#
# Returns:
#   Icon character string or empty string if key not found
# -----------------------------------------------------------------------------
get_icon() {
    local style="$1"
    echo -n "${ICONS[$style]:-}"
}

# -----------------------------------------------------------------------------
# Gets indentation level for a content type.
#
# Args:
#   $1: type - Content type key from INDENTS array
#
# Returns:
#   Indentation level number (defaults to INDENTS[default] if type not found)
# -----------------------------------------------------------------------------
get_indent() {
    local type="$1"
    echo -n "${INDENTS[$type]:-$INDENTS[default]}"
}

# -----------------------------------------------------------------------------
# Retrieves a divider character by its code.
#
# Args:
#   $1: code - Divider key from DIVIDERS array
#
# Returns:
#   Divider character string or empty string if code not found
# -----------------------------------------------------------------------------
get_divider() {
    local code="$1"
    echo -n "${DIVIDERS[$code]:-}"
}

# -----------------------------------------------------------------------------
# Gets a semantic prefix symbol for message types.
#
# Args:
#   $1: code - Message type key from PREFIXES array
#
# Returns:
#   Prefix symbol string (success: ✓, error: ✗, etc.)
#   Returns non-zero exit code if key not found
# -----------------------------------------------------------------------------
get_semantic_prefix() {
    local code="$1"
    local prefix="${PREFIXES[$code]}"

    if [[ -n $prefix ]]; then
        echo -n "${PREFIXES[$code]}"
        return 0
    fi

    return 1
}


# =============================================================================
# CORE NOTIFICATION FUNCTION
# =============================================================================

# -----------------------------------------------------------------------------
# Core function for displaying styled notifications.
#
# This is the foundation of the alenaal system. It handles text styling,
# indentation, colors, and prefixes/suffixes. All other display functions
# ultimately call this function.
#
# Args:
#   Options:
#     -i, --indent NUM    : Indentation level (default: 1)
#     -c, --color NAME    : Direct color name (overrides semantic colors)
#     -p, --prefix TEXT   : Custom prefix text/icon
#     -s, --suffix TEXT   : Custom suffix text/icon
#     --italic            : Apply italic style
#     --bold              : Apply bold style
#     --inline            : Do not append newline (stay on same line)
#     --                  : Separator for notification text
#   Positional:
#     TEXT                : Notification content to display
#
# Returns:
#   0 on success, 1 on error (missing text)
#
# Example:
#   alenaal --color "red" --bold --prefix "★ " "Important message"
# -----------------------------------------------------------------------------
alenaal() {
    # Local variable initialization
    local text=""                                   # Notification content to display
    local prefix=""                                 # Optional text/icon to prepend
    local suffix=""                                 # Optional text/icon to append
    local indent_level=$(get_indent "default")      # User-specified indentation level
    local is_italic=false                           # Apply italic style flag
    local is_bold=false                             # Apply bold style flag
    local color_name=""                             # Direct color name (overrides semantic)
    local is_inline=false                           # Skip newline flag

    # Command-line option parsing
    while [[ $# -gt 0 ]]; do
        case "$1" in
            # Indentation Level Option
            -i|--indent)
                if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
                    indent_level="$2"
                    shift 2
                else
                    alenaal_error "Option '-i|--indent' requires a numeric level argument"
                    return 1
                fi
                ;;

            # Custom Color Option
            -c|--color)
                if [[ -z "$2" ]]; then
                    alenaal_error "Option '-c|--color' requires a color name"
                    return 1
                fi
                color_name=$2
                shift 2
                ;;

            # Custom Prefix Option
            -p|--prefix)
                if [[ $# -lt 2 ]]; then
                    alenaal_error "Option '-p|--prefix' requires a text or icon"
                    return 1
                fi
                prefix="$2"
                shift 2
                ;;

            # Custom Suffix Option
            -s|--suffix)
                if [[ $# -lt 2 ]]; then
                    alenaal_error "Option '-s|--suffix' requires a text or icon"
                    return 1
                fi
                suffix="$2"
                shift 2
                ;;

            # Style Option: Italic
            --italic)
                is_italic=true
                shift
                ;;

            # Style Option: Bold
            --bold)
                is_bold=true
                shift
                ;;

            # Style Option: Inline (no newline)
            --inline)
                is_inline=true
                shift
                ;;

            # Option Separator
            --)
                shift
                text="$*"
                if [[ -z "$text" ]]; then
                    alenaal_error "No notification text provided after '--' separator"
                    return 1
                fi
                break
                ;;

            # Unknown Option Handler
            -*)
                alenaal_warning "Unrecognized option: $1"
                shift
                ;;

            # Notification Text (Default Case)
            *)
                text="$1"
                shift
                ;;
        esac
    done

    # Input validation
    if [[ -z "$text" ]]; then
        alenaal_error "No notification text provided"
        return 1
    fi

    # Indentation calculation
    local indent_spaces=0
    if [[ $indent_level -gt 0 ]]; then
        indent_spaces=$(( (indent_level - 1) * $INDENT_SPACES ))
    fi

    # Color resolution
    if [[ -z "${color_name}" ]]; then
        color_name="default"
    fi

    # ANSI color code retrieval
    local color_code=$(get_color_code "${color_name}" "${is_bold}" "${is_italic}")

    # Notification construction
    local full_notification="${color_code}${prefix}${text}${suffix}$(get_color_code reset)"

    # -------------------------------------------------------------------------
    # Output with indentation
    # -------------------------------------------------------------------------
    # Two output modes:
    #   - Normal mode: adds newline at end (default)
    #   - Inline mode: no newline (useful for prompts)
    # -------------------------------------------------------------------------
    if [[ $is_inline == true ]]; then
        printf "%${indent_spaces}s%b" "" "$full_notification"
    else
        printf "%${indent_spaces}s%b\n" "" "$full_notification"
    fi
}


# =============================================================================
# DIVIDER FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
# Creates customizable horizontal dividers with optional centered text.
#
# This function generates lines made of repeated characters (dividers) that
# can span a specified length, include centered/left/right-aligned text,
# and support colors and indentation.
#
# Args:
#   Options:
#     -s, --style STYLE   : Divider style (key from DIVIDERS or custom char)
#     -i, --indent NUM    : Indentation level
#     -p, --padding NUM   : Padding spaces around text (default: 1)
#     -l, --length NUM    : Total divider length in characters (default: 60)
#     -c, --color NAME    : Color name for the divider
#     -t, --text TEXT     : Text to embed in the divider
#     -a, --align ALIGN   : Text alignment: left|center|right (default: left)
#     -w, --wrap NUM      : Number of style chars to wrap around text (default: 1)
#     --newline           : Add extra newline after divider
#     --                  : Separator for text (alternative to -t)
#   Positional:
#     TEXT                : Text to embed (alternative to -t)
#
# Returns:
#   0 on success, 1 on invalid parameters
#
# Example:
#   alenaal_divider --style double --length 80 --text "SECTION" --align center
# -----------------------------------------------------------------------------
alenaal_divider() {
    # Default configuration
    local style="━"                             # Default style character (thick line)
    local length=60                             # Default total length in characters
    local color=""                              # No color by default
    local text=""                               # No text by default
    local indent_level=$(get_indent "default")  # No indentation by default
    local align="left"                          # Left alignment by default
    local add_newline=false                     # No extra newline by default
    local padding=1                             # Padding spaces around text
    local wrap=1                                # Style characters wrapping text

    # Parse command-line options
    while [[ $# -gt 0 ]]; do
        case "$1" in
            # Style option
            -s|--style)
                if [[ -n "$2" ]]; then
                    # First try to get a predefined divider character
                    style=$(get_divider "$2")
                    # If no predefined style found, use the argument as custom character
                    if [[ -z $style ]]; then
                        style="$2"
                    fi
                    shift 2
                else
                    alenaal_error "Option '--style' requires an argument"
                    return 1
                fi
                ;;

            # Indentation option
            -i|--indent)
                if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
                    indent_level="$2"
                    shift 2
                else
                    alenaal_error "Option '--indent' requires a positive integer argument"
                    return 1
                fi
                ;;

            # Padding option
            -p|--padding)
                if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
                    padding="$2"
                    shift 2
                else
                    alenaal_error "Option '--padding' requires a positive integer argument"
                    return 1
                fi
                ;;

            # Length option
            -l|--length)
                if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
                    length="$2"
                    shift 2
                else
                    alenaal_error "Option '--length' requires a positive integer argument"
                    return 1
                fi
                ;;

            # Color option
            -c|--color)
                if [[ -n "$2" ]]; then
                    color="$2"
                    shift 2
                else
                    alenaal_error "Option '--color' requires an argument"
                    return 1
                fi
                ;;

            # Text option
            -t|--text)
                if [[ -n "$2" ]]; then
                    text="$2"
                    shift 2
                else
                    alenaal_error "Option '--text' requires an argument"
                    return 1
                fi
                ;;

            # Alignment option
            -a|--align)
                if [[ -n "$2" && "$2" =~ ^(left|center|right)$ ]]; then
                    align="$2"
                    shift 2
                else
                    alenaal_error "Option '--align' must be 'left', 'center', or 'right'"
                    return 1
                fi
                ;;

            # Wrap option
            -w|--wrap)
                if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
                    wrap="$2"
                    shift 2
                else
                    alenaal_error "Option '--wrap' requires a positive integer argument"
                    return 1
                fi
                ;;

            # Newline option
            --newline)
                add_newline=true
                shift
                ;;

            # Option separator
            --)
                shift
                if [[ $# -eq 0 ]]; then
                    alenaal_error "No text provided after '--' separator"
                    return 1
                fi
                text="$*"
                break
                ;;

            # Unknown option handler
            -*)
                alenaal_warning "Unrecognized option: $1"
                shift
                ;;

            # Text argument (default case)
            *)
                text="$1"
                shift
                ;;
        esac
    done

    # Validate parameters
    if [[ $length -lt 1 ]]; then
        alenaal_error "Length must be at least 1 character"
        return 1
    fi

    if [[ $indent_level -lt 0 ]]; then
        alenaal_error "Indent level cannot be negative"
        return 1
    fi

    if [[ $padding -lt 0 ]]; then
        alenaal_error "Padding value cannot be negative"
        return 1
    fi

    if [[ $wrap -lt 0 ]]; then
        alenaal_error "Wrap count cannot be negative"
        return 1
    fi

    # Warn about unusually large padding values but don't fail
    if [[ $padding -gt 20 ]]; then
        alenaal_warning "Padding value $padding is unusually large"
    fi

    # Build the divider
    local divider=""

    if [[ -n "$text" ]]; then
        local processed_text="$text"

        # Apply padding to text if specified
        if [[ $padding -gt 0 ]]; then
            local pad_spaces=""
            for ((i=0; i<padding; i++)); do
                pad_spaces+=" "
            done
            processed_text="${pad_spaces}${text}${pad_spaces}"
        fi

        # Apply wrap characters to text if specified
        if [[ $wrap -gt 0 ]]; then
            local wrap_chars=""
            for ((i=0; i<wrap; i++)); do
                wrap_chars+="${style}"
            done
            processed_text="${wrap_chars}${processed_text}${wrap_chars}"
        fi

        # Calculate final text length after padding and wrapping
        local text_len=${#processed_text}

        # Handle case where text is longer than requested length
        if [[ $text_len -ge $length ]]; then
            divider="$processed_text"
        else
            # Calculate space distribution based on alignment
            local left_len=0
            local right_len=0

            case "$align" in
                center)
                    left_len=$(( (length - text_len) / 2 ))
                    right_len=$(( length - text_len - left_len ))
                    ;;
                right)
                    left_len=$(( length - text_len ))
                    ;;
                left|*)
                    right_len=$(( length - text_len ))
                    ;;
            esac

            # Build left side with style characters
            for ((i=0; i<left_len; i++)); do
                divider+="$style"
            done

            # Add processed text
            divider+="$processed_text"

            # Build right side with style characters
            for ((i=0; i<right_len; i++)); do
                divider+="$style"
            done
        fi
    else
        # Simple divider without text
        for ((i=0; i<length; i++)); do
            divider+="$style"
        done
    fi

    # Output the divider
    local alenaal_options=()

    if [[ $indent_level -gt 0 ]]; then
        alenaal_options+=("-i" "$indent_level")
    fi

    if [[ -n "$color" ]]; then
        alenaal_options+=("-c" "$color")
    fi

    alenaal "${alenaal_options[@]}" "$divider"

    if $add_newline; then
        alenaal_newline
    fi

    return 0
}


# =============================================================================
# BASIC OUTPUT FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
# Outputs a blank line.
#
# Simply prints an empty line to the terminal for vertical spacing.
# -----------------------------------------------------------------------------
alenaal_newline() {
    echo
}


# =============================================================================
# SEMANTIC NOTIFICATION FUNCTIONS
# =============================================================================

# These functions provide convenient shortcuts for common message types.
# Each applies appropriate colors, prefixes, and styles automatically.

# -----------------------------------------------------------------------------
# Displays a success message with checkmark icon and green color.
#
# Args:
#   $@: Message text and optional alenaal arguments
# -----------------------------------------------------------------------------
alenaal_success() {
    local prefix=$(get_semantic_prefix "success")
    local color_name=$(get_color_name "success")

    alenaal --color "${color_name}" --prefix "${prefix} " "$@"
}

# -----------------------------------------------------------------------------
# Displays a warning message with warning icon and yellow color.
#
# Args:
#   $@: Message text and optional alenaal arguments
# -----------------------------------------------------------------------------
alenaal_warning() {
    local prefix=$(get_semantic_prefix "warning")
    local color_name=$(get_color_name "warning")

    alenaal --color "${color_name}" --prefix "${prefix} " "$@" >&2
}

# -----------------------------------------------------------------------------
# Displays an error message with X icon and red color.
#
# Args:
#   $@: Message text and optional alenaal arguments
# -----------------------------------------------------------------------------
alenaal_error() {
    local prefix=$(get_semantic_prefix "error")
    local color_name=$(get_color_name "error")

    alenaal --color "${color_name}" --prefix "${prefix} " "$@" >&2
}

# -----------------------------------------------------------------------------
# Displays a debug message with insect icon and italic_white color.
#
# Args:
#   $@: Message text and optional alenaal arguments
# -----------------------------------------------------------------------------
alenaal_debug() {
    local prefix=$(get_semantic_prefix "debug")
    local color_name=$(get_color_name "debug")

    alenaal --color "${color_name}" --prefix "${prefix} " "$@" >&2
}

# -----------------------------------------------------------------------------
# Displays an informational message with arrow icon and blue color.
#
# Args:
#   $@: Message text and optional alenaal arguments
# -----------------------------------------------------------------------------
alenaal_info() {
    local prefix=$(get_semantic_prefix "info")
    local color_name=$(get_color_name "info")

    alenaal --color "${color_name}" --prefix "${prefix} " "$@"
}

# -----------------------------------------------------------------------------
# Displays a complete message with ◉ icon and green color.
#
# Args:
#   $@: Message text and optional alenaal arguments
# -----------------------------------------------------------------------------
alenaal_complete() {
    local prefix=$(get_semantic_prefix "complete")
    local color_name=$(get_color_name "complete")

    alenaal --color "${color_name}" --prefix "${prefix} " "$@"
}

# -----------------------------------------------------------------------------
# Displays a alarm message with ✖ icon and green color.
#
# Args:
#   $@: Message text and optional alenaal arguments
# -----------------------------------------------------------------------------
alenaal_cancel() {
    local prefix=$(get_semantic_prefix "cancel")
    local color_name=$(get_color_name "cancel")

    alenaal --color "${color_name}" --prefix "${prefix} " "$@"
}

# -----------------------------------------------------------------------------
# Displays a alarm message with ⚠ icon and green color.
#
# Args:
#   $@: Message text and optional alenaal arguments
# -----------------------------------------------------------------------------
alenaal_alarm() {
    local prefix=$(get_semantic_prefix "alarm")
    local color_name=$(get_color_name "alarm")

    alenaal --color "${color_name}" --prefix "${prefix} " "$@"
}

# -----------------------------------------------------------------------------
# Displays a note message with ! icon and yellow color.
#
# Args:
#   $@: Message text and optional alenaal arguments
# -----------------------------------------------------------------------------
alenaal_note() {
    local prefix=$(get_semantic_prefix "note")
    local color_name=$(get_color_name "note")

    alenaal --color "${color_name}" --prefix "${prefix} " "$@"
}

# -----------------------------------------------------------------------------
# Displays a suggestion message with > icon and bright_white color.
#
# Args:
#   $@: Message text and optional alenaal arguments
# -----------------------------------------------------------------------------
alenaal_suggestion() {
    local prefix=$(get_semantic_prefix "suggestion")
    local color_name=$(get_color_name "suggestion")

    alenaal --color "${color_name}" --prefix "${prefix} " "$@"
}

# -----------------------------------------------------------------------------
# Displays a question prompt for user input.
#
# Args:
#   $@: Question text to display
# -----------------------------------------------------------------------------
alenaal_ask() {
    local prefix=$(get_semantic_prefix "ask")
    local color_name=$(get_color_name "ask")

    alenaal --color "${color_name}" --prefix "${prefix} " --inline "$@"
}


# =============================================================================
# WELCOME MESSAGE FUNCTION
# =============================================================================

# -----------------------------------------------------------------------------
# Displays a prominent welcome banner with red heart and full-width dividers.
#
# Creates a distinctive header for script startup, with the message centered
# between red horizontal lines.
#
# Args:
#   $@: Welcome message text
#
# Example:
#   alenaal_welcome "My Script v1.0.0"
# -----------------------------------------------------------------------------
alenaal_welcome() {
    alenaal -c red "\n\e[1;31m─────────────────────────────────────────────────────────────────\e[0m"
    alenaal -c red "  \e[1;31m❤\e[0m \e[1;97m${@}\e[0m"
    alenaal -c red "\e[1;31m─────────────────────────────────────────────────────────────────\e[0m"
}


# =============================================================================
# FORMATTED CONTENT FUNCTION
# =============================================================================

# -----------------------------------------------------------------------------
# Advanced formatting function for structured content display.
#
# This function provides a higher-level interface for displaying formatted
# content with automatic indentation, icons, dividers, and spacing based on
# content type. It's ideal for help screens, menus, and structured output.
#
# Args:
#   Type flags (mutually exclusive):
#     --header              : Main header formatting
#     --section             : Section header formatting
#     --subsection          : Subsection header formatting
#     --item                : List item formatting
#   
#   Style flags:
#     --STYLE_NAME          : Use icon from ICONS[STYLE_NAME] (e.g., --guide)
#   
#   Options:
#     --divider             : Add a divider after content
#     --newline             : Add a newline after content
#     --no-divider          : Suppress automatic divider
#     --no-newline          : Suppress automatic newline
#     -i, --indent NUM      : Custom indentation level
#     -p, --icon ICON       : Custom icon (overrides style-based icon)
#     --color NAME          : Custom color name
#     --italic              : Apply italic style
#     --bold                : Apply bold style
#     --                    : Separator for text content
#   
#   Positional:
#     TEXT                  : Content to display
#
# Returns:
#   0 on success, 1 on error
#
# Example:
#   alenaal_format --header --divider "Main Menu"
#   alenaal_format --section --guide --italic "Getting Started"
#   alenaal_format --item --icon "→" "Option 1: Initialize"
# -----------------------------------------------------------------------------
alenaal_format() {
    # Configuration and defaults
    local text=""                   # Text content to display
    local prefix=""
    local display_type=""           # Type of display (header, section, etc.)
    local display_style=""          # Style override
    local color_name=""             # Custom color override
    local indentation=""            # Indentation level
    local add_newline=false         # Add newline after content
    local add_divider=false
    local no_divider=false
    local no_newline=false
    local is_italic=false
    local is_bold=false

    # Parse command-line options
    while [[ $# -gt 0 ]]; do
        case "$1" in
            # Display type flags
            --header)       display_type="header"; shift ;;
            --section)      display_type="section"; shift ;;
            --subsection)   display_type="subsection"; shift ;;
            --item)         display_type="item"; shift ;;
            # Spacing controls
            --divider)      add_divider=true; shift ;;
            --newline)      add_newline=true; shift ;;
            --no-divider)   no_divider=true; shift ;;
            --no-newline)   no_newline=true; shift ;;

            # Indentation option
            -i|--indent)
                if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
                    indentation="$2"
                    shift 2
                else
                    if [[ -z $indentation ]]; then
                        alenaal_warning "Option '--indent' requires a positive integer argument"
                    fi
                fi
                ;;

            # Custom icon option
            -p|--prefix|--icon)
                if [[ -n "$2" ]]; then
                    prefix="$2 "
                    shift 2
                else
                    alenaal_error "Option '--icon' requires an argument"
                    return 1
                fi
                ;;

            # Custom color option
            --color)
                if [[ -n "$2" ]]; then
                    color_name="$2"
                    shift 2
                else
                    alenaal_error "Option '--color' requires an argument"
                    return 1
                fi
                ;;

            # Italic option
            --italic)
                is_italic=true
                shift
                ;;

            # Bold option
            --bold)
                is_bold=true
                shift
                ;;

            # Special handling for remaining arguments
            --)
                shift
                text="$*"
                break
                ;;

            # Style flags (catch-all for any other --* options)
            --*)
                display_style="${1##--}"
                shift
                ;;

            # Unknown options
            -*)
                alenaal_warning "Unrecognized option: $1"
                shift
                ;;

            # Content (first positional argument)
            *)
                text="$1"
                shift
                ;;
        esac
    done

    # Process display type and apply defaults
    local alenaal_args=()

    if [[ -n $display_type ]]; then
        [[ -z $indentation ]] && indentation=$(get_indent "$display_type")
        [[ -z $color_name ]] && color_name=$(get_color_name "$display_type")
    fi

    if [[ -n $display_style ]]; then
        [[ -z $prefix ]] && prefix="$(get_icon $display_style) "
    fi

    if [[ -z $indentation ]]; then
        indentation=$(get_indent "default")
    fi

    if [[ -z $color_name ]]; then
        color_name=$(get_color_name "default")
    fi

    # Display the main content if text is provided
    if [[ -n $text ]]; then
        alenaal_args+=("--prefix" "$prefix")
        alenaal_args+=("--indent" "$indentation")
        alenaal_args+=("--color" "$color_name")

        [[ $is_italic == true ]] && alenaal_args+=("--italic")
        [[ $is_bold == true ]] && alenaal_args+=("--bold")

        alenaal "${alenaal_args[@]}" -- "$text"
    fi

    # Configure divider based on display type
    local alenaal_div_args=()
    local divider_style="thick"
    local divider_length=60

    if [[ $display_type == "header" ]]; then
        [[ "$no_divider" == true ]] && add_divider=false || add_divider=true
        divider_length=85
        divider_style="double"
        [[ "$no_newline"  == true ]] || add_newline=true
    elif [[ $display_type == "section" ]]; then
        [[ "$no_divider" == true ]] && add_divider=false || add_divider=true
        if [[ -n $prefix ]]; then
            divider_length="$(( ${#prefix} + ${#text} + 1))"
        else
            divider_length="${#text}"
        fi
    elif $add_divider; then
        [[ "$no_divider" == true ]] && add_divider=false
        divider_length=$(( $divider_length - $INDENT_SPACES * $indentation))
        if [[ $divider_length -lt 1 ]]; then
            if [[ -n $prefix ]]; then
                divider_length="$(( ${#prefix} + ${#text} + 1))"
            else
                divider_length="${#text}"
            fi
        fi
        divider_style="dashed"
    fi

    # Display divider if requested
    if $add_divider; then
        alenaal_div_args+=("--indent" "$indentation")
        alenaal_div_args+=("--color" "$color_name")
        alenaal_div_args+=( "--length" "$divider_length" )
        alenaal_div_args+=( "--style" $divider_style)

        alenaal_divider "${alenaal_div_args[@]}"
    fi

    # Add extra newline if requested
    if $add_newline; then
        alenaal_newline
    fi
}


# =============================================================================
# TABLE DISPLAY FUNCTION
# =============================================================================

# -----------------------------------------------------------------------------
# Creates formatted tables with borders and multiple modes.
#
# This function builds ASCII/Unicode tables with various section types.
# It supports headers, rows, separators, footers, and double lines.
#
# Args:
#   $1: mode - Table section type:
#       header|h    : Creates top border with centered header text
#       row|r       : Creates a table row with multiple columns
#       separator|s : Creates a horizontal separator line
#       footer|f    : Creates bottom border
#       double|d    : Creates a double-line separator
#   $@: For header mode: lines of header text
#       For row mode: column values
#       For other modes: ignored
#
# Returns:
#   0 on success, 1 on invalid mode
#
# Example:
#   alenaal_table header "User List" "Active Users"
#   alenaal_table row "ID" "Name" "Status"
#   alenaal_table separator
#   alenaal_table row "1" "John" "Active"
#   alenaal_table footer
# -----------------------------------------------------------------------------
alenaal_table() {
    local mode="$1"
    shift

    # Color definitions
    local border_color=$(get_color_code_by_key "tb_border")         # Bright magenta for borders
    local header_color=$(get_color_code_by_key "tb_header_txt")     # Bright white for header text
    local row_color=$(get_color_code_by_key "tb_row")               # Light gray for row text
    local reset_color=$(get_color_code "reset")                     # Reset colors

    local table_width=62    # Table width (adjust as needed)

    case "$mode" in
        header|h)
            # Header mode: Creates a top border with centered header text
            # Create top border
            local top_border="${border_color}┌"
            local i=0
            while [ "$i" -lt "$((table_width - 2))" ]; do
                top_border="${top_border}─"
                i=$((i + 1))
            done
            top_border="${top_border}┐${reset_color}"
            printf "%b\n" "$top_border"

            # Add header lines (centered)
            if [ "$#" -gt 0 ]; then
                for line in "$@"; do
                    local line_length=$(printf "%s" "$line" | wc -m)
                    local padding_left=$(( (table_width - line_length - 4) / 2 ))
                    local padding_right=$(( table_width - line_length - padding_left - 4 ))

                    printf "%b" "${border_color}│${header_color}"

                    # Left padding
                    local j=0
                    while [ "$j" -lt "$padding_left" ]; do
                        printf " "
                        j=$((j + 1))
                    done

                    printf " %s " "$line"

                    # Right padding
                    j=0
                    while [ "$j" -lt "$padding_right" ]; do
                        printf " "
                        j=$((j + 1))
                    done

                    printf "%b\n" "${border_color}│${reset_color}"
                done

                # Add separator after header
                local bottom_border="${border_color}├"
                local i=0
                while [ "$i" -lt "$((table_width - 2))" ]; do
                    bottom_border="${bottom_border}─"
                    i=$((i + 1))
                done
                bottom_border="${bottom_border}┤${reset_color}"
                printf "%b\n" "$bottom_border"
            fi
            ;;

        row|r)
            # Row mode: Creates table rows with multiple columns
            if [ "$#" -eq 0 ]; then
                return 0
            fi

            printf "%b" "${border_color}│${reset_color}${row_color}"

            # Calculate column widths (simple equal distribution)
            col_count="$#"
            col_width=$(( (table_width - 2) / col_count - 3 ))

            first=1
            for item in "$@"; do
                if [ "$first" -eq 1 ]; then
                    first=0
                else
                    printf "%b" "${border_color}│${reset_color}${row_color}"
                fi

                # Truncate if too long, add ellipsis
                item_length=$(printf "%s" "$item" | wc -m)
                if [ "$item_length" -gt "$col_width" ]; then
                    # Extract substring manually for sh compatibility
                    truncated=$(printf "%s" "$item" | cut -c 1-"$((col_width - 1))")
                    printf " %s…" "$truncated"
                    # Add remaining spaces
                    k=0
                    while [ "$k" -lt "$((col_width - ${#truncated}))" ]; do
                        printf " "
                        k=$((k + 1))
                    done
                else
                    printf " %s " "$item"
                    # Add padding
                    k=0
                    while [ "$k" -lt "$((col_width - item_length))" ]; do
                        printf " "
                        k=$((k + 1))
                    done
                fi
            done

            printf " %b\n" "${border_color}│${reset_color}"
            ;;

        separator|s)
            # Separator mode: Creates horizontal separator lines
            separator="${border_color}├"
            i=0
            while [ "$i" -lt "$((table_width - 2))" ]; do
                separator="${separator}─"
                i=$((i + 1))
            done
            separator="${separator}┤${reset_color}"
            printf "%b\n" "$separator"
            ;;

        footer|f)
            # Footer mode: Creates bottom border for the table
            footer="${border_color}└"
            i=0
            while [ "$i" -lt "$((table_width - 2))" ]; do
                footer="${footer}─"
                i=$((i + 1))
            done
            footer="${footer}┘${reset_color}"
            printf "%b\n" "$footer"
            ;;

        double|d)
            # Double line mode: Creates a double-line separator
            double_sep="${border_color}╞"
            i=0
            while [ "$i" -lt "$((table_width - 2))" ]; do
                double_sep="${double_sep}═"
                i=$((i + 1))
            done
            double_sep="${double_sep}╡${reset_color}"
            printf "%b\n" "$double_sep"
            ;;

        *)
            alenaal_error "Usage: alenaal_table [header|row|separator|footer|double] [content...]"
            return 1
            ;;
    esac
}
