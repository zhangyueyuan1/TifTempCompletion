# Author: Yueyuan Zhang
# Email: 
# Date: 2020-7-10
# Description: complete temperature data in Tiff

import rasterio
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

with rasterio.open(r"F:\GitHubCollection\TifTempCompletion\test\A2018017_dagraded_v3.tif") as src:
    lst=src.read(1, masked=True)
    lst=lst*0.02

with rasterio.open(r"F:\GitHubCollection\TifTempCompletion\test\A2018015_lst.tif")as src2:
    lst_ref=src2.read(1, masked=True)
    lst_ref=lst_ref*0.02  
    
with rasterio.open(r"F:\GitHubCollection\TifTempCompletion\test\MOD13A2.A2018001.tif") as src:
    ndvi=src.read(1, masked=True)
    ndvi=ndvi*0.0001
    #plt.imshow(ndvi) 

whole_x = ndvi.shape[0]
whole_y = ndvi.shape[1]

masked=lst[0][0]
# Null_pixel_lst=np.where(lst == masked)
# Valid_pixel_lst=np.where(lst<60000)

# Null_pixel_ref=np.where(lst_ref == masked)
# Valid_pixel_ref=np.where(lst_ref <60000)

# Null_pixel_ndvi=np.where(ndvi == masked)
# Valid_pixel_ndvi=np.where(ndvi>-1)

def find_similar(center_x_min, center_x_max, center_y_min, center_y_max, window):
    window_ts_value1 = lst_ref[center_x_min:center_x_max, center_y_min: center_y_max]
    window_ts_value2 = window_ts_value1[np.where(window_ts_value1 != masked)] #参考lst图层窗口内的有效值
    
    window_ndvi_value1 = ndvi[center_x_min:center_x_max, center_y_min: center_y_max]
    window_ndvi_value2 = window_ndvi_value1[np.where(window_ndvi_value1 != masked)] #窗口内的ndvi有效值
    
    ts_predict_block1 = lst[center_x_min:center_x_max, center_y_min: center_y_max]
    ts_predict_block2 = ts_predict_block1[np.where(ts_predict_block1 != masked)]   #预测lst图层窗口内的有效值

    Mean_ts_value = window_ts_value2 * 0 + np.nanmean(window_ts_value2)
    Mean_ndvi_value = window_ndvi_value2 * 0 + np.nanmean(window_ndvi_value2)
    
    if (window_ts_value2.shape[0]) > 0:                 #如果存在有效像元
        RMSE_ts=sqrt(mean_squared_error(window_ts_value2.reshape(-1,1), Mean_ts_value.reshape(-1,1)))
        T_thd = RMSE_ts #温度阈值
        
        RMSE_ndvi=sqrt(mean_squared_error(window_ndvi_value2.reshape(-1,1), Mean_ndvi_value.reshape(-1,1)))
        V_thd = RMSE_ndvi  #植被指数阈值
        
        for ts_value in window_ts_value2:
            
            location = np.where (window_ts_value2 == ts_value)
            
            center_ts_value = window_ts_value1[(center_x_max - 1)/2][(center_y_max - 1)/2]
            Diff_ts = abs(center_ts_value - ts_value)
            
            center_ndvi_value = window_ndvi_value1[(center_x_max - 1)/2][(center_y_max - 1)/2]
            Diff_ndvi = abs(center_ndvi_value - window_ndvi_value2[location])
                                   
            ref_similar=[]
            lst_similar=[]
            
            if Diff_ts<=T_thd || Diff_ndvi<=V_thd:
                                
                ref_similar.append(ts_value)
                lst_similar.append(ts_predict_block2[location])
                
                similar_no=len(ref_similar)

            if similar_no >= 10:
                break

    else:
        similar_no = 0

    similar_limit = 10
    window_max=15

    while similar_no < similar_limit:

        window = window + 1

        center_x_min = center_x_min - 1
        center_x_max = center_x_max + 1
        center_y_min = center_y_min - 1
        center_y_max = center_y_max + 1
        
        if center_x_min < 0:
            center_x_min = 0
        if center_x_max > whole_x:
            center_x_max = whole_x

        if center_y_min < 0:
            center_y_min = 0
        if center_y_max > whole_y:
            center_y_max = whole_y
        
        if window>=window_max:
            break

    return ref_similar, lst_similar, similar_no

result = find_similar(0,3,0,3,1)

# x=result[0]
# y=result[1]
# Count=result[2]

# regre_result = regression.fit(x, y)



    

        
        
    
    
    
