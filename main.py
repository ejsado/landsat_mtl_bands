# this script will automate the creation of a mosaic dataset with imagery
# it attempts to use predefined band definitions by ESRI
# everything is set by the user in "options.py"

import sys
import glob
import arcpy

from options import *


# scan a directory for MTL text files and TIF files
# return a list of dictionaries with the scene name, MTL file, list of TIFs, and associated raster composite
def find_landsat_scenes(directory):
	# scene dictionary will have pairs (key: value)
	# (name: scene name)
	# (mtl: path to mtl file)
	# (images: [list of TIF files])
	# (composite: path to composite raster)
	landsatScenes = []
	# iterate through the MTL text files
	for mtl in glob.glob(directory + r"\**\*MTL.txt", recursive=True):
		splitPath = mtl.split("\\")
		# get the scene name from the MTL file
		sceneName = splitPath[-1][:-8]
		print("found scene: " + sceneName)
		# get the path to the containing folder
		sceneDir = "\\".join(splitPath[:-1])
		tifList = []
		# find all TIFs in that containing folder
		allTifs = glob.glob(sceneDir + r"\*.TIF")
		# find any related TIFs and add them to the image list
		for tif in allTifs:
			if sceneName in tif:
				tifList.append(tif)
		# check if the composite raster already exists for this scene
		compName = sceneName + compositeText
		compositePath = None
		if arcpy.Exists(compName):
			# if it exists, set it to the full path
			compositePath = arcpy.env.workspace + "\\" + compName
		# if related TIFs were found, add the scene to the list
		if len(tifList) > 0:
			landsatScenes.append(
				{
					"name": sceneName,
					"mtl": mtl,
					"images": tifList,
					"composite": compositePath
				}
			)
	return landsatScenes


if __name__ == '__main__':
	print("Running landsat_mtl_bands")
	# index all MTL and related files
	sceneList = find_landsat_scenes(imagesFolder)
	# exit if no scenes (MTLs) were found
	if len(sceneList) == 0:
		sys.exit("No scenes found.")
	if createRasterComposites:
		print("creating composite rasters")
		for scene in sceneList:
			compositeName = scene["name"] + compositeText
			print("create composite: " + compositeName)
			# run the geoprocessing tool to create each composite raster
			arcpy.CompositeBands_management(scene["mtl"], compositeName)
			# set the index to the composite in the scene list
			scene["composite"] = arcpy.env.workspace + "\\" + compositeName
	if createMosaicDataset:
		print("creating mosaic dataset: " + mosaicName)
		# creating a mosaic dataset requires a spatial reference
		# this tool assumes all rasters are in the same area
		# and simply gets the spatial reference of the first TIF found
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
		# build a list of composite rasters
		compList = []
		for scene in sceneList:
			if scene["composite"]:
				compList.append(scene["composite"])
		# exit if no composites are found
		if len(compList) == 0:
			sys.exit("No raster composites found.")
		# run the geoprocessing tool
		arcpy.AddRastersToMosaicDataset_management(
			mosaicName,
			"Raster Dataset",
			compList,
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


