"""
Take an image from the Spector CCD and turn it into a 1D spectrum by summing along the spatial direction.

Steps:
    * Read the file.
    * Subtract the bias from the image.
    * Get the exposure time and the arc lamp name.
    * Sum along the spatial dimension to go from 2D to 1D.
    * Save a plot of this spectrum for QC.
    * Save a 1D fits file with appropriate header keywords.
"""
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from pathlib import Path
import argparse

# smk = snakemake  # noqa


def _get_keywords_from_fname(filename):
    filename = Path(filename)
    lamp_manufacturer = filename.stem.split("_")[0]
    lamp_type = filename.stem.split("_")[1]
    ccd = filename.stem.split("_")[2]
    exposure_time = int(filename.stem.split("_")[-2].strip("s"))
    id_number = filename.stem.split("_")[-1]

    return lamp_manufacturer, lamp_type, ccd, exposure_time, id_number


def _make_new_1d_fits_file(
    oned_spec, lamp_manufacturer, lamp_type, ccd, exposure_time, id_number
):
    hdu_1D = fits.PrimaryHDU(oned_spec)
    hdu_1D.header["BRAND"] = lamp_manufacturer
    hdu_1D.header["LAMP"] = lamp_type
    hdu_1D.header["CCD"] = ccd
    hdu_1D.header["EXPTIME"] = exposure_time
    hdu_1D.header["ID"] = id_number

    return hdu_1D


def main(filename, dark_filename, output_plot, output_1dspec):
    # Get some keywords from the filenames
    (
        lamp_manufacturer,
        lamp_type,
        ccd,
        exposure_time,
        id_number,
    ) = _get_keywords_from_fname(filename)

    hdu = fits.open(filename)

    dark_hdu = fits.open(dark_filename)
    dark_image = dark_hdu[0].data

    # Subtract off the dark frame
    oned_spec = np.sum(hdu[0].data - dark_image, axis=0)

    # Make our output plot
    fig, ax = plt.subplots(constrained_layout=True)
    ax.plot(oned_spec, c="k")
    ax.set_xlabel("Pixel")
    ax.set_ylabel("Counts")
    ax.set_title(f"{lamp_manufacturer} {lamp_type} ({ccd}): {exposure_time}s exposure")
    fig.savefig(output_plot)

    # Make a new fits file
    hdu_1D = _make_new_1d_fits_file(
        oned_spec, lamp_manufacturer, lamp_type, ccd, exposure_time, id_number
    )
    print(f"\tSaving the file to {output_1dspec}...")
    hdu_1D.writeto(output_1dspec, overwrite=True)
    print("\tDone!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("dark_filename")
    parser.add_argument("output_1dspec")
    parser.add_argument("output_plot")

    args = parser.parse_args()
    filename = Path(args.filename)
    dark_filename = Path(args.dark_filename)
    output_1dspec = Path(args.output_1dspec)
    output_plot = Path(args.output_plot)

    # Run the script
    print(f"\tRunning on {filename}...")
    main(filename, dark_filename, output_plot, output_1dspec)
