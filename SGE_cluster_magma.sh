#!/bin/bash
exec "$(dirname "$0")/SGE_cluster.sh" cellect-magma.snakefile "$@"
