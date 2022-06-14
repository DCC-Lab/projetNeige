import pandas as pd
import numpy as np

def getdata_excel(file, row):
    """file: str
        row: int, represent the picture
        
        return: array of 2 lines: 1-1 to the length of the row (representing the pixels); 2-the values in the excel of the row chosen"""
    path = f"C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\{file}.xlsx"
    matrix = np.array(pd.read_excel(path, skiprows=row-1, nrows=1))
    matrix = matrix[0][4:]
    pix = []
    for i in range(1, matrix.size+1):
        pix.append(i)
    return np.array([pix, matrix])

def calculate_slope(matrix):
    """matrix: array of 2 lines, the first one is the values concerning the height (pixel), the second concerning the intensity of the pixel
        
        return: the slope of the matrix values acording to the constant step between the first line of values"""
    constant_step = matrix[0][1]-matrix[0][0]
    x = matrix[1][:]
    slope = np.diff(x)/constant_step
    slope = np.array([matrix[0][1:], slope])
    return slope

def find_height(slope, scale=None):
    """slope: array of 2 lines, the first one is the values concerning the height (pixel), the second concerning the slope of the pixel intensity
        scale: list of 3 elements [min, max, step(1 or -1), range where we know the height is within, the scale by default change acording to the name of the file
        
        return: height in pixels of snow that is the streepestslope in the range chosen"""
    if scale is None:
        raise Exception("scale must have a value")
    streepest = slope[1][0]
    pix = scale[0]
    for i, value in enumerate(slope[1][scale[0]:scale[1]:scale[2]]):
        if value*scale[2] <= streepest:
            streepest = value*scale[2]
            pix = scale[0]+i*scale[2]
        else:
            continue
    heightx = 0
    for i, value in enumerate(slope[1][pix::scale[2]]):
        if value*scale[2] >= 0:
            heightx = slope[0][pix+i*scale[2]]
            break
        elif value*scale[2]/streepest < 0.5:
            heightx = slope[0][pix+i*scale[2]]
            break
        else:
            pass
    return heightx

def store_heights_pandacsv(file, rows, heights):
    """file: str
        rows: list
        heights: list
        
        return: dataframe pandas with 2 colums: 1-the date and hour; 2-the height associated"""
    path = f"C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\{file}.xlsx"
    dates = []
    for row in rows:
        date = list(pd.read_excel(path, header=0, usecols='D', skiprows=row, nrows=1))[0]
        dates.append(date)
    all_heights = {'date': dates, 'height': heights}
    all_heights = pd.DataFrame(all_heights)
    all_heights.to_csv(f"heights{file[-3:]}.csv", index=False)
    return all_heights


rows = []
heights = []
#write the file name here:
file = 'PlotAlign'

if file == 'PlotwithrefAlignIFM':
    scale = [1, 200, 1]
    for row in range(1, 87):
        rows.append(row)
        matrix = getdata_excel(file, row)
        slope = calculate_slope(matrix)
        height = find_height(slope, scale=scale)
        heights.append(height*10/40.8)
        #conditions where the scale for the next row must be particular to find the right height
        if row+1 == 7: 
            scale = [height-10, height+50, 1]
        elif row+1 == 18:
            scale = [25, 55, 1]
        elif row+1 == 19:
            scale = [90, 120, 1]
        elif row+1 == 41:
            scale = [130, 180, 1]
        else:
            scale = [height-30, height+30, 1]

elif file == 'PlotwithrefAlignCT1':
    scale = [0, 50, 1]
    #first row is at 0 pixel acording to the reference chosen
    rows.append(1)
    heights.append(0+59)
    for row in range(2, 18):
        rows.append(row)
        matrix = getdata_excel(file, row)
        slope = calculate_slope(matrix)
        height = find_height(slope, scale=scale)
        heights.append(height*10/40.8+59)
        #conditions where the scale for the next row must be particular to find the right height
        if row+1 == 11: 
            scale = [50, 70, 1]
        elif row+1 == 15:
            scale = [height, height+60, 1]
        elif row+1 == 12:
            scale = [60, 70, 1]    
        elif row+1 >= 13:
            scale = [height-20, height+20, 1]
        else:
            scale = [height-2, height+15, 1]

elif file == 'PlotAlignCT2':
    scale = [150, 180, 1]
    for row in range(1, 12):
        #to find the right reference for this file
        if row in [1, 11]:
            ranking = [390, 375, -1]
        elif row in [6, 7]:
            ranking = [417, 400, -1]
        elif row == 9:
            ranking = [395, 390, -1]
        elif row == 8:
            ranking = [417, 410, -1]
        elif row == 10:
            ranking = [385, 375, -1]
        else:
            ranking = [405, 395, -1]
        rows.append(row)
        matrix = getdata_excel(file, row)
        slope = calculate_slope(matrix)
        height = find_height(slope, scale=scale)
        minend = find_height(slope, scale=ranking)
        heights.append(130-((minend-height)*10/40.8))
        #conditions where the scale for the next row must be particular to find the right height
        if row+1 == 9: 
            scale = [100, 130, 1]
        elif row+1 >= 10:
            scale = [50, 100, 1]
        else:
            scale = [150, 180, 1]

elif file == 'PlotwithrefAlignCT3':
    scale = [150, 300, 1]
    for row in range(1, 27):
        rows.append(row)
        matrix = getdata_excel(file, row)
        slope = calculate_slope(matrix)
        height = find_height(slope, scale=scale)
        heights.append(height*10/40.8)
        #conditions where the scale for the next row must be particular to find the right height
        if row+1 == 15: 
            scale = [height-10, height+30, 1]
        elif row+1 == 16 or row+1 == 18:
            scale = [height-10, height+45, 1]
        elif row+1 == 23:
            scale = [height-40, height+10, 1]
        elif row+1 >= 25:
            scale = [0, 50, 1]
        else:
            scale = [height-35, height+20, 1]

else:
    raise NotImplementedError

print(store_heights_pandacsv(file, rows, heights))
