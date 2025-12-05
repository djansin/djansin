#!/usr/bin/env sh

# Function: yes_no
# Description: Prompts the user for a yes/no response and returns 0 for "yes" and 1 for anything else.
# Arguments:
#   $1: The message to display to the user.
# Returns:
#   0 if the user responds with "yes", 1 for any other response.
# Usage: if yes_no "Do you want to proceed?"; then
#            # Proceed with the operation
#        else
#            # Cancel the operation
#        fi
yes_no() {
    local response=""
    echo -n "$(tput setaf 4)?$(tput sgr0) $1 (y/N)? "
    read response
    case "$response" in
    [yY])
        return 0
        ;;
    *)
        return 1
        ;;
    esac
}

# Function: ask_question
# Description: Prompts the user for an answer to a question.
# Arguments:
#   $1: The question to ask the user.
# Returns:
#   The user's answer.
ask_question() {
    echo -n "$(tput setaf 4)?$(tput sgr0) $1 "
    read answer
    echo "${answer}"
}

# Function: change_ownership
# Description: Changes the ownership of a file or folder and its contents to a specified UID.
# Parameters:
#   $1: Path to the file or folder
#   $2: UID to set as the ownership
# Returns:
#   0: Successful ownership change
#   1: Error in providing path or UID
#   2: Path does not exist
change_ownership() {
    # Check if path and UID are provided
    if [ $# -lt 2 ]; then
        return 1
    fi

    local path=$1
    local uid=$2

    # Check if the path exists
    if [ ! -e "$path" ]; then
        return 2
    fi

    # Change ownership recursively
    chown -R $uid:$uid $path
}

# Function to retrieve the Django version without the patch version
# Usage: django_version=$(get_django_version)
# Returns: Django version number without the patch version (e.g., 4.2)
get_django_version() {
    local version=$(python -m django --version)
    local django_version=$(echo $version | cut -d '.' -f 1,2)
    echo $django_version
}

# Function: convert_dotted_path_to_slash
# Description: Converts a dotted path to a path with slashes.
# Arguments:
#   $1: Dotted path to be converted
# Output: Path with slashes
convert_dotted_path_to_slash() {
    local dotted_path=$1
    local slash_path=$(echo "$dotted_path" | tr '.' '/')
    echo "$slash_path"
}

# Function: convert_slash_path_to_dotted
# Description: Converts a slashed path to a path with dots.
# Arguments:
#   $1: Slashed path to be converted
# Output: Path with dots
convert_slashed_path_to_dot() {
    local slashed_path=$1
    local dot_path=$(echo "$slashed_path" | tr '/' '.')
    echo "$dot_path"
}

# Function: replace_all
# Description: Replaces all occurrences of a search term within a given text
#              and prints whether the operation was successful.
# Arguments:
#   $1: The input text (can be multi-line)
#   $2: The search term to look for
#   $3: The replacement string
# Output:
#   - A success or failure message
#   - The modified text if replacements occurred
replace_all() {
    local text="$1"
    local search="$2"
    local replace="$3"

    # Perform the replacement on all occurrences of the search term
    local new_text
    new_text="${text//$search/$replace}"

    # Check whether any replacement actually happened
    if [[ "$new_text" == "$text" ]]; then
        return 1
    else
        echo "${new_text}"
        return 0
    fi
}

# -----------------------------------------------------------------------------
# Function: to_lower
# Description:
#   Converts the given string to lowercase.
# Arguments:
#   $1 : Input string
# Output:
#   Prints the lowercase version of the input string
# Example:
#   to_lower "HelloWorld"  # Output: helloworld
# -----------------------------------------------------------------------------
to_lower() {
    local input="$1"
    echo "$input" | awk '{print tolower($0)}'
}

# -----------------------------------------------------------------------------
# Function: to_capitalize
# Description:
#   Capitalizes the first character of the given string, keeping the rest unchanged.
# Arguments:
#   $1 : Input string
# Output:
#   Prints the string with the first character capitalized
# Example:
#   to_capitalize "helloWorld"  # Output: HelloWorld
# -----------------------------------------------------------------------------
to_capitalize(){
    local input="$1"
    echo "$input" | awk '{print toupper(substr($0,1,1)) substr($0,2)}'
}

# -----------------------------------------------------------------------------
# Function: to_snake_case
# Description:
#   Converts a CamelCase or kebab-case string to snake_case.
# Arguments:
#   $1 : Input string in CamelCase or kebab-case
# Output:
#   Prints the string in snake_case format
# Example:
#   to_snake_case "MyAppName"    # Output: my_app_name
#   to_snake_case "my-app-name"  # Output: my_app_name
# Implementation:
#   - Replaces hyphens with underscores
#   - Inserts underscores between lowercase/uppercase and uppercase/lowercase transitions
#   - Converts all letters to lowercase
# -----------------------------------------------------------------------------
to_snake_case() {
    local input="$1"
    printf '%s' "$input" \
        | sed -e 's/-/_/g' \
              -e 's/\([a-z0-9]\)\([A-Z]\)/\1_\2/g' \
              -e 's/\([A-Z]\)\([A-Z][a-z]\)/\1_\2/g' \
        | tr '[:upper:]' '[:lower:]'
}
