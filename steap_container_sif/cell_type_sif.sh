#!/bin/bash
# Run the STEAP enrichment pipeline inside the Singularity/Apptainer container.
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

${RUNTIME} exec \
    -B "${HOST_STEAP}/gwas:/STEAP/gwas" \
    -B "${HOST_STEAP}/out:/STEAP/out" \
    -B "${HOST_STEAP}/config:/STEAP/config" \
    -B "${HOST_STEAP}/.snakemake:/STEAP/.snakemake" \
    "${SIF}" /bin/bash -c "
    source /etc/steap/container_env.sh
    steap_activate
    cd /STEAP
    snakemake --unlock \${SNAKEMAKE_FLAGS} -j -s cellect-ldsc.snakefile --configfile config/config.yml
    snakemake \${SNAKEMAKE_FLAGS} -j -s cellect-ldsc.snakefile --configfile config/config.yml
    snakemake \${SNAKEMAKE_FLAGS} -j -s cellect-magma.snakefile --configfile config/config.yml || \
    snakemake \${SNAKEMAKE_FLAGS} -j -s cellect-magma.snakefile --configfile config/config.yml
    snakemake \${SNAKEMAKE_FLAGS} -j -s cellect-h-magma.snakefile --configfile config/config.yml || \
    snakemake \${SNAKEMAKE_FLAGS} -j -s cellect-h-magma.snakefile --configfile config/config.yml
"
