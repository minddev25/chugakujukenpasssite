#!/bin/bash
#
# Article Management Shell Script (ma.sh)
# Wrapper script for ma.py to generate and update HTML pages
# for the chugakujukenpasssite from article.md files
#

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print usage information
usage() {
    cat << EOF
Article Management Script (ma.sh)

Usage: $0 [OPTIONS] [ARTICLE_FILE]

Options:
    -h, --help          Show this help message
    -o, --output FILE   Specify output HTML filename
    -u, --update        Update existing HTML page instead of creating new
    -l, --list          List all article markdown files
    -n, --new TITLE     Create a new article.md template with the given title
    -v, --validate      Validate article.md format before processing

Arguments:
    ARTICLE_FILE        Path to article markdown file (default: article.md)

Environment Variables:
    OPENAI_API_KEY      OpenAI API key for content generation (required)

Examples:
    # Generate HTML from default article.md
    $0

    # Generate HTML from specific article file
    $0 my-article.md

    # Update existing HTML page
    $0 -u article.md

    # Create new article template
    $0 -n "新しい勉強法"

    # List all articles
    $0 -l

EOF
}

# Check if Python 3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_message "$RED" "Error: Python 3 is not installed."
        exit 1
    fi
}

# Check if OpenAI API key is set
check_api_key() {
    if [ -z "$OPENAI_API_KEY" ]; then
        print_message "$RED" "Error: OPENAI_API_KEY environment variable is not set."
        print_message "$YELLOW" "Please set it with: export OPENAI_API_KEY='your-api-key'"
        exit 1
    fi
}

# Check if required Python packages are installed
check_dependencies() {
    python3 -c "import openai" 2>/dev/null || {
        print_message "$YELLOW" "Warning: openai package not installed."
        print_message "$YELLOW" "Installing openai package..."
        pip3 install openai || {
            print_message "$RED" "Error: Failed to install openai package."
            print_message "$YELLOW" "Please install manually: pip3 install openai"
            exit 1
        }
    }
}

# Create a new article template
create_template() {
    local title="$1"
    local filename="${SCRIPT_DIR}/article.md"
    
    if [ -f "$filename" ]; then
        print_message "$YELLOW" "Warning: article.md already exists."
        read -p "Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_message "$YELLOW" "Aborted."
            exit 0
        fi
    fi
    
    cat > "$filename" << EOF
---
title: ${title}
description: 
category: 
tags: []
references: []
---

# ${title}

## はじめに

ここに記事の内容を書きます。

## ポイント1

説明文...

### 詳細

詳細な説明...

## ポイント2

説明文...

## まとめ

まとめの内容...
EOF
    
    print_message "$GREEN" "✓ Created article template: $filename"
    print_message "$YELLOW" "Please edit the file and add your content."
}

# Validate article.md format
validate_article() {
    local article_file="$1"
    
    if [ ! -f "$article_file" ]; then
        print_message "$RED" "Error: Article file not found: $article_file"
        exit 1
    fi
    
    print_message "$YELLOW" "Validating article format..."
    
    # Check if file has content
    if [ ! -s "$article_file" ]; then
        print_message "$RED" "Error: Article file is empty"
        exit 1
    fi
    
    # Check for frontmatter
    if ! grep -q "^---" "$article_file"; then
        print_message "$YELLOW" "Warning: No YAML frontmatter found. Consider adding metadata."
    fi
    
    print_message "$GREEN" "✓ Article format looks good"
}

# Main script logic
main() {
    local article_file="article.md"
    local output_file=""
    local update_mode=false
    local list_mode=false
    local validate_mode=false
    local new_title=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -u|--update)
                update_mode=true
                shift
                ;;
            -l|--list)
                list_mode=true
                shift
                ;;
            -n|--new)
                new_title="$2"
                shift 2
                ;;
            -v|--validate)
                validate_mode=true
                shift
                ;;
            -*)
                print_message "$RED" "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                article_file="$1"
                shift
                ;;
        esac
    done
    
    # Check prerequisites
    check_python
    
    # Handle new template creation
    if [ -n "$new_title" ]; then
        create_template "$new_title"
        exit 0
    fi
    
    # Handle list mode
    if [ "$list_mode" = true ]; then
        check_dependencies
        python3 "$SCRIPT_DIR/ma.py" --list
        exit 0
    fi
    
    # Construct full path to article file for validation
    local temp_article_file="$article_file"
    if [[ "$temp_article_file" != /* ]]; then
        temp_article_file="${SCRIPT_DIR}/${temp_article_file}"
    fi
    
    # Validate if requested (can be done without API key)
    if [ "$validate_mode" = true ]; then
        validate_article "$temp_article_file"
        exit 0
    fi
    
    # Check API key for generation/update operations
    check_api_key
    check_dependencies
    
    # Construct full path to article file
    if [[ "$article_file" != /* ]]; then
        article_file="${SCRIPT_DIR}/${article_file}"
    fi
    
    # Build Python command
    local py_cmd="python3 $SCRIPT_DIR/ma.py"
    
    if [ -n "$output_file" ]; then
        py_cmd="$py_cmd --output $output_file"
    fi
    
    if [ "$update_mode" = true ]; then
        py_cmd="$py_cmd --update"
    fi
    
    py_cmd="$py_cmd $(basename "$article_file")"
    
    # Run Python script
    print_message "$GREEN" "Processing article..."
    cd "$SCRIPT_DIR"
    eval "$py_cmd"
    
    print_message "$GREEN" "✓ Done!"
}

# Run main function
main "$@"
