#!/bin/bash
# One-time host setup: create bind-mount directories and seed config from the image.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIF="${STEAP_SIF:-${SCRIPT_DIR}/steap_container.sif}"
HOST_STEAP="${STEAP_HOST_DIR:-${HOME}/STEAP}"

if command -v apptainer >/dev/null 2>&1; then
    RUNTIME=apptainer
elif command -v singularity >/dev/null 2>&1; then
    RUNTIME=singularity
else
    echo "ERROR: neither apptainer nor singularity found in PATH" >&2
    exit 1
fi

if [[ ! -f "${SIF}" ]]; then
    echo "ERROR: container image not found: ${SIF}" >&2
    echo "Build it first: bash build_steap_container/build.sh" >&2
    exit 1
fi

mkdir -p "${HOST_STEAP}/gwas" "${HOST_STEAP}/out" "${HOST_STEAP}/config" "${HOST_STEAP}/.snakemake"

if [[ ! -f "${HOST_STEAP}/config/config.yml" ]]; then
    echo "Copying default config from container to ${HOST_STEAP}/config/"
    ${RUNTIME} exec \
        -B "${HOST_STEAP}/config:/STEAP/host_config" \
        "${SIF}" cp -r /STEAP/config/. /STEAP/host_config/
fi

echo "Host directories ready at: ${HOST_STEAP}"
echo "  config:  ${HOST_STEAP}/config/config.yml"
echo "  gwas:    ${HOST_STEAP}/gwas/"
echo "  out:     ${HOST_STEAP}/out/"
echo ""
echo "Next: edit config.yml, add GWAS files, then run:"
echo "  bash steap_container_sif/cell_type_sif.sh"
