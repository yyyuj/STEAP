# STEAP Singularity / Apptainer container

This directory contains runtime scripts and configuration for running STEAP inside a Singularity or Apptainer container. The image includes all conda environments pre-built — **you do not need to copy Python or conda folders from outside the image**.

For a high-level overview, see the [main README](../README.md#singularity--apptainer-container).

---

## Contents

| File | Purpose |
|------|---------|
| `steap_container.sif` | Container image (built by `build_steap_container/build.sh`; not in git) |
| `container_env.sh` | Shared conda prefix and Snakemake flags (installed to `/etc/steap/` in image) |
| `setup_host_dirs.sh` | One-time host directory setup and config seeding |
| `cell_type_sif.sh` | Run full enrichment pipeline (LDSC + MAGMA + H-MAGMA) |
| `munge_sif.sh` | Munge raw GWAS summary statistics |

---

## Prerequisites

- Pre-built `steap_container.sif` — [pull from Sylabs Library](#pull-pre-built-image) or [build locally](#building-the-image)
- Singularity ≥ 3.0 or Apptainer on the execution host
- Linux x86_64
- Writable home directory for bind-mounted data

---

## Quick start

```bash
# 1. One-time setup: creates $HOME/STEAP/{gwas,out,config,.snakemake}
bash steap_container_sif/setup_host_dirs.sh

# 2. Configure your analysis
vim $HOME/STEAP/config/config.yml
# Add munged GWAS files to $HOME/STEAP/gwas/

# 3. Run enrichment analysis
bash steap_container_sif/cell_type_sif.sh
```

Results appear under `$HOME/STEAP/out/` according to `BASE_OUTPUT_DIR` in your config.

---

## Pull pre-built image

The recommended way to obtain `steap_container.sif` is from the [Sylabs Cloud Library](https://cloud.sylabs.io/library/roshchupkin/steap/steap). From the repository root:

```bash
singularity pull --name steap_container_sif/steap_container.sif library://roshchupkin/steap/steap:2.0
```

Use `apptainer pull` instead of `singularity pull` if Apptainer is your runtime. Replace `2.0` with the tag that matches your STEAP version (see `%labels` in `build_steap_container/steap_container.def`).

Verify after download:

```bash
singularity test steap_container_sif/steap_container.sif
```

---

## Building the image

Build locally only if you cannot pull from the library or need a custom image. Image building requires Linux, network access, and `--fakeroot` (or root). It cannot be built on Windows or macOS directly.

From the repository root:

```bash
bash build_steap_container/build.sh
```

Verify:

```bash
singularity test steap_container_sif/steap_container.sif
# or: apptainer test steap_container_sif/steap_container.sif
```

Detailed build instructions: [build_steap_container/build_steap_singularity_steps.txt](../build_steap_container/build_steap_singularity_steps.txt)

### What gets baked into the image

| Location | Contents |
|----------|----------|
| `/opt/miniconda/envs/steap` | Python 3.9, Snakemake, pipeline dependencies |
| `/opt/miniconda/envs/munge_ldsc` | Python 2.7, LDSC munging tools |
| `/opt/snakemake-conda` | `cellectpy3` and `cellectpy27` rule environments |
| `/STEAP` | Pipeline code, reference data, example config |
| `/etc/steap/container_env.sh` | Runtime environment configuration |

Snakemake rule environments are created during the image build with `--conda-create-envs-only` and stored at a fixed prefix (`/opt/snakemake-conda`). This avoids the fragile workflow of copying `.snakemake/conda` from a host install.

---

## Host directory layout

After `setup_host_dirs.sh`, the host directory structure is:

```
$HOME/STEAP/
├── config/
│   └── config.yml          # Pipeline configuration (editable)
├── gwas/
│   └── *.sumstats.gz       # Munged GWAS input files
├── out/
│   └── CELLECT-*/          # Pipeline output (created at runtime)
└── .snakemake/             # Writable Snakemake metadata (locks, logs)
```

Override the default location:

```bash
export STEAP_HOST_DIR=/path/to/my_steap_data
bash steap_container_sif/setup_host_dirs.sh
```

---

## Bind mounts

Wrapper scripts automatically bind-mount host directories into the container:

| Host path | Container path | Purpose |
|-----------|----------------|---------|
| `$HOME/STEAP/gwas` | `/STEAP/gwas` | GWAS input files |
| `$HOME/STEAP/out` | `/STEAP/out` | Pipeline output |
| `$HOME/STEAP/config` | `/STEAP/config` | Configuration |
| `$HOME/STEAP/.snakemake` | `/STEAP/.snakemake` | Writable Snakemake metadata |

Conda environments are **not** bind-mounted. They live inside the read-only image at `/opt/miniconda` and `/opt/snakemake-conda`.

Override the image path:

```bash
export STEAP_SIF=/path/to/steap_container.sif
bash steap_container_sif/cell_type_sif.sh
```

---

## Running individual workflows

### Full enrichment pipeline

`cell_type_sif.sh` runs all three snakefiles in sequence:

1. `cellect-ldsc.snakefile` (S-LDSC)
2. `cellect-magma.snakefile` (MAGMA)
3. `cellect-h-magma.snakefile` (H-MAGMA)

Each snakefile is retried once on failure (useful for transient cluster issues).

### GWAS munging

Edit the parameters at the top of `munge_sif.sh`:

```bash
SUMSTATS_FILE="my_gwas.txt"
OUTPUT_PREFIX="my_gwas"
N_CASE=170756
N_CONTROL=329443
```

Place the raw summary statistics file in `$HOME/STEAP/gwas/`, then:

```bash
bash steap_container_sif/munge_sif.sh
```

Output: `$HOME/STEAP/gwas/${OUTPUT_PREFIX}.sumstats.gz`

### Manual container execution

For advanced use, open an interactive shell:

```bash
singularity exec \
  -B $HOME/STEAP/gwas:/STEAP/gwas \
  -B $HOME/STEAP/out:/STEAP/out \
  -B $HOME/STEAP/config:/STEAP/config \
  -B $HOME/STEAP/.snakemake:/STEAP/.snakemake \
  steap_container_sif/steap_container.sif /bin/bash
```

Inside the container:

```bash
source /etc/steap/container_env.sh
steap_activate
cd /STEAP
snakemake ${SNAKEMAKE_FLAGS} -j 4 -s cellect-ldsc.snakefile --configfile config/config.yml
```

---

## Environment variables

Set on the host before calling wrapper scripts:

| Variable | Default | Description |
|----------|---------|-------------|
| `STEAP_SIF` | `steap_container_sif/steap_container.sif` | Path to container image |
| `STEAP_HOST_DIR` | `$HOME/STEAP` | Host data directory for bind mounts |

Set inside the container (via `/etc/steap/container_env.sh`):

| Variable | Value | Description |
|----------|-------|-------------|
| `STEAP_CONDA_PREFIX` | `/opt/snakemake-conda` | Snakemake rule conda environments |
| `STEAP_ROOT` | `/STEAP` | Pipeline root directory |
| `SNAKEMAKE_FLAGS` | `--use-conda --conda-prefix /opt/snakemake-conda` | Flags for all Snakemake calls |

---

## Troubleshooting

### Wrong Python version or missing packages

**Symptom:** `ModuleNotFoundError`, or Python 3.8+ when Python 2 is expected.

**Cause:** Running Python without activating the correct conda environment.

**Fix:** Always use the wrapper scripts, or inside the container:

```bash
source /opt/miniconda/etc/profile.d/conda.sh
conda activate steap        # for pipeline
conda activate munge_ldsc   # for GWAS munging
```

Do **not** run:

```bash
singularity exec steap_container.sif python3 scripts/foo.py   # wrong
```

### Read-only file system (`.snakemake`)

**Symptom:** `OSError: [Errno 30] Read-only file system` under `.snakemake`.

**Cause:** The `.snakemake` directory is not bind-mounted from the host.

**Fix:**

```bash
bash steap_container_sif/setup_host_dirs.sh
```

### Snakemake tries to create conda environments at runtime

**Symptom:** Long conda download during pipeline run; or failure to create envs.

**Cause:** Image was not built correctly, or `--conda-prefix` is missing.

**Fix:**

1. Rebuild: `bash build_steap_container/build.sh`
2. Verify: `singularity test steap_container_sif/steap_container.sif`
3. Ensure wrapper scripts source `/etc/steap/container_env.sh`

### Copied conda from host install

**Symptom:** Broken shebangs, `bad interpreter`, env activation failures.

**Cause:** Conda environments contain hardcoded absolute paths. Copying `.snakemake/conda` from a host install into the container will not work.

**Fix:** Rebuild the image. Never copy conda folders from outside.

### Container image not found

```bash
singularity pull --name steap_container_sif/steap_container.sif library://roshchupkin/steap/steap:2.0
# or: bash build_steap_container/build.sh
```

---

## For administrators

- Build definition: `build_steap_container/steap_container.def`
- One-shot build: `build_steap_container/build.sh`
- Image version label: `2.0` (see `%labels` in def file)
- Container help text: `singularity run steap_container.sif`
- Sylabs Library: `library://roshchupkin/steap/steap:TAG`

After building and passing `singularity test`, publish a release:

```bash
singularity remote login SylabsCloud
singularity push steap_container_sif/steap_container.sif library://roshchupkin/steap/steap:TAG
```

Use a `TAG` that matches the image version (for example `2.0`).

When distributing to students, provide:

1. The pull command above (or a local copy of `steap_container.sif`)
2. Link to this README
3. Instruction to run `setup_host_dirs.sh` once, then edit config and run `cell_type_sif.sh`

No conda or Python setup is required on student machines beyond Singularity/Apptainer.
