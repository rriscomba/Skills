#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/skills" && pwd)"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"

install_skill() {
    local skill_name="$1"
    local src="${SKILLS_DIR}/${skill_name}"

    if [[ ! -d "$src" ]]; then
        echo "Error: skill '${skill_name}' not found in ${SKILLS_DIR}" >&2
        exit 1
    fi

    mkdir -p "${CLAUDE_SKILLS_DIR}"
    cp -r "${src}" "${CLAUDE_SKILLS_DIR}/${skill_name}"
    echo "Installed: ${skill_name} → ${CLAUDE_SKILLS_DIR}/${skill_name}"
}

if [[ $# -eq 0 ]]; then
    # Install all skills
    for skill_dir in "${SKILLS_DIR}"/*/; do
        skill_name="$(basename "$skill_dir")"
        install_skill "$skill_name"
    done
else
    install_skill "$1"
fi
