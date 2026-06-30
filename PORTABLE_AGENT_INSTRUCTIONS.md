# Portable Agent Instructions: Install ALF 2.4

Use these instructions in agents that do not support OpenAI/Codex `SKILL.md` skills.

## Purpose

Install ALF 2.4 and pyALF from the `ALF-2.4` branches, create a conda environment for ALF DQMC work, and run all pyALF notebooks as the final check.

## Required Behavior

1. Ask the user which directory ALF 2.4 should be installed in.
2. Require a path with no spaces. ALF installation scripts do not support folder names containing spaces.
3. Use `ALFDQMC` as the default conda environment base name.
4. If `ALFDQMC` already exists, automatically choose the next available name such as `ALFDQMC_2`, `ALFDQMC_3`, and tell the user the actual name.
5. Do not automatically install required system software or subsystems.
6. If Conda, Git, Make, a Fortran compiler, BLAS/LAPACK, Xcode command line tools, WSL, or a Linux/Unix-like shell is missing, stop and tell the user what they need to install manually.
7. On Windows, require WSL and run from inside a WSL Linux shell. Do not run `wsl --install`.

## Repository Files

The reusable helper script is:

```text
skills/install-alf-24/scripts/prepare_alf24.py
```

The source-derived requirements reference is:

```text
skills/install-alf-24/references/alf24-requirements.md
```

## Installation Command

From the repository root, run:

```bash
python skills/install-alf-24/scripts/prepare_alf24.py --install-dir /path/without/spaces --env-base ALFDQMC
```

Replace `/path/without/spaces` with the user's chosen installation directory.

For a dry run:

```bash
python skills/install-alf-24/scripts/prepare_alf24.py --install-dir /path/without/spaces --dry-run
```

For clone/environment preparation without building ALF:

```bash
python skills/install-alf-24/scripts/prepare_alf24.py --install-dir /path/without/spaces --skip-build
```

## Final Notebook Check

After installation, activate the actual conda environment name printed by the helper script:

```bash
conda activate ALFDQMC
cd "$PYALF_DIR/Notebooks"
find . -name '*.ipynb' -print0 | sort -z | xargs -0 -n 1 jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1
```

Use the actual environment name if the helper selected a fallback such as `ALFDQMC_2`.

Treat any failed notebook execution as a failed installation check. This includes `minimal_ALF_run.ipynb`, `parallel_tempering.ipynb`, and every other `.ipynb` file under `pyALF/Notebooks`.

## Success Report

When finished, report:

- The conda environment name.
- The ALF directory.
- The pyALF directory.
- Whether ALF was built.
- Whether all notebooks executed successfully.
- Any manual prerequisite the user still needs to install.
