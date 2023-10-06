# `data/`

The data in these directories is the following.

## `data/csv`

Where tabular data relevant to the project is stored. This includes information on identifiers and image data. The CSV files are as follows:

- `mss_identifiers.csv`: A file linking the internal project IDs for each manuscript to other relevant identifiers. Columns are the following:
  - **project_ID**. The internal ID used in this project.
  - **Princeton_ARK**. The archival resource key (ARK) used by Princeton. (This category is subject to change when the project expands its sources.) This data can also be found referenced in the IIIF manifests.
  - **IIIF_manifest**. The IIIF manifest for the manuscript, if available.
  - **shelfmark**. The shelfmark for the manuscript. (Also Princeton specific right now; subject to change.)
  - **ISMI_ID**. The identifier used by the [Islamic Scientific Manuscripts Initiative](https://ismi.mpiwg-berlin.mpg.de/) for this manuscript, if available.

- `mss_imagedata.csv`: A file linking the internal project IDs for each manuscript to data on the photos making up the digitized manuscript. Columns are the following:
  - **project_ID**. The internal ID used in this project.
  - **img_type**. Current categories are (1) *photo_digital*, if the digital manuscript was produced from digital photographs; or (2) *microfilm_digital*, if produced from a scan of a microfilm.
  - **reduction_ratio**. Only relevant if this is a scan of a microfilm. Records the reduction ratio used for the creation of the microfilm.
  - **photo_spread**. Current categories are (1) *folio*, if each image is one folio; or (2) *bifolio*, if each image is of a bifolio spread.
  - **img_count**. Count of the number of images associated with the digitized manuscript.
    
- `fols_imagedata.csv`: A file linking the individual images for all the manuscripts to data on the image files.
  - **project_ID**. The internal ID of the manuscript associated with the image file.
  - **img**. The relevant image file.
  - **format**. Image format, e.g. JPEG or TIFF.
  - **width_px**. The width of the image in pixels.
  - **height_px**. The height of the image in pixels.
  - **mode**. The types and depths of pixels in the image, e.g. RGB (3x8-bit pixels, true color) or L (Luminance: 8-bit pixels, grayscale).
  - **filesize_KB**. The filesize of the image in kilobytes.
  - **greyscale_bool**. TRUE if the image is greyscale, FALSE if the image is in color.
 
## `/data/json`

Currently used to store IIIF manifests of manuscripts used in the project, for recordkeeping. Each IIIF manifest recieves as a filename the project_ID used for that particular digitized manuscript. Links to the live IIIF manifests available online can be found through the `mss_identifiers.csv` file, as noted above.

## `data/xml`
Where xml data relevant to the project is stored. This directory contains directories for data from each of the manuscripts, sorted into separate subdirectories which recieve the relevant manuscript project_ID as a subdirectory name. Each subdirectory contains the ALTO XML files that can be used to train the segmentation models.

Note: these are ALTO XML files which contain references to the filenames of the source image files in the `<fileName>` tag. These image files, however, are not stored in this GitHub repository. For publically-available images, such as images obtained via IIIF, the images may be acquired from the relevant digital manuscript repositories. See the `mss_identifiers.csv` file or the IIIF manifest json files above for relevant data where to find these images online.
