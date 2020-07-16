# Author: Yueyuan Zhang
# Email: 
# Date: 2020-7-10
# Description: complete temperature data in Tiff

import gdal
import zyytif

gdal.AllRegister()

# Target Data
target = "./test/A2018015_lst.tif"

# Reference Data
reference = "./test/A2018017_dagraded_v3.tif"

# Vegedation Data
vege = ""

# Null Value
null = 65535

# Window Size List
winlist = [5, 7, 9, 11, 13, 15, 17, 19]

def findPairs(target, reference):
    nullcells = findNullCell(target, null)
    for ncellitem in nullcells:
        for currentwin in winlist:
            win_target = getWindowByLocation(target, ncellitem, currentwin)
            win_reference = getWindowByLocation(reference, ncellitem, currentwin)

def calTthd():
    pass

def calVthd():
    pass

#! find the null cells
def findNullCell(band, nullValue):
    nullcells = []
    for rowIndex in range(band.YSize):
        for cellIndex in range(band.XSize):
            cell = band.ReadAsArray(cellIndex, rowIndex, 1, 1)[0][0]
            if cell == nullValue:
                nullcells.append([rowIndex, cellIndex])
    return nullcells

#! get window cells
#! The size must be odd number
def getWindowByLocation(band, location, size):
    if size%2 == 0 or size < 2:
        raise Exception("Size must be odd number and larger than 1!")
    offsize = int(size/2)
    xStart = location[0] - offsize
    yStart = location[1] - offsize
    xSize = size
    ySize = size
    if xStart < 0:
        xSize = xStart + xSize
        xStart = 0
    if yStart < 0:
        ySize = yStart + ySize
        yStart = 0
    win = band.ReadAsArray(xStart, yStart, xSize, ySize)
    return win


#! Start below

# Get bands
# from target
dataset_target = gdal.Open(target)
band_target = dataset_target.GetRasterBand(1)
# from reference
dataset_reference = gdal.Open(reference)
band_reference = dataset_reference.GetRasterBand(1)



ncells = findNullCell(band_target, null)

print(ncells)

win = getWindowByLocation(band_target, [0,1], 5)

print(win)