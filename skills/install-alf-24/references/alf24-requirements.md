# ALF 2.4 Requirements Reference

This reference is distilled from the requested source material: the "Part I. Just run it" Requirements section in `ALF_Tutorial-2.4.pdf` and the full `ALF_Tutorial-2.4_README.md`.

## Source-Derived Requirements

- Use the ALF-2.4 branches for both ALF and pyALF.
- Avoid folder names containing spaces because the installation scripts do not support them.
- pyALF needs Python, Jupyter, and the Python packages SciPy, NumPy, matplotlib, f90nml, h5py, pandas, numba, tkinter, ipywidgets, and ipympl.
- Add the pyALF directory to `PYTHONPATH`.
- ALF itself needs BLAS/LAPACK, `make`, and a Fortran 2003-compatible compiler such as `gfortran` or `ifort`.
- Linux package names commonly include `gfortran`, `liblapack-dev` or `lapack-devel`, and `make`, depending on the distribution.
- macOS needs Xcode command line tools and a Fortran compiler.
- Windows users should use Windows Subsystem for Linux and then follow the Linux-style instructions inside WSL.

## Skill Policy

This skill may create a conda environment, clone/update the ALF and pyALF repositories, configure conda activation hooks, and build ALF. It must not automatically install Conda, WSL, OS package-manager packages, Xcode tools, compilers, BLAS/LAPACK, or other system/subsystem prerequisites.

