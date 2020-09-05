# Author: Yueyuan Zhang
# Email: 
# Date: 2020-7-10
# Description: complete temperature data in Tiff

import gdal
import zyytif
import math
import numpy as np
import os

gdal.AllRegister()

#! Target Data
target = "./test/pro3_A2018017_dagraded_v3.tif"

#! Reference Data
reference = "./test/pro3_A2018015_lst.tif"
reference_dir = "./test/refs/"

#! Vegetation Data
vege = "./test/pro3_MOD13A2.A2018001.tif"
vege_dir = "./test/ndvi/"

#! Null Value
null = -3e+038   #-3.40282346639e+038

#! Pairs Number
pairsNum = 7

#! Max window size
# range_max = max(band_target.XSize, band_target.YSize)
range_max = 25

def abs(value):
    if value < 0:
        return -value
    return value

def findPairs(target, reference, vege, ncellitem):
    result = None
    result = findPairs_dynamic(target, reference, vege, ncellitem)
    if len(result["pairs"]) < 3:
        result = findPairs_fixed(target, reference, vege, ncellitem)
    return result

def findPairs_dynamic(target, reference, vege, ncellitem):
    leastPairs = []
    for currentwin in winlist:
        win_target, clocation_t, adjust_t = getWindowByLocation(target, ncellitem, currentwin)
        win_reference, clocation_r, adjust = getWindowByLocation(reference, ncellitem, currentwin)

        ept_r = reference.ReadAsArray(ncellitem[0], ncellitem[1], 1, 1)[0][0]
        ept_v = vege.ReadAsArray(ncellitem[0], ncellitem[1], 1, 1)[0][0]
        
        win_reference = combineNull(win_reference, win_target, null, clocation_r)

        # similar cells in reference window
        win_vege, clocation_v, adjust_v = getWindowByLocation(vege, ncellitem, currentwin)
        
        r_ave = getAvergae(win_reference, null, clocation_r)
        tthd = getTVthd(win_reference, null, r_ave, clocation_r)
        # print(tthd)

        v_ave = getAvergae(win_vege, null, clocation_r)
        vthd = getTVthd(win_vege, null, v_ave, clocation_r)
        # print(vthd)

        cells_r = getSimilar(win_reference, clocation_r, ept_r, tthd)
        cells_v = getSimilar(win_vege, clocation_v, ept_v, vthd)

        common = findCommon(cells_r, cells_v)

        #! judge if common pairs is enough
        if len(common) > pairsNum:
            common_ad = []
            # print("Bingo!")
            for com in common:
                com_n = [0, 0]
                com_n[0] = com[0] + adjust[0]
                com_n[1] = com[1] + adjust[1]
                common_ad.append(com_n)
            return {
                "clocation" : [ncellitem[0], ncellitem[1]],
                "pairs" : common_ad
            }
        elif len(common) > 2:
            common_ad = []
            # print("Bingo!")
            for com in common:
                com_n = [0, 0]
                com_n[0] = com[0] + adjust[0]
                com_n[1] = com[1] + adjust[1]
                common_ad.append(com_n)
            leastPairs = common_ad
    return {
        "clocation" : [ncellitem[0], ncellitem[1]],
        "pairs" : leastPairs
        }

def findPairs_fixed(target, reference, vege, ncellitem):
    leastPairs = []
    for currentwin in winlist:
        win_target, clocation_t, adjust_t = getWindowByLocation(target, ncellitem, currentwin)
        win_reference, clocation_r, adjust = getWindowByLocation(reference, ncellitem, currentwin)

        ept_r = reference.ReadAsArray(ncellitem[0], ncellitem[1], 1, 1)[0][0]
        ept_v = vege.ReadAsArray(ncellitem[0], ncellitem[1], 1, 1)[0][0]
        
        win_reference = combineNull(win_reference, win_target, null, clocation_r)

        # similar cells in reference window
        win_vege, clocation_v, adjust_v = getWindowByLocation(vege, ncellitem, currentwin)

        cells_r = getSimilar(win_reference, clocation_r, ept_r, 0.05)
        cells_v = getSimilar(win_vege, clocation_v, ept_v, 0.05)

        common = findCommon(cells_r, cells_v)
        
        #! judge if common pairs is enough
        if len(common) > pairsNum:
            common_ad = []
            # print("Bingo!")
            for com in common:
                com_n = [0, 0]
                com_n[0] = com[1] + adjust[0]
                com_n[1] = com[0] + adjust[1]
                common_ad.append(com_n)
            return {
                "clocation" : [ncellitem[0], ncellitem[1]],
                "pairs" : common_ad
            }
        else:
            common_ad = []
            # print("Bingo!")
            for com in common:
                com_n = [0, 0]
                com_n[0] = com[1] + adjust[0]
                com_n[1] = com[0] + adjust[1]
                common_ad.append(com_n)
            leastPairs = common_ad
    return {
        "clocation" : [ncellitem[0], ncellitem[1]],
        "pairs" : leastPairs
        }

def combineNull(target, reference, null, eptLocation):
    for yIndex in range(len(target)):
        for xIndex in range(len(target[0])):
            if yIndex == eptLocation[1] and xIndex == eptLocation[0]:
                continue
            if reference[yIndex][xIndex] < null:
                target[yIndex][xIndex] = reference[yIndex][xIndex]
    return target

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
            if yIndex == clocation[1] and xIndex == clocation[0]:
                continue
            if win[yIndex][xIndex] < null:
                continue
            if abs(win[yIndex][xIndex] - cvalue) < thd:
                cells.append([xIndex, yIndex])
    return cells

def getAvergae(win, null, ept):
    sum = 0
    count = 0
    for yIndex in range(len(win)):
        for xIndex in range(len(win[yIndex])):
            if win[yIndex][xIndex] < null:
                continue
            if yIndex == ept[1] and xIndex == ept[0]:
                continue
            sum = sum + win[yIndex][xIndex]
            count = count + 1
    if count == 0:
        return ept
    ave = sum/count
    return ave

def getAvergaeByLocation(band, locations):
    sum = 0
    count = 0
    for lct in locations:
        cellvalue = band.ReadAsArray(lct[0], lct[1], 1, 1)[0][0]
        # print(cellvalue)
        sum = sum + cellvalue
        count = count + 1
    ave = sum/count
    return ave

def getTVthd(win, null, ave, ept):
    sum = 0
    count = 0
    for rowIndex in range(len(win)):
        for cellIndex in range(len(win[rowIndex])):
            if win[rowIndex][cellIndex] < null:
                continue
            if rowIndex == ept[1] and cellIndex == ept[0]:
                continue
            sum = sum + (win[rowIndex][cellIndex] - ave)*(win[rowIndex][cellIndex] - ave)
            count = count + 1
    if count == 0:
        return 0
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

def findNullCell2(band, nullValue):
    nullcells = []
    for rowIndex in range(band.YSize):
        for cellIndex in range(band.XSize):
            cell = band.ReadAsArray(cellIndex, rowIndex, 1, 1)[0][0]
            if cell < nullValue:
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
        clocation[0] = clocation[0] + xStart
        xStart = 0
    if yStart < 0:
        ySize = yStart + ySize
        clocation[1] = clocation[1] + yStart
        yStart = 0
    if (xStart + xSize) > band.XSize:
        xSize = xSize - (xStart + xSize - band.XSize)
    if (yStart + ySize) > band.YSize:
        ySize = ySize - (yStart + ySize - band.YSize)
    win = band.ReadAsArray(xStart, yStart, xSize, ySize)

    adjust = [xStart, yStart]

    return win, clocation, adjust

def getDi(band_r, band_v, location, clocation, trans):
    ts0_ = band_r.ReadAsArray(clocation[0], clocation[1], 1, 1)[0][0]
    tsi_ = band_r.ReadAsArray(location[0], location[1], 1, 1)[0][0]
    abs1 = round(abs(ts0_ - tsi_ + 0.001), 9)
    
    vs0_ = band_v.ReadAsArray(clocation[0], clocation[1], 1, 1)[0][0]
    vsi_ = band_v.ReadAsArray(location[0], location[1], 1, 1)[0][0]
    abs2 = round(abs(vs0_ - vsi_ + 0.001), 9)

    local_r = [trans[0] + (location[0] + 0.5) * trans[2], trans[1] + (location[1] + 0.5) * trans[3]]
    local_c = [trans[0] + (clocation[0] + 0.5) * trans[2], trans[1] + (clocation[1] + 0.5) * trans[3]]

    dis = round((local_r[0] - local_c[0])*(local_r[0] - local_c[0]) + (local_r[1] - local_c[1])*(local_r[1] - local_c[1]), 20)

    di = (abs1) * (abs2) * (dis)

    return di

def getWi(dis):
    wis = []

    sum = 0
    for di in dis:
        sum = sum + round((1/di), 9)

    for di in dis:
        wi = (1/di)/sum
        wis.append(wi)

    return wis

def getAB(band_target, band_reference, pairs, wis):

    Ts_ = getAvergaeByLocation(band_target, pairs)
    Tsd_ = getAvergaeByLocation(band_reference, pairs)

    sum_up = 0
    sum_bottom = 0

    for index in range(len(pairs)):
        Tsi = band_target.ReadAsArray(pairs[index][0], pairs[index][1], 1, 1)[0][0]
        Tsdi = band_reference.ReadAsArray(pairs[index][0], pairs[index][1], 1, 1)[0][0]
        sum_up = sum_up + wis[index]*(Tsi - Ts_)*(Tsdi - Tsd_)
        sum_bottom = sum_bottom + wis[index]*(Tsdi - Tsd_)*(Tsdi - Tsd_)

    a = sum_up/sum_bottom
    b = Ts_ - a*Tsd_
    return a,b


#! Start below
# find all target
target_file_collection = os.listdir(reference_dir)
all_collection = []
for target_file in target_file_collection:
    ext = os.path.splitext(target_file)[-1]
    if ext == ".tif":
        all_collection.append(target_file)
all_collection.sort()

# find all vegetation
vege_file_collection = os.listdir(vege_dir)
vege_collection = []
for vege_file in vege_file_collection:
    ext = os.path.splitext(vege_file)[-1]
    if ext == ".tif":
        vege_collection.append(vege_file)

target_collection = all_collection[0:len(all_collection) - 15]
fileProgress = 0
for target in target_collection:
    fileProgress = fileProgress + 1
    # Get bands
    # from target
    dataset_target = gdal.Open(reference_dir + target)
    band_target = dataset_target.GetRasterBand(1)

    time_curr_str = target[9:16]
    time_curr_year = int(time_curr_str[0:4])
    time_curr_day = int(time_curr_str[4:7])

    time_ref_start = time_curr_day + 1
    time_ref_end = time_curr_day + 16

    reference_date_str = []
    for day in range(time_ref_start, time_ref_end):
        reference_date_str.append(str(time_curr_year) + "{:0>3d}".format(day))

    reference_collection = []
    for referfile in all_collection:
        ext = os.path.splitext(referfile)[-1]
        if ext == ".tif":
            for ref_date in reference_date_str:
                if referfile.find(ref_date) > -1:
                    reference_collection.append(referfile)
                    break

    trans = dataset_target.GetGeoTransform()
    # print(dataset_target.GetProjection())

    # Window Size List
    winlist = []
    for item in range(3, range_max, 2):
        winlist.append(item)
    # winlist = [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]

    trans = [trans[0], trans[3], trans[1], trans[5]]

    
    new_buffer = np.array(band_target.ReadAsArray(0, 0, band_target.XSize, band_target.YSize))

    nullcells = findNullCell2(band_target, null)
    total = len(nullcells)
    currentProgress = 0

    #! Debug line
    # nullcells = [[238,148]]

    for ncellitem in nullcells:
        print("[" + target + "] start calculate NULL cell : [" + str(ncellitem[0]) + "], [" + str(ncellitem[1]) + "]")

        # from reference
        band_reference = None
        pairs = {
            "clocation" : [ncellitem[0], ncellitem[1]],
            "pairs" : []
        }
        leastPairs = {
            "clocation" : [ncellitem[0], ncellitem[1]],
            "pairs" : []
        }
        for reference_file in reference_collection:

            # find corresponding vegetation file
            time_ref_str = reference_file[9:16]
            time_ref_year = int(time_ref_str[0:4])
            time_ref_day = int(time_ref_str[4:7])

            vegeDay = str(time_ref_year) + ("{:0>3d}".format(int((time_ref_day - 1)/16)*16 + 1))

            vege = ""
            for vege_file in vege_collection:
                if vege_file.find(vegeDay) > -1:
                    vege = vege_dir + vege_file
            
            dataset_vege = gdal.Open(vege)
            band_vege = dataset_vege.GetRasterBand(1)

            dataset_reference = gdal.Open(reference_dir + reference_file)
            band_reference = dataset_reference.GetRasterBand(1)
            if band_reference.ReadAsArray(ncellitem[0], ncellitem[1], 1, 1)[0][0] < null:
                print("[" + target + "] cell [" + str(ncellitem[0]) + "],[" + str(ncellitem[1]) + "] in reference [" + reference_file + "] is NULL!")
                continue
            else:
                print("[" + target + "] cell [" + str(ncellitem[0]) + "],[" + str(ncellitem[1]) + "] in reference [" + reference_file + "] is assigned!")

            pairs = findPairs(band_target, band_reference, band_vege, ncellitem)

            if len(pairs["pairs"]) > 2:
                print("[" + target + "] cell [" + str(ncellitem[0]) + "],[" + str(ncellitem[1]) + "] in reference [" + reference_file + "] find enough pairs (>2)!")
                break
            elif len(pairs["pairs"]) > 0:
                print("[" + target + "] cell [" + str(ncellitem[0]) + "],[" + str(ncellitem[1]) + "] in reference [" + reference_file + "] find a few pairs (>0 <2)!")
                if len(len(pairs["pairs"]) > leastPairs["pairs"]):
                    leastPairs = pairs

        if band_reference == None:
            continue
        if len(leastPairs["pairs"]) > len(pairs["pairs"]):
            pairs = leastPairs


        a = 0
        b = 0
        if len(pairs["pairs"]) < 3 and len(pairs["pairs"]) > 0:
            Ts_ = getAvergaeByLocation(band_target, pairs["pairs"])
            Tsd_ = getAvergaeByLocation(band_reference, pairs["pairs"])
            a = Ts_/Tsd_
        if len(pairs["pairs"]) == 0:
            print("[" + target + "] cell [" + str(ncellitem[0]) + "],[" + str(ncellitem[1]) + "] can not find any pairs (<1)!")
            continue
        else:
            clocation = pairs["clocation"]
            dis = []
            for pair in pairs["pairs"]:
                di = getDi(band_reference, band_vege, pair, clocation, trans)
                dis.append(di)

            wis = getWi(dis)

            a,b = getAB(band_target, band_reference, pairs["pairs"], wis)

        print("[" + target + "] in cell [" + str(ncellitem[0]) + "],[" + str(ncellitem[1]) + "] a : [" + str(a) + "]")
        print("[" + target + "] in cell [" + str(ncellitem[0]) + "],[" + str(ncellitem[1]) + "] b : [" + str(b) + "]")
            
        nullcell_r = band_reference.ReadAsArray(ncellitem[0], ncellitem[1], 1, 1)[0][0]

        completion = a*nullcell_r + b

        new_buffer[ncellitem[1], ncellitem[0]] = completion

        print("[" + target + "] X:[" + str(ncellitem[0]) + "] Y:[" + str(ncellitem[1]) + "] value:" + str(completion))
        currentProgress = currentProgress + 1
        print("[" + target + "] progress : " + "[" + str(currentProgress) + "/" + str(total) + "]")

    zyytif.ZYYTif.WriteTiff(new_buffer, band_target.XSize, band_target.YSize, 1, dataset_target.GetGeoTransform(), dataset_reference.GetProjection(), "./test/new_" + time_curr_str + ".tif")
    print("File : [" + target + "] finished! Progress : [" + str(fileProgress) + "/" + str(len(target_collection)) + "]")