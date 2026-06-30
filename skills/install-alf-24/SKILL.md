---
name: install-alf-24
description: Install ALF 2.4 and pyALF ALF-2.4, prepare a conda environment for ALF DQMC work, choose a non-conflicting environment name starting from ALFDQMC, and handle operating-system prerequisites. Use when the user asks to install, set up, configure, build, or verify ALF 2.4, pyALF, or an ALFDQMC conda environment on Linux, macOS, or Windows/WSL.
---

# Install ALF 2.4

## Overview

Install ALF 2.4 and pyALF from the ALF-2.4 branches, prepare the Python/Jupyter conda environment, and verify the setup without silently changing system-level prerequisites.

Use `scripts/prepare_alf24.py` for the actual installation workflow. Read `references/alf24-requirements.md` when you need the source-derived dependency details.

## Required User Prompt

Before running the installer, ask the user which directory ALF 2.4 should be installed in. Tell the user that ALF installation scripts do not support paths containing spaces, so the chosen directory must avoid spaces.

Use `ALFDQMC` as the default conda environment base name unless the user requests another base name. If `ALFDQMC` already exists, the installer must choose the next available name, such as `ALFDQMC_2`, and report the actual name to the user.

## Guardrails

- Do not install required system software or subsystems automatically.
- If Conda, Git, Make, a Fortran compiler, BLAS/LAPACK, Xcode command line tools, WSL, or a Linux/Unix-like shell is missing, stop and tell the user what they need to install themselves.
- On native Windows, prefer WSL. If no WSL distro is available, tell the user to install and initialize WSL themselves; do not run `wsl --install`.
- Avoid installation directories containing spaces.
- Ask before using networked commands if the current environment requires approval.

## Workflow

1. Ask for the install directory.
2. If working on Windows, verify that the user is operating inside a ready WSL/Linux shell. If not, explain the WSL requirement and stop.
3. Check prerequisites without installing them.
4. Run the helper script from this skill:

```bash
python scripts/prepare_alf24.py --install-dir /path/without/spaces --env-base ALFDQMC
```

5. Watch the script output for the final conda environment name. Report that name clearly, especially when it differs from `ALFDQMC`.
6. Verify the final summary includes the ALF directory, pyALF directory, and activation command.
7. As a final check, run all cells of every notebook in `pyALF/Notebooks`, including `minimal_ALF_run.ipynb`, `parallel_tempering.ipynb`, and any other `.ipynb` file. Treat any failed notebook execution as a failed installation check. Fix the configuration or installation if any notebook fails to run, until all notebooks execute successfully.

## Common Commands

Dry-run the plan without creating the environment, cloning repositories, or building ALF:

```bash
python scripts/prepare_alf24.py --install-dir /path/without/spaces --dry-run
```

Skip the ALF build only when the user explicitly asks for clone/env preparation without compilation:

```bash
python scripts/prepare_alf24.py --install-dir /path/without/spaces --skip-build
```

After installation, activate the environment:

```bash
conda activate ALFDQMC
```

Use the actual environment name printed by the installer if it selected a fallback name.

Run every pyALF notebook as the final installation check:

```bash
conda activate ALFDQMC
cd "$PYALF_DIR/Notebooks"
find . -name '*.ipynb' -print0 | sort -z | xargs -0 -n 1 jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1
```

Use the actual environment name printed by the installer if it selected a fallback name.


