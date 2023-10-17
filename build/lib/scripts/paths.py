"""
Exposes common paths useful for manipulating datasets and generating figures.

"""
from pathlib import Path

# Absolute path to the top level of the repository
root = Path(__file__).resolve().parents[2].absolute()

# Absolute path to the `src` folder
src = root / "src"

# Absolute path to the `src/data` folder (contains datasets)
data = src / "data"

# Path to the plots folder
plots = src / "results" / "plots"

# Path to the 1D spectra
oned_spec = data / "processed" / "oned_spectra"

# Path to the *calibrated* 1D spectra
wave_calibrated = data / "processed" / "wave_calibrated"

# Path to other resources
resources = data / "resources"

# Results
results = src / "results"
