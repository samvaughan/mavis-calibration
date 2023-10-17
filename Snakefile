"""
A Snakefile to run our scripts on every input exposure
"""
import numpy as np
from pathlib import Path
import glob
import pandas as pd


def _get_wildcards_from_filenames(filename):
    stem = filename.stem
    if stem.startswith("Dark"):
        pass
    manufacturer, lamp_type, ccd_colour, exposure_time, id_number = stem.split("_")
    return manufacturer, lamp_type, ccd_colour, exposure_time, id_number


all_files = list(glob.glob("src/data/raw/*/*.fits"))
# Sort these to be alphabetical
all_files.sort()

# Read in all of our wildcards from these files
all_manufacturers = []
all_lamp_types = []
all_ID_numbers = []
all_exposure_times = []
all_CCD_colours = []
for file in all_files:
    file = Path(file)
    if file.stem.startswith("Dark"):
        continue
    (
        manufacturer,
        lamp_type,
        ccd_colour,
        exposure_time,
        id_number,
    ) = _get_wildcards_from_filenames(Path(file))
    all_manufacturers.extend([manufacturer])
    all_lamp_types.extend([lamp_type])
    all_CCD_colours.extend([ccd_colour])
    all_ID_numbers.extend([id_number])
    all_exposure_times.extend([exposure_time])

# Now make a dataframe of all of these
df = pd.DataFrame(
    data=dict(
        manufacturer=all_manufacturers,
        lamp_type=all_lamp_types,
        ccd_colour=all_CCD_colours,
        ID_number=all_ID_numbers,
        exposure_time=all_exposure_times,
    )
)
df["has_dark"] = True


# Mark things we don't have darks for
mask_1 = (
    (df.manufacturer == "GS") & (df.exposure_time == "10s") & (df.ccd_colour == "Red")
)
mask_2 = (
    (df.manufacturer == "Newport")
    & (df.exposure_time == "90s")
    & (df.ccd_colour == "Red")
    & (df.lamp_type == "HgAr")
)
mask_3 = (
    (df.manufacturer == "Newport")
    & (df.exposure_time == "10s")
    & (df.ccd_colour == "Blue")
    & (df.lamp_type == "HgAr")
)
mask_4 = (
    (df.manufacturer == "Newport")
    & (df.exposure_time == "10s")
    & (df.ccd_colour == "Blue")
    & (df.lamp_type == "HgNe")
)
mask_5 = (
    (df.manufacturer == "Newport")
    & (df.exposure_time == "60s")
    & (df.ccd_colour == "Blue")
    & (df.lamp_type == "HgNe")
)
mask_6 = (
    (df.manufacturer == "Newport")
    & (df.exposure_time == "600s")
    & (df.ccd_colour == "Blue")
    & (df.lamp_type == "Kr")
)
no_dark_mask = mask_1 | mask_2 | mask_3 | mask_4 | mask_5 | mask_6

df.loc[no_dark_mask, "has_dark"] = False


def get_dark_filename(wildcards):
    mask = (
        (df.manufacturer == f"{wildcards.lamp_manufacturer}")
        & (df.exposure_time == f"{wildcards.exposure_time}")
        & (df.ccd_colour == f"{wildcards.ccd_colour}")
        & (df.lamp_type == f"{wildcards.LampType}")
        & (df.ID_number == f"{wildcards.id_number}")
    )
    assert (
        mask.sum() == 1
    ), "This mask should always only have one True value in it... Check the wildcards!"
    has_dark = df.loc[mask, "has_dark"].values[0]
    if has_dark:
        filename = f"src/data/raw/{wildcards.lamp_manufacturer}_{wildcards.LampType}_{wildcards.ccd_colour}_fits/Dark_{wildcards.ccd_colour}_{wildcards.exposure_time}.fits"
    else:
        filename = "src/data/raw/no_dark.flag"
    return filename


# The Snakemake rules
rule all:
    input:
        results=expand(
            "src/results/{lamp_manufacturer}_{LampType}_{ccd_colour}_{exposure_time}_{id_number}_1dspec_cal_fluxes.csv",
            zip,
            lamp_manufacturer=np.array(df.manufacturer),
            LampType=np.array(df.lamp_type),
            id_number=np.array(df.ID_number),
            exposure_time=np.array(df.exposure_time),
            ccd_colour=np.array(df.ccd_colour),
        ),


rule save_1D_spec:
    input:
        dark_frame=get_dark_filename,
        raw_spectrum="src/data/raw/{lamp_manufacturer}_{LampType}_{ccd_colour}_fits/{lamp_manufacturer}_{LampType}_{ccd_colour}_{exposure_time}_{id_number}.fits",
    output:
        oned_spectrum="src/data/processed/oned_spectra/{lamp_manufacturer}_{LampType}_{ccd_colour}_{exposure_time}_{id_number}_1dspec.fits",
        oned_plot="src/results/plots/oned_spectra/{lamp_manufacturer}_{LampType}_{ccd_colour}_{exposure_time}_{id_number}_plot.png",
    shell:
        "python src/scripts/save_1d_spec.py {input.raw_spectrum} {output.oned_spectrum} {output.oned_plot} --dark_filename {input.dark_frame}"


rule wavelength_calibration:
    input:
        oned_spectrum=rules.save_1D_spec.output.oned_spectrum,
    output:
        wavecal_spectrum="src/data/processed/wave_calibrated/{lamp_manufacturer}_{LampType}_{ccd_colour}_{exposure_time}_{id_number}_1dspec_cal.fits",
    shell:
        "python src/scripts/apply_wavelength_calibration.py {input.oned_spectrum} {output.wavecal_spectrum}"


rule measure_fluxes:
    input:
        wavecal_spectrum=rules.wavelength_calibration.output.wavecal_spectrum,
        linelist_file="src/data/resources/linelist_{LampType}_{ccd_colour}.csv",
    output:
        final_table="src/results/{lamp_manufacturer}_{LampType}_{ccd_colour}_{exposure_time}_{id_number}_1dspec_cal_fluxes.csv",
        output_plot="src/results/plots/lines_measured/{lamp_manufacturer}_{LampType}_{ccd_colour}_{exposure_time}_{id_number}_1dspec_cal_fluxes.png",
    shell:
        "python src/scripts/measure_fluxes.py {input.wavecal_spectrum} {output.final_table} {input.linelist_file} {output.output_plot}"


# # We have 12 photron exposures with the following parameters
# N_photron = 12
# Photron_lamp_names = ["ThAr"] * N_photron
# Photron_exposure_times = ["900s"] + ["10s"] + ["60s"] * 10
# Photron_CCD_colours = ["Blue"] + ["Red"] * 11
# Photron_ID_numbers = ["01"] + ["01"] + [f"{x:02}" for x in np.arange(1, 11)]
# # We have 11 GS exposures with the following parameters
# # Looks like we're missing the 10s GS dark
# N_GS = 11
# GS_lamp_names = ["ThAr"] * N_GS
# GS_exposure_times = ["900s"] + ["60s"] * 10
# GS_CCD_colours = ["Blue"] + ["Red"] * 10
# GS_ID_numbers = ["01"] + [f"{x:02}" for x in np.arange(1, 11)]
# # We have 56 Newport exposures
# N_Newport = 56
# Newport_lamp_names = (
#     ["Ar"] * 12 + ["HgAr"] * 14 + ["HgNe"] * 3 + ["Kr"] * 12 + ["Ne"] * 13 + ["Xe"] * 2
# )
# Newport_exposure_times = (
#     (["600s"] + ["10s"] + ["60s"] * 10)  # Ar
#     + (["10s"] * 10 + ["90s"] * 4)  # HgAr
#     + (["10s"] + ["60s"] + ["300s"])  # HgNe
#     + (["600s"] + ["10s"] + ["60s"] * 10)  # Kr
#     + (["300s"] * 2 + ["1s"] + ["10s"] * 10)  # Ne
#     + (["600s"] + ["600s"])  # Xr
# )
# # TODO: fix these
# Newport_CCD_colours = ["Blue"] + ["Red"] * 10
# Newport_ID_numbers = ["01"] + [f"{x:02}" for x in np.arange(1, 11)]
# # The overall lists
# lamp_manufacturers = ["Photron"] * 12 + ["GS"] * 12
# all_lamp_names = Photron_lamp_names + GS_lamp_names
# all_ID_numbers = Photron_ID_numbers + GS_ID_numbers
# all_exposure_times = Photron_exposure_times + GS_exposure_times
# all_CCD_colours = Photron_CCD_colours + GS_CCD_colours
