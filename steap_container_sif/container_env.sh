#!/bin/bash
# Shared environment for STEAP Singularity/Apptainer containers.
# Sourced by runtime wrapper scripts inside the container.

STEAP_CONDA_PREFIX="${STEAP_CONDA_PREFIX:-/opt/snakemake-conda}"
STEAP_ROOT="${STEAP_ROOT:-/STEAP}"

steap_activate() {
    # shellcheck disable=SC1091
    source /opt/miniconda/etc/profile.d/conda.sh
    conda activate steap
}

steap_activate_munge() {
    # shellcheck disable=SC1091
    source /opt/miniconda/etc/profile.d/conda.sh
    conda activate munge_ldsc
}

# Snakemake flags: rule-level conda envs live at a fixed, image-baked prefix.
SNAKEMAKE_FLAGS="--use-conda --conda-prefix ${STEAP_CONDA_PREFIX}"
