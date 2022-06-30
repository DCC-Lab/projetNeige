import pandas as pd
import numpy as np

def getdata_excel(file, row):
    """Read and return the data of an exel file

    file: str of the file
    row: int of the row we want, represent a picture
        
    return: array of 2 lines: 1-1 to the length of the row (representing the pixels); 2-the values in the excel of the row chosen
    """
    path = f"C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\Datainutile\\{file}.xlsx"
    matrix = np.array(pd.read_excel(path, skiprows=row-1, nrows=1))
    matrix = matrix[0][4:]
    pix = []
    for i in range(1, matrix.size+1):
        pix.append(i)
    return np.array([pix, matrix])

def calculate_slope(matrix):
    """Calculate the difference of color (transformed in float) between consecutive pixels

    matrix: array of 2 lines, the first one is the values concerning the height (pixel), the second concerning the intensity of the pixel
        
    return: the slope of the matrix values acording to the constant step between the first line of values
    """
    constant_step = matrix[0][1]-matrix[0][0]
    x = matrix[1][:]
    slope = np.diff(x)/constant_step
    slope = np.array([matrix[0][1:], slope])
    return slope

def find_height(slope, scale):
    """find the height of the snow according to the variation of color of the image (transformed in float)
    
    slope: array of 2 lines, the first one is the values concerning the height (pixel), the second concerning the slope of the pixel intensity
    scale: list of 3 elements [min, max, step(1 or -1), range where we know the height is within, change acording to the name of the file
        
    return: height in pixels of snow that is the streepestslope in the range chosen
    """
    streepest = slope[1][scale[0]]*scale[2]
    pix = scale[0]
    for i, value in enumerate(slope[1][scale[0]:scale[1]:scale[2]]):
        if value*scale[2] <= streepest:
            streepest = value*scale[2]
            pix = scale[0]+i*scale[2]
        else:
            continue
    print(scale[2], streepest)
    heightx = 0
    for i, value in enumerate(slope[1][pix::scale[2]]):
        if value*scale[2] >= 0:
            heightx = slope[0][pix+i*scale[2]]
            break
        elif value*scale[2]/streepest < 0.5:
            heightx = slope[0][pix+i*scale[2]]
            break
        else:
            continue
    return heightx

def store_heights_pandacsv(file, heights):
    """save the heights in a csv file

    file: str of the file 
    heights: list of the heights calculated

    return: dataframe pandas with 2 colums: 1-the date and hour; 2-the height associated
    save the dataframe in csv file
    """
    path = f"C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\Datainutile\\{file}.xlsx"
    dates = pd.read_excel(path, header=0, usecols='D')['TIME'].to_list()
    all_heights = {'date': dates, 'height': heights}
    all_heights = pd.DataFrame(all_heights)
    all_heights.to_csv(f"heightsA-{file[-3:]}2.csv", index=False)
    return all_heights


heights = []
#write the file name here:
file = 'PlotwithrefAlignIFM'

if file == 'PlotwithrefAlignIFM':
    scale = [1, 200, 1]
    for row in range(1, 87):
        if row in [26, 28] or row in list(range(71, 76)) or row in list(range(62, 68)):
            ranking = [526, 540, -1]
        elif row in [34, 35, 38]:
            heights.append(np.nan)
            print(row, minend)
            continue
        elif row in list(range(76, 87)):
            ranking = [535, 540, -1]
        else:
            ranking = [520, 540, -1]
        matrix = getdata_excel(file, row)
        slope = calculate_slope(matrix)
        minend = find_height(slope, ranking)
        height = find_height(slope, scale)
        heights.append(130-((minend-height)*10/40.8))
        print(row, minend, height)
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
    heights.append(0+59)
    for row in range(2, 18):
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

# print(store_heights_pandacsv(file, heights))
