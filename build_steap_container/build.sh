#!/bin/bash
# One-shot build of the STEAP Singularity/Apptainer image.
# Requires: singularity or apptainer with --fakeroot (or root).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEF_FILE="${SCRIPT_DIR}/steap_container.def"
OUTPUT_SIF="${REPO_ROOT}/steap_container_sif/steap_container.sif"

if command -v apptainer >/dev/null 2>&1; then
    RUNTIME=apptainer
elif command -v singularity >/dev/null 2>&1; then
    RUNTIME=singularity
else
    echo "ERROR: neither apptainer nor singularity found in PATH" >&2
    exit 1
fi

echo "Using ${RUNTIME} to build ${OUTPUT_SIF}"
mkdir -p "$(dirname "${OUTPUT_SIF}")"

cd "${SCRIPT_DIR}"
${RUNTIME} build --fakeroot "${OUTPUT_SIF}" "${DEF_FILE}"

echo ""
echo "Build complete: ${OUTPUT_SIF}"
echo "Verify:  ${RUNTIME} test ${OUTPUT_SIF}"
echo "Setup:   bash ${REPO_ROOT}/steap_container_sif/setup_host_dirs.sh"
