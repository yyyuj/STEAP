# STEAP

**S**ingle cell **T**ype **E**nrichment **A**nalysis for **P**henotypes (**STEAP**) integrates single-cell RNA-seq specificity data with GWAS summary statistics to identify cell types enriched for genetic association with a phenotype.

STEAP extends [CELLECT](https://github.com/perslab/CELLECT) with additional post-processing and supports three complementary enrichment methods:

| Method | Reference | Snakefile |
|--------|-----------|-----------|
| **S-LDSC** | [Finucane et al., 2015](https://www.nature.com/articles/ng.3404) | `cellect-ldsc.snakefile` |
| **MAGMA** | [de Leeuw et al., 2015](https://doi.org/10.1371/journal.pcbi.1004219) | `cellect-magma.snakefile` |
| **H-MAGMA** | [Sey et al., 2020](https://doi.org/10.1038/s41593-020-0603-0) | `cellect-h-magma.snakefile` |

After enrichment analysis, STEAP provides post-processing for:

- Gene Set Enrichment Analysis (GSEA)
- Cell-type correlation
- Expression specificity (ES) gene correlation

![pipeline](https://github.com/erwinerdem/STEAP/blob/master/pipeline.png)

---

## Table of contents

- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Installation (native conda)](#installation-native-conda)
- [Singularity / Apptainer container](#singularity--apptainer-container)
- [Configuration](#configuration)
- [Tutorial: PGC depression GWAS](#tutorial-pgc-depression-gwas)
- [Running the pipeline](#running-the-pipeline)
- [Post-processing](#post-processing)
- [Project structure](#project-structure)
- [Python environments](#python-environments)
- [Troubleshooting](#troubleshooting)
- [Contact](#contact)

---

## Requirements

| Component | Details |
|-----------|---------|
| **OS** | Linux x86_64 (native or container) |
| **Conda** | Miniconda or Anaconda (native install only) |
| **Git LFS** | Required for reference data and CELLECT submodules |
| **Memory / disk** | Depends on number of ES matrices and GWAS; LDSC precomputation is the most resource-intensive step |
| **Optional** | Singularity ≥ 3.0 or Apptainer (for container workflow) |
| **Optional** | Sun Grid Engine (SGE) cluster access |

---

## Quick start

Choose one installation path:

### Option A — Singularity / Apptainer (recommended for clusters and teaching)

Best when you want a reproducible environment without managing conda on the host.

```bash
git clone https://github.com/erwinerdem/STEAP.git
cd STEAP
# Pull pre-built image (recommended) or build locally — see below
singularity pull --name steap_container_sif/steap_container.sif library://roshchupkin/steap/steap:2.0
bash steap_container_sif/setup_host_dirs.sh  # one-time host setup
# edit $HOME/STEAP/config/config.yml and add GWAS files to $HOME/STEAP/gwas/
bash steap_container_sif/cell_type_sif.sh    # run enrichment analysis
```

See [steap_container_sif/README.md](steap_container_sif/README.md) for full container documentation.

### Option B — Native conda install

Best for development or when Singularity is unavailable.

```bash
git clone https://github.com/erwinerdem/STEAP.git
bash STEAP/install.sh
conda activate steap
snakemake --use-conda -j -s cellect-ldsc.snakefile --configfile config/config.yml
```

---

## Installation (native conda)

### Step 1: Install Miniconda

The pipeline is managed through conda environments. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) if it is not already available:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
rm Miniconda3-latest-Linux-x86_64.sh
```

### Step 2: Clone and install STEAP

```bash
git clone https://github.com/erwinerdem/STEAP.git
bash STEAP/install.sh
conda activate steap
cd STEAP
```

`install.sh` must be run from the **parent** of the cloned repository (not from inside `STEAP/`). It performs the following:

1. Clones [CELLECT](https://github.com/perslab/CELLECT) (with git submodules) via git LFS
2. Merges CELLECT into the STEAP directory structure
3. Creates the `steap` conda environment from `environment_steap.yml`
4. Creates the `munge_ldsc` conda environment from `ldsc/environment_munge_ldsc.yml`

After installation, work from inside the `STEAP/` directory for all pipeline commands.

---

## Singularity / Apptainer container

The container image ships with **all Python and conda environments pre-built**. You do not need to copy Python or conda folders from outside the image.

| Path in image | Purpose |
|---------------|---------|
| `/opt/miniconda/envs/steap` | Main pipeline (Python 3.9, Snakemake) |
| `/opt/miniconda/envs/munge_ldsc` | GWAS munging (Python 2) |
| `/opt/snakemake-conda` | Snakemake rule environments (`cellectpy3`, `cellectpy27`) |
| `/STEAP` | Pipeline code, reference data, default config |

**Pull pre-built image** (recommended for most users):

```bash
singularity pull --name steap_container_sif/steap_container.sif library://roshchupkin/steap/steap:2.0
# Apptainer: apptainer pull --name steap_container_sif/steap_container.sif library://roshchupkin/steap/steap:2.0
```

Replace `2.0` with the tag that matches your STEAP release. You still need this git clone for the wrapper scripts in `steap_container_sif/`.

**Build locally** (on Linux with `--fakeroot` or root):

```bash
bash build_steap_container/build.sh
singularity test steap_container_sif/steap_container.sif
```

**Publish to Sylabs Library** (maintainers, after build and test):

```bash
singularity remote login SylabsCloud
singularity push steap_container_sif/steap_container.sif library://roshchupkin/steap/steap:TAG
```

**Run**:

```bash
bash steap_container_sif/setup_host_dirs.sh
bash steap_container_sif/cell_type_sif.sh
```

| Document | Description |
|----------|-------------|
| [steap_container_sif/README.md](steap_container_sif/README.md) | User guide: bind mounts, scripts, troubleshooting |
| [build_steap_container/build_steap_singularity_steps.txt](build_steap_container/build_steap_singularity_steps.txt) | Build reference for administrators |

---

## Configuration

All pipeline parameters are defined in [`config/config.yml`](config/config.yml). Paths may be absolute or relative to the STEAP working directory. Environment variables (including `~`) are **not** expanded.

### Key parameters

| Parameter | Description |
|-----------|-------------|
| `BASE_OUTPUT_DIR` | Output root; results are written to `CELLECT-LDSC` and `CELLECT-MAGMA` subdirectories |
| `SPECIFICITY_INPUT` | List of ES matrices (`id`, `path`); each `id` must be unique, no double underscores |
| `GWAS_SUMSTATS` | List of munged GWAS files (`id`, `path`); `.sumstats.gz` format |
| `HMAGMA_ANNOT` | Gene annotation file for H-MAGMA |
| `ANALYSIS_TYPE` | Enable `prioritization`, `conditional`, `heritability`, etc. |
| `WINDOW_DEFINITION` | Window size (kb) for mapping gene specificity to SNPs |
| `CONDITIONAL_INPUT` | Annotations for conditional analysis (when enabled) |
| `HERITABILITY_INPUT` | Annotations for heritability estimation (LDSC only) |

For typical analyses, edit `SPECIFICITY_INPUT`, `GWAS_SUMSTATS`, `BASE_OUTPUT_DIR`, and `ANALYSIS_TYPE`. Leave `LDSC_CONST` and `MAGMA_CONST` unchanged unless you have a specific reason to modify reference data paths.

When using the container, edit the host copy at `$HOME/STEAP/config/config.yml` (created by `setup_host_dirs.sh`).

---

## Tutorial: PGC depression GWAS

This walkthrough uses the public PGC + UK Biobank depression GWAS as an example.

### 1. Download summary statistics

```bash
wget -O gwas/PGC_UKB_depression.txt \
  https://datashare.is.ed.ac.uk/bitstream/handle/10283/3203/PGC_UKB_depression_genome-wide.txt \
  --no-check-certificate
```

### 2. Munge GWAS

Summary statistics must be converted to LDSC-compatible format using [`mtag_munge.py`](https://github.com/pascaltimshel/ldsc/blob/d869cfd1e9fe1abc03b65c00b8a672bd530d0617/mtag_munge.py).

**Native install:**

```bash
conda activate munge_ldsc
python2 ldsc/mtag_munge.py \
  --sumstats gwas/PGC_UKB_depression.txt \
  --merge-alleles data/ldsc/w_hm3.snplist \
  --a1 A1 --a2 A2 --snp MarkerName --p P \
  --N-cas 170756 --N-con 329443 \
  --signed-sumstats LogOR,0 --frq Freq \
  --out gwas/PGC_UKB_depression
conda deactivate
```

**Container:** edit parameters in `steap_container_sif/munge_sif.sh`, then run:

```bash
bash steap_container_sif/munge_sif.sh
```

Column names differ per GWAS. See [timshel-2020 munge examples](https://github.com/perslab/timshel-2020/blob/master/src/prep-gwas_munge/README-cmds_munge_sumstats.txt) for additional commands.

The output file `gwas/PGC_UKB_depression.sumstats.gz` is used as pipeline input.

### 3. Prepare expression specificity (ES) matrices

ES matrices quantify cell-type-specific gene expression. Generate them with [CELLEX](https://github.com/perslab/CELLEX#setup). Example notebooks are available in [cellex-notebooks](https://github.com/erwinerdem/cellex-notebooks).

Place ES matrix files in `esmu/` (or another path) and reference them under `SPECIFICITY_INPUT` in `config/config.yml`.

### 4. Configure and run

The default [`config/config.yml`](config/config.yml) is preconfigured for the PGC depression example. Adjust `BASE_OUTPUT_DIR`, `SPECIFICITY_INPUT`, and `GWAS_SUMSTATS` for your analysis, then run the pipeline (see below).

---

## Running the pipeline

Activate the `steap` environment before running Snakemake (native install):

```bash
conda activate steap
```

Run each enrichment method separately. Order does not matter, but all three are typically run:

```bash
snakemake --use-conda -j <N_CORES> -s cellect-ldsc.snakefile    --configfile config/config.yml
snakemake --use-conda -j <N_CORES> -s cellect-magma.snakefile   --configfile config/config.yml
snakemake --use-conda -j <N_CORES> -s cellect-h-magma.snakefile --configfile config/config.yml
```

Replace `<N_CORES>` with the number of parallel jobs (e.g. `8`). Snakemake creates per-rule conda environments automatically on first run (native install).

### Sun Grid Engine (SGE)

On SGE clusters, submit jobs with:

```bash
qsub SGE_cluster_ldsc.sh
qsub SGE_cluster_magma.sh
qsub SGE_cluster_h-magma.sh
```

These scripts wrap `SGE_cluster.sh`, which runs Snakemake with `--use-conda`. Ensure the `steap` environment is available in the job environment (e.g. via module load or conda activation in your cluster profile).

### Singularity / Apptainer

```bash
bash steap_container_sif/cell_type_sif.sh
```

This runs all three snakefiles sequentially inside the container with correct conda activation and `--conda-prefix /opt/snakemake-conda`.

### Useful Snakemake options

| Flag | Purpose |
|------|---------|
| `--dry-run` | Show planned jobs without executing |
| `--unlock` | Clear stale locks after interrupted runs |
| `--until <rule>` | Run pipeline up to a specific rule |
| `--rerun-incomplete` | Re-run jobs with incomplete outputs |

---

## Post-processing

After enrichment analysis, use the example notebook for downstream analysis:

- [`notebooks/depression_example.ipynb`](notebooks/depression_example.ipynb) — GSEA, correlation, and visualization

Alternatively, use the web-based [STEAP post-processing Appyter](https://appyters.maayanlab.cloud/#/STEAP_post_processing_analysis) by uploading `prioritization.csv` output files.

Post-processing scripts live in [`scripts/`](scripts/):

| Script | Purpose |
|--------|---------|
| `convert_output_to_dataframe.py` | Parse pipeline outputs into DataFrames |
| `gene_set_enrichment_analysis.py` | GSEA |
| `calculate_es_correlation.py` | ES gene correlation |
| `calculate_beta_correlation.py` | Cell-type beta correlation |
| `circosplot.py` / `upsetplot.py` | Visualization |

---

## Project structure

```
STEAP/
├── cellect-ldsc.snakefile          # S-LDSC enrichment workflow
├── cellect-magma.snakefile         # MAGMA enrichment workflow
├── cellect-h-magma.snakefile       # H-MAGMA enrichment workflow
├── config/config.yml               # Main pipeline configuration
├── environment_steap.yml           # Conda env for Snakemake orchestration
├── install.sh                      # Native installation script
├── scripts/                        # Post-processing Python scripts
├── notebooks/                      # Analysis notebooks
├── gwas/                           # GWAS input (munged .sumstats.gz)
├── esmu/                           # Expression specificity matrices
├── out/                            # Pipeline output
├── data/                           # Reference data (LDSC, MAGMA, gene coords)
├── ldsc/                           # LDSC submodule (cloned by install.sh)
├── envs/                           # Per-rule conda env specs (from CELLECT)
├── build_steap_container/          # Singularity image definition and build
│   ├── steap_container.def
│   └── build.sh
├── steap_container_sif/              # Container runtime scripts
│   ├── setup_host_dirs.sh
│   ├── cell_type_sif.sh
│   ├── munge_sif.sh
│   └── container_env.sh
├── SGE_cluster*.sh                 # Cluster submission wrappers
└── tests/                          # Unit tests for post-processing utilities
```

---

## Python environments

STEAP uses multiple conda environments. This is intentional — LDSC requires Python 2, while most other tools use Python 3.

| Environment | Python | Created by | Used for |
|-------------|--------|------------|----------|
| `steap` | 3.9 | `install.sh` | Snakemake orchestration |
| `munge_ldsc` | 2.7 | `install.sh` | GWAS munging (`mtag_munge.py`) |
| `cellectpy3` | 3.6 | Snakemake (`--use-conda`) | Most pipeline rules |
| `cellectpy27` | 2.7 | Snakemake (`--use-conda`) | LDSC rules |

**Native install:** Snakemake creates `cellectpy3` and `cellectpy27` on first run in `.snakemake/conda/`.

**Container:** All four environment types are pre-built. Rule environments are at `/opt/snakemake-conda` (not under `.snakemake/conda`).

Always activate the correct environment before running commands manually:

```bash
conda activate steap        # pipeline
conda activate munge_ldsc   # GWAS munging
```

---

## Troubleshooting

### Native install

| Problem | Solution |
|---------|----------|
| `git lfs` errors | Run `git lfs install` and ensure LFS is configured |
| Conda env creation fails | Check network; retry `conda env create -f environment_steap.yml` |
| Snakemake lock error | Run `snakemake --unlock -s <snakefile> --configfile config/config.yml` |
| Wrong Python version | Activate `steap` or `munge_ldsc` before running commands |

### Container

| Problem | Solution |
|---------|----------|
| Wrong Python / missing packages | Use wrapper scripts; do not run bare `singularity exec ... python` |
| Read-only filesystem on `.snakemake` | Run `setup_host_dirs.sh` to create the bind mount |
| Snakemake downloads conda at runtime | Rebuild image; verify `/opt/snakemake-conda` is populated (`singularity test`) |
| Copied conda from host breaks paths | Never copy `.snakemake/conda` from a host install; rebuild the image |

See [steap_container_sif/README.md](steap_container_sif/README.md) for additional container troubleshooting.

### Running tests

```bash
conda activate steap
python -m pytest tests/
```

---

## Contact

Erwin Erdem — erwin.erdem@outlook.com  
Dr. Gennady Roshchupkin, PhD — g.roshchupkin@erasmusmc.nl  
Prof. dr. Steven Kushner, PhD — s.kushner@erasmusmc.nl
