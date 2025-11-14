#!/usr/bin/env bash

# =============================================================================
# MESSAGE FUNCTIONS LIBRARY
# 
# A collection of colorized, icon-based message functions for bash scripts.
# Provides consistent styling for different types of user feedback.
# =============================================================================

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
    echo -e "\e[1;95m❤\e[0m \e[1;97m${@}\e[0m"
}

# -----------------------------------------------------------------------------
# Function: message_debug
# Description: Shows debug information with subtle styling for technical details
# Usage: message_debug "Debug information"
# Parameters: $@ - Debug message content
# Returns: Formatted debug message to stdout
# -----------------------------------------------------------------------------
message_debug() {
    echo -e "\e[1;36m∅\e[0m \e[0;36m${@}\e[0m"
}

# -----------------------------------------------------------------------------
# Function: message_warning
# Description: Presents warning messages with high visibility and caution icon
# Usage: message_warning "Warning message text"
# Parameters: $@ - Warning content requiring user attention
# Returns: Formatted warning message to stdout
# -----------------------------------------------------------------------------
message_warning() {
    echo -e "\e[1;93m!\e[0m \e[1;93m${@}\e[0m"
}

# -----------------------------------------------------------------------------
# Function: message_error
# Description: Displays error messages with urgent styling and clear failure icon
# Usage: message_error "Error description"
# Parameters: $@ - Error message content
# Returns: Formatted error message to stdout
# -----------------------------------------------------------------------------
message_error() {
    echo -e "\e[1;91m✗\e[0m \e[1;91m${@}\e[0m"
}

# -----------------------------------------------------------------------------
# Function: message_info
# Description: Shows informational messages with neutral styling and info icon
# Usage: message_info "Information text"
# Parameters: $@ - Informational content
# Returns: Formatted info message to stdout
# -----------------------------------------------------------------------------
message_info() {
    echo -e "\e[1;94m→\e[0m \e[0;97m${@}\e[0m"
}

# -----------------------------------------------------------------------------
# Function: message_suggestion
# Description: Offers suggestions with friendly styling and idea bulb icon
# Usage: message_suggestion "Suggestion text"
# Parameters: $@ - Suggested action or advice
# Returns: Formatted suggestion message to stdout
# -----------------------------------------------------------------------------
message_suggestion() {
    echo -e "\e[1;96m»\e[0m \e[0;96m${@}\e[0m"
}

# -----------------------------------------------------------------------------
# Function: message_success
# Description: Announces successful operations with positive green styling
# Usage: message_success "Success message"
# Parameters: $@ - Success description
# Returns: Formatted success message to stdout
# -----------------------------------------------------------------------------
message_success() {
    echo -e "\e[1;92m✓\e[0m \e[1;92m${@}\e[0m"
}

# -----------------------------------------------------------------------------
# Function: message_note
# Description: Displays important notes with attention-grabbing yellow styling
# Usage: message_note "Note content"
# Parameters: $@ - Note text
# Returns: Formatted note message to stdout
# -----------------------------------------------------------------------------
message_note() {
    echo -e "\e[1;93m!\e[0m \e[0;93m${@}\e[0m"
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
# Function: message_table_header
# Description: Displays table headers with clean, professional formatting
# Usage: message_table_header "Header Title"
# Parameters: $@ - Header text content
# Returns: Formatted table header to stdout
# -----------------------------------------------------------------------------
message_table_header() {
    echo -e "\e[1;95m┌─────────────────────────────────────────────────────────┐\e[0m"
    echo -e "\e[1;95m│\e[1;97m ${@}\e[0m"
    echo -e "\e[1;95m└─────────────────────────────────────────────────────────┘\e[0m"
}

# -----------------------------------------------------------------------------
# Function: message_step
# Description: Shows progress steps with numbered icons for multi-step processes
# Usage: message_step 1 "Step description"
# Parameters: 
#   $1 - Step number (integer)
#   $2 - Step description text
# Returns: Formatted step message to stdout
# -----------------------------------------------------------------------------
message_step() {
    local step_number="$1"
    local step_description="$2"
    local icons=("🔸" "🔹" "🔶" "🔷" "🟣" "🟠" "🔴" "🟢" "🔵" "🟡")
    local icon_index=$(( (step_number - 1) % ${#icons[@]} ))
    
    echo -e "\e[1;97m${icons[$icon_index]} Step ${step_number}:\e[0m \e[0;97m${step_description}\e[0m"
}

# Usage:
#   Start a background process with a message:
#     sleep 10 &
#     spinner "Processing..."
# Usage:
#   Start a command with output redirected to /dev/null and a message:
#     your_command > /dev/null &
#     spinner "Processing..."
spinner() {
    # Accepts a message as input
    local info="$1"

    # Get the process ID of the background process
    local pid=$!

    # Set the delay for the spinner animation
    local delay=0.5

    # Define the spinner characters
    local spinstr='|/-\'

    # Loop until the background process is running
    while kill -0 $pid 2>/dev/null; do
        # Rotate the spinner characters
        local temp=${spinstr#?}
        printf " [%c]  %s" "$spinstr" "$info"
        local spinstr=$temp${spinstr%"$temp"}

        # Add backspace characters to reset the cursor position
        sleep $delay
        local reset="\r"

        # Reset the cursor position for the next spinner update
        printf $reset
    done

    # Clear the entire line once the process is complete
    printf "\r%-${COLUMNS}s\r" " "
}
