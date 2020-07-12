# Author: Yueyuan Zhang
# Email: 
# Date: 2020-7-10
# Description: complete temperature data in Tiff

import gdal
import zyytif

gdal.AllRegister()

# Target Data
target = "./test/A2018015_lst.tif"

# Completion Data
completion = "./test/A2018017_dagraded_v3.tif"

# Vegedation Data
vege = ""

def findPairs(target, completion):
    pass

def calTthd():
    pass

def calVthd():
    pass

def findNullCell(target, nullValue):
    dataset1 = gdal.Open(target)
    band = dataset1.GetRasterBand(1)
    nullcells = []
    for rowIndex in range(dataset1.RasterYSize):
        for cellIndex in range(dataset1.RasterXSize):
            cell = band.ReadAsArray(cellIndex, rowIndex, 1, 1)[0][0]
            if cell == nullValue:
                nullcells.append([rowIndex, cellIndex])
    return nullcells

ncells = findNullCell(target, 65535)

print(ncells)