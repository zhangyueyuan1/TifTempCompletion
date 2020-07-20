# Author: Yueyuan Zhang
# Email: 
# Date: 2020-7-10
# Description: complete temperature data in Tiff

import gdal
#import zyytif
import math

gdal.AllRegister()

# Target Data
target = "F:\\GitHubCollection\\TifTempCompletion\\test\\pro3_A2018017_dagraded_v3.tif"

# Reference Data
reference = "F:\\GitHubCollection\\TifTempCompletion\\test\\pro3_A2018015_lst.tif"

# Vegetation Data
vege = "F:\\GitHubCollection\\TifTempCompletion\\test\\pro3_MOD13A2.A2018001.tif"

# Null Value
null = -3.40282346639e+038   #-3.40282346639e+038

# Pairs Number
pairsNum = 8

# Window Size List
winlist = [5, 7, 9, 11, 13, 15, 17, 19]

def abs(value):
    if value < 0:
        return -value
    return value

def findPairs(target, reference, vege):
    nullcells = findNullCell(target, null)
    for ncellitem in nullcells:
        for currentwin in winlist:
            win_target = getWindowByLocation(target, ncellitem, currentwin)
            win_reference, clocation_r, adjust = getWindowByLocation(reference, ncellitem, currentwin)

            ept_r = reference.ReadAsArray(ncellitem[0], ncellitem[1], 1, 1)[0][0]
            if ept_r == -3.40282346639e+038:
                continue
            ept_v = vege.ReadAsArray(ncellitem[0], ncellitem[1], 1, 1)[0][0]

            # similar cells in reference window
            win_vege, clocation_v, adjust_v = getWindowByLocation(vege, ncellitem, currentwin)
            
            r_ave = getAvergae(win_reference, -3.40282346639e+038, ept_r)
            tthd = getTVthd(win_reference, -3.40282346639e+038, r_ave, ept_r)
            print(tthd)

            v_ave = getAvergae(win_vege, -3.40282346639e+038, ept_v)
            vthd = getTVthd(win_vege, -3.40282346639e+038, v_ave, ept_v)
            print(vthd)

            cells_r = getSimilar(win_reference, clocation_r, ept_r, tthd)
            cells_v = getSimilar(win_vege, clocation_v, ept_v, vthd)

            common = findCommon(cells_r, cells_v)

            print(common)

            if len(common) > pairsNum:
                common_ad = []
                print("Bingo!")
                for com in common:
                    com[0] = com[0] + adjust[0]
                    com[1] = com[1] + adjust[1]
                    common_ad.append(com)
                return {
                    "clocation" : [ncellitem[0], ncellitem[1]],
                    "pairs" : common_ad
                }
    return []
                

def findCommon(win1, win2):
    common = []
    for w1 in win1:
        for w2 in win2:
            if w1[0] == w2[0] and w1[1] == w2[1]:
                common.append(w1)
    return common

def getSimilar(win, clocation, cvalue, thd):
    cells = []
    for yIndex in range(len(win)):
        for xIndex in range(len(win[yIndex])):
            if yIndex == clocation[0] and xIndex == clocation[1]:
                continue
            if abs(win[yIndex][xIndex] - cvalue) < thd:
                cells.append([yIndex, xIndex])
    return cells

def getAvergae(win, null, ept):
    sum = 0
    count = -1
    for yIndex in range(len(win)):
        for xIndex in range(len(win[yIndex])):
            if win[yIndex][xIndex] == null:
                continue
            sum = sum + win[yIndex][xIndex]
            count = count + 1
    
    sum = sum - ept
    ave = sum/count
    return ave


def getTVthd(win, null, ave, ept):
    sum = 0
    count = -1
    for row in win:
        for cell in row:
            if cell == null:
                continue
            sum = sum + (cell - ave)*(cell - ave)
            count = count + 1
    sum = sum - (ept - ave)*(ept - ave)
    return math.sqrt(sum/count)
    


#! find the null cells
def findNullCell(band, nullValue):
    nullcells = []
    for rowIndex in range(band.YSize):
        for cellIndex in range(band.XSize):
            cell = band.ReadAsArray(cellIndex, rowIndex, 1, 1)[0][0]
            if cell == nullValue:
                nullcells.append([cellIndex, rowIndex])
    return nullcells

#! get window cells
#! The size must be odd number
def getWindowByLocation(band, location, size):
    if size%2 == 0 or size < 2:
        raise Exception("Size must be odd number and larger than 1!")
    offsize = int(size/2)
    clocation = [offsize, offsize]
    xStart = location[0] - offsize
    yStart = location[1] - offsize
    xSize = size
    ySize = size
    if xStart < 0:
        xSize = xStart + xSize
        clocation[0] = clocation[0] + xSize
        xStart = 0
    if yStart < 0:
        ySize = yStart + ySize
        clocation[0] = clocation[0] + xSize
        yStart = 0
    win = band.ReadAsArray(xStart, yStart, xSize, ySize)

    adjust = [xStart, yStart]

    return win, clocation, adjust

def getDi(band_r, band_v, location, clocation, trans):
    ts0_ = band_r.ReadAsArray(clocation[0], clocation[1], 1, 1)[0][0]
    tsi_ = band_r.ReadAsArray(location[0], location[1], 1, 1)[0][0]
    abs1 = abs(ts0_ - tsi_ + 0.001)
    
    vs0_ = band_v.ReadAsArray(clocation[0], clocation[1], 1, 1)[0][0]
    vsi_ = band_v.ReadAsArray(location[0], location[1], 1, 1)[0][0]
    abs2 = abs(vs0_ - vsi_ + 0.001)

    local_r = [trans[0] + (location[0] + 0.5) * trans[2], trans[1] + (location[1] + 0.5) * trans[3]]
    local_c = [trans[0] + (clocation[0] + 0.5) * trans[2], trans[1] + (clocation[1] + 0.5) * trans[3]]

    dis = (local_r[0] - local_c[0])*(local_r[0] - local_c[0]) + (local_r[1] - local_c[1])*(local_r[1] - local_c[1])

    return abs1*abs2*dis

#! Start below

# Get bands
# from target
dataset_target = gdal.Open(target)
band_target = dataset_target.GetRasterBand(1)
# from reference
dataset_reference = gdal.Open(reference)
band_reference = dataset_reference.GetRasterBand(1)
# from Vegetation
dataset_vege = gdal.Open(vege)
band_vege = dataset_vege.GetRasterBand(1)

trans = dataset_target.GetGeoTransform()
# print(dataset_target.GetProjection())

trans = [trans[0], trans[3], trans[1], trans[5]]

pairs = findPairs(band_target, band_reference, band_vege)

clocation = pairs["clocation"]
for pair in pairs["pairs"]:
    di = getDi(band_reference, band_vege, pair, clocation, trans)
    print(di)