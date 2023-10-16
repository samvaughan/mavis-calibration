import numpy as np
import pytest
from src.scripts import apply_wavelength_calibration as wavecal
from astropy.io import fits

oned_spec_filename = "tests/test_data/Photron_ThAr_Red_60s_02_1dspec.fits"


@pytest.mark.parametrize("oned_spec_filename", [oned_spec_filename])
def test_spectrum_has_correct_wavelength_calibration(oned_spec_filename, tmp_path):
    output_plot = tmp_path / "test_wavecal.png"
    output_1dspec = tmp_path / "test_wavecal.fits"
    wavecal.main(oned_spec_filename, output_1dspec, output_plot)

    # Assert that we have the correct WCS
    hdu = fits.open(output_1dspec)
    header = hdu[0].header
    if header["CCD"] == "Red":
        red_WCS = [2048.0, 0.5185891473977, 6781.932617188]
        assert np.allclose(
            [hdu[0].header["CRPIX1"], hdu[0].header["CDELT1"], hdu[0].header["CRVAL1"]],
            red_WCS,
        )
