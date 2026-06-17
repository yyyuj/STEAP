# -*- coding: utf-8 -*-

# Some overlapping functionality
include: "rules/common_func1.smk"

########################################################################################
################################### VARIABLES ##########################################
########################################################################################

# Where all the output will be saved
BASE_OUTPUT_DIR = os.path.join( config['BASE_OUTPUT_DIR'], "CELLECT-H-MAGMA")

# More overlapping functionality
include: "rules/common_func2.smk"

ANNOT_DIR = os.path.abspath(config['MAGMA_CONST']['ANNOT_DIR'])
ANNOT_FILE = os.path.join(ANNOT_DIR, config['HMAGMA_ANNOT'])

include: "rules/magma_common.smk"
