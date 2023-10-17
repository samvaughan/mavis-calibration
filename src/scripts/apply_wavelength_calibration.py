"""
Take a red or blue spectrum and copy over a wavelength calibration from a properly reduced Hector image.

Steps:
    * Read in our 1D spec
    * Load the appropriate red or blue wavelength calibration from some reduced files
    * Make another QC plot,

TODO:
    * Add some lines of known wavelength to test this.
"""
from astropy.io import fits
from astropy.wcs import WCS
import argparse
from pathlib import Path


def main(
    onedspec_file,
    wavelength_calibrated_output_file,
):
    # Open the spectrum
    hdu = fits.open(onedspec_file)
    spec = hdu[0].data
    ccd = hdu[0].header["CCD"]
    naxis = hdu[0].header["NAXIS1"]

    # Make a WCS with the appropriate values
    wcs = WCS(naxis=1)
    wcs.wcs.crpix = [2048]
    wcs.NAXIS = naxis
    if ccd == "Blue":
        wcs.wcs.cdelt = [0.5470085470085]
        wcs.wcs.crval = [4799.726495726]
    elif ccd == "Red":
        wcs.wcs.cdelt = [0.5185891473977]
        wcs.wcs.crval = [6781.932617188]

    # Add this to the fits header
    hdu[0].header.extend(wcs.to_header())
    hdu.writeto(wavelength_calibrated_output_file, overwrite=True)

    # # Now make a QC plot
    # wcs = WCS(hdu[0].header)
    # wave = wcs.pixel_to_world_values(np.arange(naxis))
    # fig, ax = plt.subplots(constrained_layout=True)
    # ax.plot(wave, spec, c="k")
    # ax.set_xlabel("Wavelength (Angstroms)")
    # ax.set_ylabel("Counts")
    # fig.savefig(output_plot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("onedspec_file")
    parser.add_argument("wavelength_calibrated_output_file")

    args = parser.parse_args()
    onedspec_file = args.onedspec_file
    wavelength_calibrated_output_file = args.wavelength_calibrated_output_file

    onedspec_file = Path(onedspec_file)
    wavelength_calibrated_output_file = Path(wavelength_calibrated_output_file)

    # Run the script
    main(onedspec_file, wavelength_calibrated_output_file)
