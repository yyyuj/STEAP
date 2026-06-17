#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -j y
#$ -V

SNAKEFILE="${1:?Usage: SGE_cluster.sh <snakefile>}"
shift
snakemake --use-conda -j -s "$SNAKEFILE" --configfile config/config.yml "$@"
