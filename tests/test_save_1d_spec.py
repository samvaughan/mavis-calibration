from src.scripts import save_1d_spec as script
import numpy as np
import pytest
from astropy.io import fits

# Some test data we have
filename = "tests/test_data/Photron_ThAr_Red_60s_02.fits"


@pytest.mark.parametrize("filename", [filename])
def test_reading_keywords_gets_correct_values(filename):
    (
        lamp_manufacturer,
        lamp_type,
        ccd,
        exposure_time,
        id_number,
    ) = script._get_keywords_from_fname(filename)

    assert lamp_manufacturer == "Photron"
    assert lamp_type == "ThAr"
    assert ccd == "Red"
    assert exposure_time == 60
    assert id_number == "02"


@pytest.mark.parametrize("filename", [filename])
def test_make_new_1d_fits_file_has_correct_header_keywords(filename):
    # Make a simple array
    oned_spec = np.arange(100)
    (
        lamp_manufacturer,
        lamp_type,
        ccd,
        exposure_time,
        id_number,
    ) = script._get_keywords_from_fname(filename)
    hdu = script._make_new_1d_fits_file(
        oned_spec, lamp_manufacturer, lamp_type, ccd, exposure_time, id_number
    )

    header = hdu.header

    assert header["BRAND"] == lamp_manufacturer
    assert header["LAMP"] == lamp_type
    assert header["CCD"] == ccd
    assert header["EXPTIME"] == exposure_time
    assert header["ID"] == id_number


@pytest.mark.parametrize("filename", [filename])
def test_main_creates_plot_and_spec(filename, tmp_path):
    # Run the main script
    output_plot = tmp_path / "test.png"
    output_1dspec = tmp_path / "test.fits"
    script.main(filename, output_plot, output_1dspec)

    # Test that we get a plot and a 1D spec fil
    assert output_plot.exists()
    assert output_1dspec.exists()


@pytest.mark.parametrize("filename", [filename])
def test_main_makes_a_1d_spec(filename, tmp_path):
    # Run the main script
    output_plot = tmp_path / "test.png"
    output_1dspec = tmp_path / "test.fits"
    script.main(filename, output_plot, output_1dspec)

    spec_hdu = fits.open(output_1dspec)

    assert spec_hdu[0].data.ndim == 1
