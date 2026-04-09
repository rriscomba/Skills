#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/skills" && pwd)"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"

install_from_zip() {
    local zip_path="$1"

    if [[ ! -f "$zip_path" ]]; then
        echo "Error: archivo no encontrado: ${zip_path}" >&2
        exit 1
    fi

    mkdir -p "${CLAUDE_SKILLS_DIR}"
    unzip -o "$zip_path" -d "${CLAUDE_SKILLS_DIR}" > /dev/null
    skill_name="$(unzip -Z1 "$zip_path" | head -1 | tr -d '/')"
    echo "Instalado: ${skill_name} → ${CLAUDE_SKILLS_DIR}/${skill_name}"
}

install_from_name() {
    local skill_name="$1"
    local src="${SKILLS_DIR}/${skill_name}"

    if [[ ! -d "$src" ]]; then
        echo "Error: skill '${skill_name}' no encontrado en ${SKILLS_DIR}" >&2
        exit 1
    fi

    mkdir -p "${CLAUDE_SKILLS_DIR}"
    cp -r "${src}" "${CLAUDE_SKILLS_DIR}/${skill_name}"
    echo "Instalado: ${skill_name} → ${CLAUDE_SKILLS_DIR}/${skill_name}"
}

if [[ $# -eq 0 ]]; then
    # Instalar todos los skills desde la carpeta skills/
    for skill_dir in "${SKILLS_DIR}"/*/; do
        install_from_name "$(basename "$skill_dir")"
    done
elif [[ "$1" == *.zip ]]; then
    install_from_zip "$1"
else
    install_from_name "$1"
fi
