"""
Given a 1D spectrum which has been wavelength calibrated, measure the flux from a series of emission lines.

Steps:
    * Read in our wavelength calibrated 1D spectrum.
    * Read in a table file which defines the arc regions we want to sum over.
    * Cut our spectrum around each line and sum the flux in each region.
    * Save a postage stamp of the spectrum around each line.
    * Save a table with these measurements.

ToDo:
    * Maybe could fit gaussians rather than just summing?
"""

from astropy.io import fits
import numpy as np
import pandas as pd
from astropy.wcs import WCS
import argparse
import matplotlib.pyplot as plt


def measure_flux(wavelength, spectrum, linelist):
    fluxes = np.zeros(len(linelist))
    for index, row in linelist.iterrows():
        wave_low, wave_high = row.line_start, row.line_end
        mask = (wavelength > wave_low) & (wavelength < wave_high)
        fluxes[index] = np.sum(spectrum[mask])

    return fluxes


def main(input_spectrum, output_table, table_filename, output_plot_filename):
    # Load the file and get the CCD
    hdu = fits.open(input_spectrum)
    spectrum = hdu[0].data
    wcs = WCS(hdu[0].header)
    wavelength = wcs.pixel_to_world_values(np.arange(hdu[0].header["NAXIS1"]))

    # Now get the appropriate table file
    linelist = pd.read_csv(table_filename)

    linelist["Wavelength"] = np.mean(
        [linelist["line_start"], linelist["line_end"]], axis=0
    )

    # Get the nearest pixel to the centre of each emission line
    pixel_numbers = np.argmin(
        np.abs(wavelength[:, None] - linelist["Wavelength"].values[None, :]), axis=0
    )
    linelist["pixel"] = pixel_numbers

    # Measure the fluxes
    fluxes = measure_flux(wavelength, spectrum, linelist)

    # Now sort out the units
    exposure_time = int(hdu[0].header["EXPTIME"])
    number_of_fibres = 61
    adu_per_second = fluxes / exposure_time / number_of_fibres

    linelist["Flux"] = adu_per_second

    # Now save the final file to a .csv file
    linelist.loc[:, ["pixel", "Wavelength", "Flux"]].to_csv(output_table, index=False)

    # Finally, make a plot showing the locations of each line
    fig, ax = plt.subplots(constrained_layout=True)
    ax.plot(wavelength, spectrum, c="k")
    for index, row in linelist.iterrows():
        ax.axvspan(
            row["line_start"],
            row["line_end"],
            alpha=0.6,
            facecolor="r",
            linewidth=2.0,
            linestyle="dashed",
        )
    ax.set_xlabel("Wavelength (Angstrom)")
    ax.set_ylabel("Flux")
    fig.savefig(output_plot_filename, bbox_inches="tight")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_spectrum")
    parser.add_argument("output_table")
    parser.add_argument("table_filename")
    parser.add_argument("output_plot")

    args = parser.parse_args()
    input_spectrum = args.input_spectrum
    output_table = args.output_table
    table_filename = args.table_filename
    output_plot = args.output_plot
    # input_spectrum = paths.wave_calibrated / "Photron_ThAr_Red_60s_02_1dspec_cal.fits"
    # output_table = paths.results / "Photron_ThAr_Red_60s_02_1dspec_cal_fluxes.csv"
    # table_filename = paths.resources / "linelist_ThAr_Red.csv"
    main(input_spectrum, output_table, table_filename, output_plot)
