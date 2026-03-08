#!/usr/bin/env bash
set -euo pipefail

# Agentic Engineering Kit -- Installer
# Copies selected components into a target project and optionally creates
# a .<name>/ directory with symlinks to the canonical rules/, skills/, agents/.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CATALOG="$SCRIPT_DIR/catalog.yaml"

usage() {
    cat <<'EOF'
Usage: install.sh [OPTIONS] [COMPONENT...]

Copy components from the agentic-engineering-kit into your project.

Arguments:
  COMPONENT       One or more component IDs to install (e.g., "constitution").
                  Use --list to see available components.

Options:
  --list                    List all available components and exit.
  --target DIR              Target project directory (default: current directory).
  --setup-platform NAME     Create a .<NAME>/ directory with symlinks to
                            rules/, skills/, and agents/ (e.g., "cursor", "claude").
  --all                     Install all components.
  --force                   Overwrite existing files without prompting.
  --dry-run                 Show what would be done without making changes.
  -h, --help                Show this help message.

Examples:
  ./install.sh --list
  ./install.sh constitution --target ~/my-project
  ./install.sh --all --target ~/my-project
  ./install.sh --setup-platform cursor --target ~/my-project
  ./install.sh --setup-platform claude --target ~/my-project
  ./install.sh constitution --target ~/my-project --setup-platform cursor
EOF
    exit 0
}

# --- YAML parsing (minimal, no external deps) ---

get_components() {
    local ids=()
    local paths=()
    local names=()
    local targets=()
    local current_id="" current_path="" current_name="" current_target="."

    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*id:[[:space:]]*(.*) ]]; then
            if [[ -n "$current_id" ]]; then
                ids+=("$current_id")
                paths+=("$current_path")
                names+=("$current_name")
                targets+=("$current_target")
            fi
            current_id="${BASH_REMATCH[1]}"
            current_id="${current_id#"${current_id%%[![:space:]]*}"}"
            current_path=""
            current_name=""
            current_target="."
        elif [[ "$line" =~ ^[[:space:]]*path:[[:space:]]*(.*) ]]; then
            current_path="${BASH_REMATCH[1]}"
            current_path="${current_path#"${current_path%%[![:space:]]*}"}"
        elif [[ "$line" =~ ^[[:space:]]*name:[[:space:]]*(.*) ]]; then
            current_name="${BASH_REMATCH[1]}"
            current_name="${current_name#"${current_name%%[![:space:]]*}"}"
        elif [[ "$line" =~ ^[[:space:]]*install_target:[[:space:]]*(.*) ]]; then
            current_target="${BASH_REMATCH[1]}"
            current_target="${current_target#"${current_target%%[![:space:]]*}"}"
            current_target="${current_target//\"/}"
        fi
    done < "$CATALOG"

    if [[ -n "$current_id" ]]; then
        ids+=("$current_id")
        paths+=("$current_path")
        names+=("$current_name")
        targets+=("$current_target")
    fi

    COMPONENT_IDS=("${ids[@]}")
    COMPONENT_PATHS=("${paths[@]}")
    COMPONENT_NAMES=("${names[@]}")
    COMPONENT_TARGETS=("${targets[@]}")
}

list_components() {
    get_components
    echo "Available components:"
    echo ""
    printf "  %-20s %-30s %s\n" "ID" "NAME" "PATH"
    printf "  %-20s %-30s %s\n" "---" "---" "---"
    for i in "${!COMPONENT_IDS[@]}"; do
        printf "  %-20s %-30s %s\n" "${COMPONENT_IDS[$i]}" "${COMPONENT_NAMES[$i]}" "${COMPONENT_PATHS[$i]}"
    done
    echo ""
}

find_component_index() {
    local search_id="$1"
    for i in "${!COMPONENT_IDS[@]}"; do
        if [[ "${COMPONENT_IDS[$i]}" == "$search_id" ]]; then
            echo "$i"
            return 0
        fi
    done
    return 1
}

copy_component() {
    local idx="$1"
    local target_dir="$2"
    local force="$3"
    local dry_run="$4"

    local comp_id="${COMPONENT_IDS[$idx]}"
    local comp_path="${COMPONENT_PATHS[$idx]}"
    local comp_target="${COMPONENT_TARGETS[$idx]}"
    local src="$SCRIPT_DIR/$comp_path"
    local dest_dir="$target_dir"

    if [[ "$comp_target" != "." ]]; then
        dest_dir="$target_dir/$comp_target"
    fi

    if [[ -d "$src" ]]; then
        local dest="$dest_dir/$(basename "$comp_path")"
        if [[ "$dry_run" == "true" ]]; then
            echo "  [dry-run] Would copy directory: $comp_path -> $dest"
            return 0
        fi
        if [[ -d "$dest" && "$force" != "true" ]]; then
            echo "  [skip] Directory already exists: $dest (use --force to overwrite)"
            return 0
        fi
        mkdir -p "$(dirname "$dest")"
        cp -r "$src" "$dest"
        echo "  [installed] $comp_id -> $dest"
    elif [[ -f "$src" ]]; then
        local dest="$dest_dir/$(basename "$comp_path")"
        if [[ "$dry_run" == "true" ]]; then
            echo "  [dry-run] Would copy: $comp_path -> $dest"
            return 0
        fi
        if [[ -f "$dest" && "$force" != "true" ]]; then
            echo "  [skip] File already exists: $dest (use --force to overwrite)"
            return 0
        fi
        mkdir -p "$(dirname "$dest")"
        cp "$src" "$dest"
        echo "  [installed] $comp_id -> $dest"
    else
        echo "  [error] Source not found: $src"
        return 1
    fi
}

# --- Platform setup (generic) ---

create_symlink() {
    local link_path="$1"
    local target_path="$2"
    local dry_run="$3"

    if [[ ! -d "$target_path" ]]; then
        return 0
    fi

    if [[ "$dry_run" == "true" ]]; then
        echo "  [dry-run] Would symlink: $link_path -> $target_path"
        return 0
    fi

    mkdir -p "$(dirname "$link_path")"

    if [[ -L "$link_path" ]]; then
        local existing
        existing="$(readlink "$link_path")"
        if [[ "$existing" == "$target_path" ]]; then
            echo "  [skip] Symlink already correct: $link_path"
            return 0
        fi
        rm "$link_path"
    elif [[ -d "$link_path" ]]; then
        echo "  [skip] Real directory exists at $link_path, not replacing with symlink"
        return 0
    fi

    ln -s "$target_path" "$link_path"
    echo "  [symlink] $link_path -> $target_path"
}

setup_platform() {
    local name="$1"
    local target_dir="$2"
    local dry_run="$3"

    local platform_dir="$target_dir/.$name"
    echo "Setting up .$name/ platform structure in $target_dir ..."

    if [[ "$dry_run" != "true" ]]; then
        mkdir -p "$platform_dir"
    fi

    for subdir in rules skills agents; do
        create_symlink "$platform_dir/$subdir" "$target_dir/$subdir" "$dry_run"
    done

    echo "  .$name/ setup complete."

    # Cross-client .agents/ convention (agentskills.io standard)
    local agents_dir="$target_dir/.agents"
    if [[ ! -d "$agents_dir" || -L "$agents_dir/skills" || ! -e "$agents_dir/skills" ]]; then
        echo "Setting up .agents/ cross-client structure in $target_dir ..."
        if [[ "$dry_run" != "true" ]]; then
            mkdir -p "$agents_dir"
        fi
        for subdir in rules skills; do
            create_symlink "$agents_dir/$subdir" "$target_dir/$subdir" "$dry_run"
        done
        echo "  .agents/ setup complete."
    fi
}

# --- Main ---

main() {
    local target_dir="."
    local platforms=()
    local force="false"
    local dry_run="false"
    local install_all="false"
    local components=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                ;;
            --list)
                list_components
                exit 0
                ;;
            --target)
                target_dir="$2"
                shift 2
                ;;
            --setup-platform)
                platforms+=("$2")
                shift 2
                ;;
            --all)
                install_all="true"
                shift
                ;;
            --force)
                force="true"
                shift
                ;;
            --dry-run)
                dry_run="true"
                shift
                ;;
            -*)
                echo "Error: Unknown option '$1'"
                echo "Run './install.sh --help' for usage."
                exit 1
                ;;
            *)
                components+=("$1")
                shift
                ;;
        esac
    done

    # Resolve target to absolute path
    target_dir="$(cd "$target_dir" 2>/dev/null && pwd)" || {
        echo "Error: Target directory does not exist: $target_dir"
        exit 1
    }

    # Load catalog
    if [[ ! -f "$CATALOG" ]]; then
        echo "Error: catalog.yaml not found at $CATALOG"
        exit 1
    fi
    get_components

    # Determine what to install
    if [[ "$install_all" == "true" ]]; then
        components=("${COMPONENT_IDS[@]}")
    fi

    # Install components
    if [[ ${#components[@]} -gt 0 ]]; then
        echo "Installing components to $target_dir ..."
        for comp in "${components[@]}"; do
            local idx
            idx=$(find_component_index "$comp") || {
                echo "  [error] Unknown component: $comp"
                echo "  Run './install.sh --list' to see available components."
                exit 1
            }
            copy_component "$idx" "$target_dir" "$force" "$dry_run"
        done
        echo ""
    fi

    # Platform setup
    if [[ ${#platforms[@]} -gt 0 ]]; then
        for p in "${platforms[@]}"; do
            setup_platform "$p" "$target_dir" "$dry_run"
            echo ""
        done
    fi

    # If nothing was requested, show help
    if [[ ${#components[@]} -eq 0 && ${#platforms[@]} -eq 0 ]]; then
        echo "Nothing to do. Specify components to install or use --setup-platform."
        echo "Run './install.sh --help' for usage."
        exit 1
    fi

    echo "Done."
}

main "$@"
