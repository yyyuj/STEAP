#!/bin/bash
exec "$(dirname "$0")/SGE_cluster.sh" cellect-h-magma.snakefile "$@"
