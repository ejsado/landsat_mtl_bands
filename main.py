# this script will automate the creation of a mosaic dataset with imagery
# it attempts to use predefined band definitions by ESRI
# Everything is set by the user in "options.py" including band wavelength names

import sys
import glob
from options import *


# scan a directory for MTL text files and QA TIF files
# return a list of dictionaries with the scene name, MTL file, and list of TIFs
def find_landsat_mtls(directory):
	# scene dictionary will have pairs (key: value)
	# (scene: scene name)
	# (mtl: path to mtl file)
	# (images: [list of TIF files])
	landsatScenes = []
	# iterate through the MTL text files
	for mtl in glob.glob(directory + r"\**\*MTL.txt", recursive=True):
		splitPath = mtl.split("\\")
		# get the scene name from the MTL file
		sceneName = splitPath[-1][:-8]
		print("found scene: " + sceneName)
		sceneDir = "\\".join(splitPath[:-1])
		tifList = []
		allTifs = glob.glob(sceneDir + r"\*.TIF")
		# find any TIFs and add them to the image list
		for tif in allTifs:
			if sceneName in tif:
				tifList.append(tif)
		if len(tifList) > 0:
			landsatScenes.append(
				{
					"scene": sceneName,
					"mtl": mtl,
					"images": tifList
				}
			)
	return landsatScenes


if __name__ == '__main__':
	print("Running landsat_mtl_bands")
	# index all TIF files as (key:value) -> (scene name:[list of TIF files])
	sceneList = find_landsat_mtls(imagesFolder)
	if len(sceneList) == 0:
		sys.exit("No scenes found.")
	if createMosaicDataset:
		print("creating mosaic dataset: " + mosaicName)
		# get the properties of the first image found
		describeRaster = arcpy.Describe(sceneList[0]["images"][0])
		# set the spatial reference of the raster
		rasterSpatialRef = describeRaster.spatialReference
		# run the geoprocessing tool
		arcpy.CreateMosaicDataset_management(
			arcpy.env.workspace,
			mosaicName,
			rasterSpatialRef,
			product_definition=imageryType
		)
	if addRastersToMosaic:
		print("add rasters to mosaic: " + mosaicName)
		# build a list of MTL files
		mtlList = []
		for scene in sceneList:
			mtlList.append(sceneList[scene]["mtl"])
		# set raster type for geoprocessing tool, found here:
		# https://pro.arcgis.com/en/pro-app/2.8/help/data/imagery/satellite-sensor-raster-types.htm#ESRI_SECTION1_40FE2ABD0A6145728056156125910AFF
		if imageryType == "LANDSAT_6BANDS":
			rasterType = "Landsat 5 TM"
		elif imageryType == "LANDSAT_8BANDS":
			rasterType = "Landsat 8"
		else:
			sys.exit("Invalid 'imageryType' in options.")
		print(rasterType)
		# run the geoprocessing tool
		arcpy.AddRastersToMosaicDataset_management(
			mosaicName,
			rasterType,
			mtlList,
			update_overviews="UPDATE_OVERVIEWS",
			build_pyramids="BUILD_PYRAMIDS",
			calculate_statistics="CALCULATE_STATISTICS",
			duplicate_items_action="OVERWRITE_DUPLICATES"
		)
	if buildFootprints:
		print("building footprints for: " + mosaicName)
		arcpy.BuildFootprints_management(mosaicName)
	if buildSeamlines:
		print("building seamlines for: " + mosaicName)
		arcpy.BuildSeamlines_management(mosaicName)


