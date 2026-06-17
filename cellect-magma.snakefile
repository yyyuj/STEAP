# -*- coding: utf-8 -*-

# Some overlapping functionality
include: "rules/common_func1.smk"

########################################################################################
################################### VARIABLES ##########################################
########################################################################################

# Where all the output will be saved
BASE_OUTPUT_DIR = os.path.join(config['BASE_OUTPUT_DIR'], "CELLECT-MAGMA")

# More overlapping functionality
include: "rules/common_func2.smk"

ANNOT_FILE = os.path.join(BASE_OUTPUT_DIR, "precomputation/NCBI37_1kgp_up" + str(WINDOWSIZE_KB) + "kb_down" + str(WINDOWSIZE_KB) + "kb.genes.annot")

include: "rules/magma_common.smk"


###################################### CREATE ANNOTATIONS ######################################

rule make_annot:
	'''
	Annotates genes (maps SNPs to genes).
	'''
	input:
		SNPLOC_FILE,
		GENELOC_FILE
	output:
		ANNOT_FILE
	conda:
		"envs/cellectpy3.yml"
	shell:
		"echo \"$(cat magma/bin/README.txt)\"; {MAGMA_EXEC} --annotate window = {WINDOWSIZE_KB},{WINDOWSIZE_KB} \
		--snp-loc {SNPLOC_FILE} \
		--gene-loc {GENELOC_FILE} \
		--out {BASE_OUTPUT_DIR}/precomputation/NCBI37_1kgp_up{WINDOWSIZE_KB}kb_down{WINDOWSIZE_KB}kb"
