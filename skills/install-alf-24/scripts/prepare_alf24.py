#!/usr/bin/env python3
"""Prepare ALF 2.4, pyALF, and a matching conda environment."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


ALF_BRANCH = "ALF-2.4"
ALF_REPO = "https://git.physik.uni-wuerzburg.de/ALF/ALF.git"
PYALF_REPO = "https://git.physik.uni-wuerzburg.de/ALF/pyALF.git"
PYTHON_PACKAGES = [
    "python=3.10",
    "ipython",
    "jupyterlab",
    "scipy",
    "numpy",
    "matplotlib",
    "h5py",
    "pandas",
    "numba",
    "ipywidgets",
    "ipympl",
    "f90nml",
    "tk",
]


def shlex_join(cmd: list[str]) -> str:
    try:
        import shlex

        return shlex.join(cmd)
    except Exception:
        return " ".join(cmd)


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    dry_run: bool = False,
    capture: bool = False,
) -> subprocess.CompletedProcess[str] | None:
    print(f"+ {shlex_join(cmd)}")
    if dry_run:
        return None
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def fail(message: str, code: int = 2) -> None:
    print(f"\nERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def command_path(name: str) -> str | None:
    if name == "conda" and os.environ.get("CONDA_EXE"):
        return os.environ["CONDA_EXE"]
    return shutil.which(name)


def check_windows() -> None:
    if platform.system() != "Windows":
        return

    wsl = shutil.which("wsl.exe")
    if not wsl:
        fail(
            "Native Windows is not supported for this installer. Install and initialize WSL yourself, "
            "then rerun from a Linux shell inside WSL."
        )

    result = subprocess.run([wsl, "-l", "-q"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw = result.stdout
    try:
        distro_text = raw.decode("utf-16")
    except UnicodeError:
        distro_text = raw.decode(errors="replace")
    distro_text = distro_text.replace("\x00", "")
    distros = [line.strip() for line in distro_text.splitlines() if line.strip()]
    if not distros:
        fail(
            "WSL is present but no ready Linux distro was found. Install and initialize a WSL distro "
            "yourself, then rerun from inside that distro."
        )

    fail(
        "Run this installer from inside a WSL Linux shell, not from native Windows PowerShell or cmd. "
        f"Available WSL distros: {', '.join(distros)}"
    )


def has_linux_library(token: str) -> bool:
    ldconfig = shutil.which("ldconfig")
    if ldconfig:
        result = subprocess.run([ldconfig, "-p"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if token.lower() in result.stdout.lower():
            return True

    candidates = [
        Path("/usr/lib"),
        Path("/usr/lib64"),
        Path("/usr/local/lib"),
        Path("/usr/lib/x86_64-linux-gnu"),
        Path("/opt/homebrew/lib"),
    ]
    patterns = [f"*{token}*.so*", f"*{token}*.dylib*", f"*{token}*.a"]
    for base in candidates:
        if not base.exists():
            continue
        for pattern in patterns:
            if any(base.glob(pattern)):
                return True
    return False


def missing_prerequisites() -> list[str]:
    check_windows()
    missing: list[str] = []

    if not command_path("conda"):
        missing.append("Conda was not found. Install Anaconda or Miniconda yourself and restart the shell.")
    if not command_path("git"):
        missing.append("Git was not found. Install Git yourself.")
    if not command_path("make"):
        missing.append("make was not found. Install your OS build tools yourself.")
    if not (command_path("gfortran") or command_path("ifort")):
        missing.append("No Fortran compiler was found. Install gfortran or ifort yourself.")

    system = platform.system()
    if system == "Linux":
        if not has_linux_library("lapack"):
            missing.append("LAPACK was not found. Install your distribution's LAPACK development package yourself.")
        if not has_linux_library("blas"):
            missing.append("BLAS was not found. Install your distribution's BLAS development package yourself.")
    elif system == "Darwin":
        xcode_select = shutil.which("xcode-select")
        if not xcode_select:
            missing.append("xcode-select was not found. Install Xcode command line tools yourself.")
        else:
            result = subprocess.run(
                [xcode_select, "-p"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            if result.returncode != 0:
                missing.append("Xcode command line tools are not ready. Install them yourself.")

    return missing


def existing_conda_env_names(conda: str) -> set[str]:
    result = run([conda, "env", "list", "--json"], capture=True)
    if result is None:
        return set()
    data = json.loads(result.stdout)
    names: set[str] = set()
    for env_path in data.get("envs", []):
        path = Path(env_path)
        names.add(path.name)
    return names


def choose_env_name(base: str, existing: set[str]) -> str:
    if base not in existing:
        return base
    index = 2
    while f"{base}_{index}" in existing:
        index += 1
    return f"{base}_{index}"


def clone_or_update(repo: str, target: Path, *, dry_run: bool) -> None:
    if target.exists():
        if not (target / ".git").exists():
            fail(f"{target} already exists and is not a Git repository.")
        run(["git", "-C", str(target), "fetch", "origin", ALF_BRANCH], dry_run=dry_run)
        run(["git", "-C", str(target), "checkout", ALF_BRANCH], dry_run=dry_run)
        run(["git", "-C", str(target), "pull", "--ff-only", "origin", ALF_BRANCH], dry_run=dry_run)
        return

    run(["git", "clone", "-b", ALF_BRANCH, repo, str(target)], dry_run=dry_run)


def conda_env_prefix(conda: str, env_name: str) -> Path:
    result = run(
        [conda, "run", "-n", env_name, "python", "-c", "import sys; print(sys.prefix)"],
        capture=True,
    )
    if result is None:
        fail("Cannot determine conda environment prefix during dry-run.")
    return Path(result.stdout.strip())


def write_activation_hooks(prefix: Path, alf_dir: Path, pyalf_dir: Path, *, dry_run: bool) -> None:
    activate_dir = prefix / "etc" / "conda" / "activate.d"
    deactivate_dir = prefix / "etc" / "conda" / "deactivate.d"
    activate_file = activate_dir / "alf24.sh"
    deactivate_file = deactivate_dir / "alf24.sh"

    activate_text = f"""#!/usr/bin/env sh
export ALF_DIR="{alf_dir}"
export PYALF_DIR="{pyalf_dir}"
export _ALF24_OLD_PYTHONPATH="${{PYTHONPATH-}}"
if [ -n "${{PYTHONPATH-}}" ]; then
  export PYTHONPATH="{pyalf_dir}:$PYTHONPATH"
else
  export PYTHONPATH="{pyalf_dir}"
fi
"""
    deactivate_text = """#!/usr/bin/env sh
if [ -n "${_ALF24_OLD_PYTHONPATH+x}" ]; then
  export PYTHONPATH="$_ALF24_OLD_PYTHONPATH"
  unset _ALF24_OLD_PYTHONPATH
fi
unset ALF_DIR
unset PYALF_DIR
"""

    print(f"+ write {activate_file}")
    print(f"+ write {deactivate_file}")
    if dry_run:
        return
    activate_dir.mkdir(parents=True, exist_ok=True)
    deactivate_dir.mkdir(parents=True, exist_ok=True)
    activate_file.write_text(activate_text, encoding="utf-8")
    deactivate_file.write_text(deactivate_text, encoding="utf-8")
    activate_file.chmod(0o755)
    deactivate_file.chmod(0o755)


def verify_python_packages(conda: str, env_name: str, *, dry_run: bool) -> None:
    code = (
        "import f90nml, h5py, ipympl, ipywidgets, matplotlib, numba, numpy, pandas, scipy, tkinter; "
        "print('ALF Python package imports OK')"
    )
    run([conda, "run", "-n", env_name, "python", "-c", code], dry_run=dry_run)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install-dir", help="Directory that will contain ALF/ and pyALF/. Must avoid spaces.")
    parser.add_argument("--env-base", default="ALFDQMC", help="Preferred conda environment name.")
    parser.add_argument("--skip-build", action="store_true", help="Clone and create the conda env without running make.")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan without changing files or environments.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    install_dir_text = args.install_dir
    if not install_dir_text:
        install_dir_text = input("Install ALF 2.4 in which directory? ").strip()
    if not install_dir_text:
        fail("No install directory was provided.")
    if any(ch.isspace() for ch in install_dir_text):
        fail("The install directory contains whitespace. Choose a path without spaces.")

    install_dir = Path(install_dir_text).expanduser().resolve()
    alf_dir = install_dir / "ALF"
    pyalf_dir = install_dir / "pyALF"

    missing = missing_prerequisites()
    if missing:
        print("\nRequired system or subsystem prerequisites are not ready:")
        for item in missing:
            print(f"- {item}")
        print("\nInstall the missing prerequisites yourself, then rerun this script.")
        return 2

    conda = command_path("conda")
    if not conda:
        fail("Conda lookup failed unexpectedly.")

    existing = existing_conda_env_names(conda)
    env_name = choose_env_name(args.env_base, existing)
    if env_name != args.env_base:
        print(f"\nConda environment '{args.env_base}' already exists; using '{env_name}' instead.")
    else:
        print(f"\nUsing conda environment name: {env_name}")

    print(f"Install directory: {install_dir}")
    print(f"ALF directory: {alf_dir}")
    print(f"pyALF directory: {pyalf_dir}")

    if args.dry_run:
        print("\nDry run: no files, repositories, conda environments, or builds will be changed.")
    else:
        install_dir.mkdir(parents=True, exist_ok=True)

    run(
        [conda, "create", "-y", "-n", env_name, "-c", "conda-forge", *PYTHON_PACKAGES],
        dry_run=args.dry_run,
    )
    clone_or_update(ALF_REPO, alf_dir, dry_run=args.dry_run)
    clone_or_update(PYALF_REPO, pyalf_dir, dry_run=args.dry_run)

    if not args.dry_run:
        prefix = conda_env_prefix(conda, env_name)
        write_activation_hooks(prefix, alf_dir, pyalf_dir, dry_run=False)
    else:
        print("+ determine conda environment prefix")
        print("+ write conda activation hooks for ALF_DIR, PYALF_DIR, and PYTHONPATH")

    verify_python_packages(conda, env_name, dry_run=args.dry_run)

    if args.skip_build:
        print("\nSkipping ALF build because --skip-build was supplied.")
    else:
        run(["make"], cwd=alf_dir, dry_run=args.dry_run)
        alf_out = alf_dir / "Prog" / "ALF.out"
        if not args.dry_run and not alf_out.exists():
            fail(f"ALF build finished but {alf_out} was not found.", code=1)

    print("\nALF 2.4 setup summary")
    print(f"- Conda environment: {env_name}")
    print(f"- ALF directory: {alf_dir}")
    print(f"- pyALF directory: {pyalf_dir}")
    print(f"- Activate with: conda activate {env_name}")
    if env_name != args.env_base:
        print(f"- Note: requested base environment '{args.env_base}' was already present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


