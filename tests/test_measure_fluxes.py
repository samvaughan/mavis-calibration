from src.scripts import measure_fluxes
import pytest
import pandas as pd
import numpy as np

oned_spec_calibrated_filename = (
    "tests/test_data/Photron_ThAr_Red_60s_02_1dspec_cal.fits"
)
table_filename = "tests/test_data/linelist_ThAr_Red.csv"


@pytest.mark.parametrize(
    "oned_spec_calibrated_filename, table_filename",
    [(oned_spec_calibrated_filename, table_filename)],
)
def test_measure_fluxes_gives_table_with_correct_column_names(
    oned_spec_calibrated_filename, table_filename, tmp_path
):
    output_table = tmp_path / "test.csv"
    output_plot = tmp_path / "plot.png"
    # Run the script
    measure_fluxes.main(
        oned_spec_calibrated_filename, output_table, table_filename, output_plot
    )

    # read in the output file
    df = pd.read_csv(output_table)
    assert np.all(df.columns == ["pixel", "Wavelength", "Flux"])


def test_measure_flux_of_known_gaussian():
    wavelength = np.arange(0, 100)
    # Make a fake Gaussian with mean=50, sigma=2 pixels
    # This should sum to 1
    sigma = 2
    mean = 50
    normalisation = 1.0 / np.sqrt(2 * np.pi * sigma**2)
    spectrum = normalisation * np.exp(-0.5 * ((wavelength - mean) / sigma) ** 2)

    # Make a fake linelist
    linelist = pd.DataFrame(dict(line_start=40, line_end=60), index=[0])

    fluxes = measure_fluxes.measure_flux(wavelength, spectrum, linelist)

    assert np.allclose(fluxes, [1])
