#!/bin/bash
# Munge GWAS summary statistics inside the Singularity/Apptainer container.
#
# Edit the parameters below for your GWAS before running.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIF="${STEAP_SIF:-${SCRIPT_DIR}/steap_container.sif}"
HOST_STEAP="${STEAP_HOST_DIR:-${HOME}/STEAP}"

# --- edit these for your GWAS ---
SUMSTATS_FILE="XXX.sumstats.txt"
OUTPUT_PREFIX="XXX"
N_CASE=170756
N_CONTROL=329443
# --------------------------------

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
    exit 1
fi

mkdir -p "${HOST_STEAP}/gwas"

${RUNTIME} exec \
    -B "${HOST_STEAP}/gwas:/STEAP/gwas" \
    "${SIF}" /bin/bash -c "
    source /etc/steap/container_env.sh
    steap_activate_munge
    python2 /STEAP/ldsc/mtag_munge.py \
        --sumstats /STEAP/gwas/${SUMSTATS_FILE} \
        --merge-alleles /STEAP/data/ldsc/w_hm3.snplist \
        --a1 A1 \
        --a2 A2 \
        --snp MarkerName \
        --p P \
        --N-cas ${N_CASE} \
        --N-con ${N_CONTROL} \
        --signed-sumstats LogOR,0 \
        --frq Freq \
        --out /STEAP/gwas/${OUTPUT_PREFIX}
"

echo "Munged output: ${HOST_STEAP}/gwas/${OUTPUT_PREFIX}.sumstats.gz"
