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
completion = ""

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
    buffer = band.ReadAsArray(0, 0, dataset1.RasterXSize, dataset1.RasterYSize)
    nullcells = []
    for rowIndex in range(len(buffer)):
        for cellIndex in range(len(buffer[rowIndex])):
            if buffer[rowIndex][cellIndex] == nullValue:
                nullcells.append([rowIndex, cellIndex])
    return nullcells

ncells = findNullCell(target, 65535)