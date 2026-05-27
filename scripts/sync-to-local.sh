#!/usr/bin/env bash
# sync-to-local.sh — symlink skills/*/ to ~/.claude/skills/*/
# Idempotent: safe to re-run after pulling new skills.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${REPO_DIR}/skills"
TARGET_DIR="${HOME}/.claude/skills"

if [[ ! -d "${SKILLS_DIR}" ]]; then
  echo "ERROR: ${SKILLS_DIR} not found" >&2
  exit 1
fi

mkdir -p "${TARGET_DIR}"

linked=0
skipped=0
for skill in "${SKILLS_DIR}"/*/; do
  [[ -d "${skill}" ]] || continue
  name="$(basename "${skill}")"
  link="${TARGET_DIR}/${name}"

  if [[ -L "${link}" ]]; then
    rm "${link}"
  elif [[ -e "${link}" ]]; then
    echo "WARN: ${link} exists but is not a symlink — skipping (handle manually)" >&2
    skipped=$((skipped + 1))
    continue
  fi

  ln -s "${skill%/}" "${link}"
  echo "linked: ${name}"
  linked=$((linked + 1))
done

echo ""
echo "Done: ${linked} linked, ${skipped} skipped."
