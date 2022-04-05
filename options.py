import arcpy

# environment settings
# set the geodatabase where the script will create items
arcpy.env.workspace = r"D:\ProjectsSyncDesktop\GIS\DenverLandUse\COFrontRangeImagery.gdb"
# overwrite items in the workspace with items created by this script
# if this is false, an error will occur when an item already exists
arcpy.env.overwriteOutput = True

# open project
aprx = arcpy.mp.ArcGISProject(r"D:\ProjectsSyncDesktop\GIS\DenverLandUse\COFrontRangeImagery.aprx")

# imagery type
# must be one of the following:
#   LANDSAT_6BANDS - Create a 6-band mosaic dataset using the Landsat 5 and 7 wavelength ranges from the TM and ETM+ sensors.
#   LANDSAT_8BANDS - Create an 8-band mosaic dataset using the LANDSAT 8 wavelength ranges.
# based off product_definition values:
#   https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/create-mosaic-dataset.htm
# other types could be supported by adding logic to find and organize other file naming structures
imageryType = "LANDSAT_6BANDS"

# select which operations to perform
createRasterComposites = True
createMosaicDataset = True
addRastersToMosaic = True
buildFootprints = True
buildSeamlines = True

# text to append to raster composites
compositeText = "_composite"

# full path to directory where the images are stored
imagesFolder = r"D:\ProjectsSyncDesktop\GIS\DenverLandUse\data\Landsat_4_5_TM_C2_L2_Mar_30"

# name of the mosaic to be edited
mosaicName = "Landsat5MosaicEE"
