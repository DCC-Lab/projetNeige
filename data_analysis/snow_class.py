import datetime as dt
import os
import warnings
from datetime import timedelta as td

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.signal as ss
from scipy.optimize import curve_fit
from sigfig import round as rd
from sklearn.metrics import r2_score

from fast_projet_neige_sensor_corrector.corrector import corrector, getZenith

warnings.filterwarnings('ignore', category=UserWarning, module='sigfig')

class Snow:
    """Contains various functions to manipulate dataframes who usually have values of type 'datetime'
    
    Attributes:
        df (dataframe): the main dataframe manipulated
        name (str): the name of the file
        fit (dataframe): dataframe resulting from the fit of df
        trace (plotly.graph_objects.Scatter): scatter object to graph later on
        date_num (dataframe): dataframe with numerical values and dates. The 'date' column 
                            is the same as the one from df.
        method (dictionary): methods used according to their category (as keys) and the name of the method (as values)
        datestocorrect (list): list of dates to correct
        df_norm (dataframe): list of dictionaries with the values of the dataframe df normalized and the info
                            about the normalization
    """

    def __init__(self, path, date=True):
        """Initialize the attributes of the class to None execept for df who comes from the path
        
        path: str of the path of the csv file who contains the dataframe
        date: bool who convert the values of the 'date' column to datetime objects if True (True by default)
        """
        if date:
            self.df = pd.read_csv(path, parse_dates=['date'])
        else:
            self.df = pd.read_csv(path)
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.fit, self.trace, self.date_num, self.method= None, None, None, {}
        self.dates_tocorrect, self.df_norm  = [], []
    
    def display(self, object='df'):
        """Print all of the dataframe specified

        object: str of the name of the dataframe among the 3 possible attributes we want to print ('df' by default)      
        """
        if object == 'df':
            data = self.df
        elif object == 'fit':
            data = self.fit
        elif object == 'date_num':
            data = self.date_num
        elif object == 'df_norm':
            data = self.df_norm[-1]['df']
            for dic in self.df_norm[:-1]:
                print(dic['df'].to_string())
        else:
            raise NotImplementedError(f'the method with the attribute {object} is not implemented yet')
        print(data.to_string())

    def find_dates(self, dates):
        """Truncate the attribute df to have only the dates wanted

        dates: list of string of the dates we want to keep (string format: '%Y-%m-%d %H:%M:%S')
            (ex. ['2021-01', '2021-03-11 07:'] represent all the values from January 2021 and those taken the hour following 7 a.m. on March 11 2021)
        
        return the modified df 
        """
        self.df['date'] = self.df['date'].astype(str)
        all_df = pd.DataFrame()
        for date in dates:
            df1 = self.df.loc[(date in datetime for datetime in self.df['date'])]
            all_df = pd.concat([all_df, df1], axis=0)
        self.df = all_df
        self.df['date'] = self.df['date'].apply(pd.to_datetime)
        self.df.reset_index(inplace = True, drop = True)
        if 'find_dates' not in self.method:
            self.method['find_dates'] = [dates]
        else:
            self.method['find_dates'].append(dates)
        return self.df

    def truncate_col(self, column, window, keepnan=True):
        """Truncate the attribute df according to the values of a certain column

        column: str of the column we want to truncate
        window: a list of values we want to keep or a tuple of 2 values being the minimum and maximum values limiting the interval of interest
        keepnan: bool to determine if we want to keep or not the NaN values (Yes/True by default)

        return the modified df
        """
        if type(window) is tuple:
            self.df = self.df.loc[((self.df[column] >= window[0]) & (self.df[column] <= window[1])) | (np.isnan(self.df[column]) & keepnan)]
        elif type(window) is list:
            self.df = self.df.loc[(((i in window) or (np.isnan(i) & keepnan)) for i in self.df[column])]
        else:
            raise NotImplementedError(f'the type {type(window)} is not implemented yet')
        if 'truncate' not in self.method:
            self.method['truncate'] = [{column: window, 'keepnan': keepnan}]
        else:
            self.method['truncate'].append({column: window, 'keepnan': keepnan})
        return self.df

    def modify_data(self, column, offset):
        """Modify the values of a column by adding a number and add these modified values in another column

        column: str of the name of the column we want to modify
        offset: float we want to add to the column selected

        return the modified df
        """
        self.df[f'{column}_moved'] = self.df[column] + offset
        if 'modify_data' not in self.method:
            self.method['modify_data'] = [{column: offset}]
        else:
            self.method['modify_data'].append({column: offset})
        return self.df

    def datetonum(self, min=None):
        """Create the attribute date_num with the 'date' column of df. More precisely, it transforms the datetime object
        in numerical values, that is the number of hours elapsed since the reference (min) entered. It also creates tow 
        new columns with the date and the hour of the day.
        
        min: date (datetime object) representing the reference for the numerical values

        return the attribute date_num
        """
        if min is None:
            min = self.df['date'].min()
        self.date_num = pd.DataFrame({'date': self.df['date'], 'date_norm': self.df['date']-min})
        # self.date_num.reset_index(inplace = True, drop = True)
        self.date_num['day'], self.date_num['hour'] = self.date_num["date"].dt.day, self.date_num['date'].dt.hour
        self.date_num["date_num"] = self.date_num["date_norm"].dt.days*24+self.date_num["date_norm"].dt.seconds/3600        
        self.date_num.pop('date_norm')
        return self.date_num

    def fit_exp(self, x='height_moved', y='irr'):
        """Fit of an exponential function on the attribute df and save it in the attribute fit

        x: indepedent variable ('height_moved' by default)
        y: dependant variable ('irr' by default)

        return the 2 parameters of the fit (y(log)=mx+b)
        """
        self.fit = pd.DataFrame({x: self.df[x], y: self.df[y]}).sort_values(by=x)
        def fitfunction(x, m, b):
            return m*x+b
        self.fit[y] = np.log(self.fit[y])
        self.fit.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.fit = self.fit.dropna()
        parameters, covariance = curve_fit(fitfunction, self.fit[x], self.fit[y])
        x_pred = pd.DataFrame({x:list(i for i in np.arange(0.5*round(min(self.fit[x])/0.5), 0.5*round(max(self.fit[x])/0.5)+0.5, 0.5))})
        y_pred = np.exp(fitfunction(x_pred, *parameters)).rename(columns={x:f'{y}_pred'})
        r = r2_score(self.fit[y], fitfunction(self.fit[x], *parameters))
        self.fit = pd.concat([x_pred, y_pred], axis=1)
        if 'fit' not in self.method:
            self.method['fit'] = [{'type':'decrease exponential', 'x':x, 'y':y, 'formula':f'y={parameters[0]}x+{parameters[1]}', 'r^2':r}]
        else:
            self.method['fit'].append({'type':'decrease exponential', 'x':x, 'y':y, 'formula':f'y={parameters[0]}x+{parameters[1]}', 'r^2':r})
        return parameters

    def poly_fit(self, other, x='date', y='height_moved'):
        """Fit a 3rd degree polynomial function on the attribute df and save it in the attribute fit

        x: indepedent variable ('date' by default)
        y: dependant variable ('height_moved' by default)

        return the 4 parameters of the fit (y=ax^3+bx^2+cx+d)
        """
        if self.date_num is None or self.date_num[x].equals(self.df[x]) is False:
            raise ValueError('self.date_num is not accurate')
        self.df.reset_index(inplace = True, drop = True)
        self.fit = pd.DataFrame({x: self.date_num['date_num'], y: self.df[y], 'day': self.date_num['day'], 'hour': self.date_num['hour']}).sort_values(by=x)
        days = []
        df_fit = pd.DataFrame()
        for day in self.fit['day']:
            if day in days:
                continue
            df = self.fit.loc[(self.fit['day'] == day) & (self.fit['hour'] >= 7) & (self.fit['hour'] <= 20)]
            dates = other.date_num.loc[other.date_num['day'] == day]
            poly = np.polyfit(df[x], df[y], 3)
            fct = np.poly1d(poly)
            df_fit = pd.concat([df_fit, pd.DataFrame({x: dates[x], y: fct(dates['date_num'])})], axis=0)
            days.append(day)
        self.fit = df_fit
        if 'fit' not in self.method:
            self.method['fit'] = [{'type':'polynomial-3', 'x':x, 'y':y, 'fomrula':f'y={poly[0]}x^3+{poly[1]}x^2+{poly[2]}x+{poly[3]}'}]
        else:
            self.method['fit'].append({'type':'polynomial-3', 'x':x, 'y':y, 'fomrula':f'y={poly[0]}x^3+{poly[1]}x^2+{poly[2]}x+{poly[3]}'})
        return self.fit

    def switch_columns(self, other, x='date', y='height_moved'):
        """Change all the values of a column of the attribute df for those of another attribute df

        x: common column between the 2 df ('date' by default)
        y: column we want to change in the self.df with the values of the same column in other.df

        return the modified df
        """
        if other.fit[x].equals(self.df[x]) is False:
            raise ValueError(f'the column {x} is not the same between self.df and other.fit')
        self.df[y] = other.fit[y].to_list()
        if 'switch_columns' not in self.method:
            self.method['switch_columns'] = [{'x':x, 'y':y}]
        else:
            self.method['switch_columns'].append({'x':x, 'y':y})
        return self.df

    def save(self, name, object='df'):
        """Save the dataframe specified
        
        name: str of the name of the csv file saved
        object: str of the name of the dataframe among the 3 possible attributes we want to print ('df' by default)
        """
        if object == 'df':
            self.df.to_csv(f'{name}.csv', index=False)
        elif object == 'fit':
            self.fit.to_csv(f'{name}.csv', index=False)
        elif object == 'date_num':
            self.date_num.to_csv(f'{name}.csv', index=False)
        elif object == 'df_norm':
            for dic in self.df_norm:
                dic['df'].to_csv(f'{name}_norm{dic["name_ref"][-4:]}.csv', index=False)
        else:
            raise ValueError(f'{object} is not a valid object')

    def make_fig(self, x, y, name=None, color=None, size=None, axis = ['', ''], mode='markers', colorscale='haline_r', cmin=None, cmax=None):
        """Create the attribute trace by initiating a scatter object
        
        x: str of the column in the dataframe representing the independent variable
        y: str of the column in the dataframe representing the dependent variable
        name: name of the scatter (None by default)
        color: str of the column of the file which separates by color the data (None by default)
        size: str of the column of the file which separates by size the data (None by default)
        axis: list of string of ints who represent the name of the axis (['', ''] by default)
        mode: mode of the points in the scatter ('markers' by default)
        colorscale: name of the colorscale we want to use ('haline_r' by default)
        cmin: minimum value of the colorscale (minimum value of the date by default)
        cmax: maximum value of the colorscale (maximum value of the date by default)
        
        return the attribute trace
        """
        liste, hovertext = [], ""
        if mode == "markers":
            data = self.df
        elif mode == 'lines':
            data = self.fit
        for i, col in enumerate(data.columns):
            df = data[col].to_list()
            liste.append(df)
            a = ':.3g' if col != 'date' else ''
            hovertext += f"<b>{col}:</b> %{{customdata[{i}]{a}}} <br>"
        all_data = np.stack(tuple(liste), axis=-1)
        if mode == 'markers':
            color = data[color] if color is not None else None
            size = data[size] if size is not None else None
            self.trace = go.Scatter(x=data[x], y=data[y], mode=mode, marker_color=color, 
                        marker_size = size, name=name, customdata=all_data, hovertemplate=hovertext, 
                        hoverlabel={'namelength': 0}, xaxis=f'x{axis[0]}', yaxis=f'y{axis[1]}', 
                        marker=dict(line=dict(width=0.2, color='black'), colorscale=colorscale, cmin=cmin, cmax=cmax))
        elif mode == 'lines':
            self.trace = go.Scatter(x=data[x], y=data[y], mode=mode, name=name, customdata=all_data, hovertemplate=hovertext, 
                        hoverlabel={'namelength': 0}, xaxis=f'x{axis[0]}', yaxis=f'y{axis[1]}', line_color=color)
        return self.trace

    def rectify_data(self, x='irr', y='date', diffuse=None):
        """Rectify the data according to the diffusion throughout the day
        
        x: str of the column in the dataframe representing the independent variable ('irr' by default)
        y: str of the column in the dataframe representing the dependent variable ('date' by default)
        diffuse: dict of the days and boolean of their diffusion (None by default). If None, the diffusion
        is determined from the dataframe with the column 'sun level' (True for the days with sun level >= 3
        and False for the others)
        
        return the corrected dataframe df
        """
        c = corrector()
        days, default_diffuse = [], {}
        df_corr = pd.DataFrame()
        for day in self.df['day']:
            if day in days:
                continue
            df = self.df.loc[self.df['day'] == day]
            if diffuse is None:
                difbool = False if df['sun level'].iloc[0] >= 3 else True
                default_diffuse[day] = difbool
            else:
                difbool = diffuse[day]
            correctedData = c.correctData(df[x].tolist(), df[y].values.astype('datetime64[s]').tolist(), diffuse=difbool)
            df_corr = pd.concat([df_corr, pd.DataFrame({y: df[y], x: correctedData})], axis=0)
            days.append(day)
        self.df[x], self.df[y] = df_corr[x], df_corr[y]
        diffuse = default_diffuse if diffuse is None else diffuse
        if 'rectify_data' not in self.method:
            self.method['rectify_data'] = [{'x': x, 'y': y, 'diffuse': diffuse}]
        else:
            self.method['rectify_data'].append({'x': x, 'y': y, 'diffuse': diffuse})
        return self.df

    def remove_highangles(self, x='date', max_angle=80):
        """Remove the data with high angles
        
        x: str of the column of the dates ('date' by default)
        max_angle: maximum angle of the sun accepted (80 by default)
        
        return the corrected dataframe df
        """
        df = self.df
        for date in df[x].values.astype('datetime64[s]').tolist():
            if getZenith(date) >= max_angle:
                self.df = self.df.drop(self.df[self.df[x] == date].index)
        if 'remove_angles' not in self.method:
            self.method['remove_angles'] = [f'angle({x})>={max_angle}']
        else:
            self.method['remove_angles'].append(f'angle({x})>={max_angle}')
        return self.df

    def shift_data(self, column, offset):
        """Shift the data to the "left" or "up" on a file according a certain offset

        column: str of the name of the column we want to move
        offset: int representing the number of data points removed at the beginning of the set, thus creating the shift
        
        return dataframe and update csv
        """
        values = self.df[column].to_list()
        values = values[offset:]
        for _ in range(offset):
            values.append(np.median(values[-3:]))
        self.df[f'{column} shifted'] = values
        if 'shift_data' not in self.method:
            self.method['shift_data'] = [{column: offset}]
        else:
            self.method['shift_data'].append({column: offset})
        return self.df

    def classify_dates(self):
        """Add two columns to the attribute df to add a specific id for each day and another for each 
        half hour independetly of the day. Also add a column of the day and another of the hour and 
        half hour.

        return the dataframe df with the new columns
        """
        self.df["month"], self.df["day"], self.df["hour"], self.df["minu"] = self.df["date"].dt.month, self.df["date"].dt.day, self.df["date"].dt.hour, self.df["date"].dt.minute//30
        self.df.month.where(self.df.loc[:, "month"] != 12, 0, inplace=True)
        self.df.minu.where(self.df.loc[:, "minu"] != 1, 5, inplace=True)
        self.df.is_copy = False
        self.df['id-day'], self.df['hour-min'] = (self.df["month"]+self.df["day"]/100), (self.df["hour"]+self.df["minu"]/10)
        self.df['id-hour'] = -abs(self.df['hour-min']-13)+7 # formula of the absolute value function where 13h is the horizontal center and the y values are arbitrary units
        for col in ['hour', 'minu']:
            self.df.pop(col)
        return self.df

    def add_id(self, name_id, id):
        """Add a column of the same id to all the data of the attribute df
        
        name_id: name of the column we add
        id: str or value of the id
        
        return the dataframe df with the new column
        """
        self.df[name_id] = [id for _ in range(self.df.shape[0])]
        return self.df

    def stripcolumns(self, columns):
        """Delete columns of the attribute df
        
        columns: list of the name of the columns we want to delete

        return the dataframe and update the csv
        """
        for col in columns:
            try:
                self.df.pop(col)
                if 'stripcolumns' not in self.method:
                    self.method['stripcolumns'] = [col]
                else:
                    self.method['stripcolumns'].append(col)
            except KeyError:
                print(f"{col} not in the dataframe")
                pass
        return self.df

    def add_luminosity(self, pathlum='C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\luminosity.csv'):
        """Add a column representing the sun level on the attribute df where the dates are the 
        date and the time in the same column

        pathlum: str of the file with the sun level according to the date

        return the dataframe and update it
        """
        dflum = pd.read_csv(pathlum)
        liste, dates = [], dflum['date'].to_list()
        for date in self.df['date']:
            if date[:10] in dates:
                liste.append(dflum.loc[dflum['date'] == date[:10]]['sun level'].to_list()[0])
            else:
                liste.append(np.nan)
        self.df['sun level'] = liste
        return self.df

    def norm_max(self, column):
        """Normalize irradiance data according to the max value of the data
        
        column: str of the column we want to normalize with itself

        return the dataframe df with the new column
        """
        ira = self.df[column]
        max_ira = max(ira)
        norm_ira = []
        for value in ira:
            norm_ira.append(value/max_ira)
        self.df[f'{column} self-norm'] = norm_ira
        if 'self-norm' not in self.method:
            self.method['self-norm'] = [{'type': 'max', 'column': column}]
        else:
            self.method['self-norm'].append({'type': 'max', 'column': column})
        return self.df

    def norm_calibrate(self, column, date='2020-12-12 10:25:15'):
        """Normalize irradiance data according to a certain value of the data
        
        column: str of the column we want to normalize with itself
        date: str of the date the certain value is ('2020-12-12 10:25:15' by default)

        return the dataframe df with the new column
        """
        ira = self.df[column]
        indexref = self.df.loc[self.df['date'] == date].index[0]
        ref_ira = np.mean(ira.loc[indexref-1:indexref+1])
        norm_ira = []
        for value in ira:
            norm_ira.append(value/(ref_ira*83))
        self.df[f'{column} self-norm'] = norm_ira
        if 'self-norm' not in self.method:
            self.method['self-norm'] = [{'type': 'calibrate', 'column': column, 'date': date}]
        else:
            self.method['self-norm'].append({'type': 'calibrate', 'column': column, 'date': date})
        return self.df

    def norm_i0(self, other, column):
        """Normalize data according to a certain reference (i0) who have the same timestamp
        
        column: str of the column we want to use to normalize

        return the efficienty of the normalization (number of values greater than 2 and the maximum value)
        and append the dataframe df normalized with the info of normalization in the attribute df_norm
        """
        # find corresponding reference
        real_dates, n = [], 1
        dates = self.df.date.tolist()
        try:
            ref = other.df.loc[other.df['date'] == dates, column]
            if self.df.shape[0] != ref.shape[0]:
                raise Exception
            print(49)
            real_dates = dates
        except Exception as err:
            ref = pd.DataFrame()
            for i, datehour in enumerate(other.df['date']):
                if (i+1) >= other.df.shape[0]*n/5:
                    print((i+1)/other.df.shape[0]*50)
                    n +=1
                if datehour in dates:
                    ref = pd.concat([ref, other.df.loc[other.df['date'] == datehour, column[1]]], axis=0)
                    real_dates.append(datehour)
        ira = self.df.loc[self.df['date'] == real_dates, column]
        if ira.shape[0] != ref.shape[0]:
            raise ValueError('the two dataframe are not the same size')
        norm_ira, eff, n = [], [], 1
        # calculate the normalized irradiance
        for i in range(ira.shape[0]):
            if (i+1) >= ira.shape[0]*n/5:
                print(50+(i+1)/ira.shape[0]*50)
                n += 1
            if ref[i] == 0:
                norm_ira.append(0)
            else:
                norm_ira.append(ira[i]/ref[i])
                if ira[i]/ref[i] > 2 or ira[i]/ref[i] < -1:
                    eff.append(ira[i]/ref[i])
        # store the result
        new_col = pd.DataFrame({f'{column} i0-norm':norm_ira})
        dicto = {'name_test': self.name, 'name_ref': other.name, 'df': pd.concat([self.df, new_col], axis=1)}
        self.df_norm.append(dicto)
        if len(eff) == 0:
            a, b, c = len(eff), max(norm_ira), min(norm_ira)
        else:
            a, b, c = len(eff), max(eff), min(eff)
        if 'i0-norm' not in self.method:
            self.method['i0-norm'] = [{'type': 'same time', 'column': column}]
        else:
            self.method['i0-norm'].append({'type': 'same time', 'column': column})
        return (a, b, c)

    def norm_i0_differenttime(self, other, columns, window=5, order=0, how=['mean', 'median']):
        """Normalize data according to a certain reference (i0) who don't have the same timestamp 
        
        columns: list of the name of the columns we want (first the one we want to normalize, second the reference)
        window: int of the number of minutes that we use for the mean/median (5 by default)
        order: int between 0 and 1 -- 1 represent the (rolling) mean/median at the right and 0 at the center (0 by default)
        how: list of the name of the method(s) used for the (rolling) ""mean/median"" (both by default)

        return the last element of the attribute df_norm
        """
        if (how not in ['mean', 'median'] and how != ['mean', 'median']) or (order not in [0, 1]):
            raise NotImplementedError('the method is not implemented')
        j, n = 0, 0
        rowref = other.df.shape[0]
        rowstu = self.df.shape[0]
        dicto = {}
        for date in other.df['date']:
            dicto[date] = []
        for i in range(rowstu):
            s1 = self.df['date'][i]
            date1 = dt.strptime(s1, '%Y-%m-%d %H:%M:%S')
            if (i+1) >= rowstu*n/10:
                    print((i+1)/rowstu*100)
                    n +=1
            while True:
                if j >= rowref:
                    break
                s2 = other.df['date'][j]
                date2 = dt.strptime(s2, '%Y-%m-%d %H:%M:%S')
                delta = (date2 - date1).total_seconds()
                if order == 0:
                    if delta < -window*60:
                        j += 1
                    elif delta <= window*60 and delta >= -window*60:
                        dicto[s2].append(self.df[columns[0]][i])
                        break
                    else:
                        break
                else:
                    if delta < 0:
                        j += 1
                    elif delta <= window*60 and delta >= 0:
                        dicto[s2].append(self.df[columns[0]][i])
                        break
                    else:
                        break
            if j > rowref:
                break
        data = pd.DataFrame({'date': dicto.keys(), 'ref':other.df[columns[1]], 'list': dicto.values()})
        for method in how:
            values = []
            eff = []
            for i, liste in enumerate(data['list']):
                if liste != [] and data['ref'][i] != 0:
                    if method == 'mean':
                        value = np.mean(liste/data['ref'][i])
                    else:
                        value = np.median(liste/data['ref'][i])
                    values.append(value)
                    if value > 2  or value < -1:
                        eff.append(value)
                else:
                    values.append(np.nan)
            data[f'{method}_norm {window}={order}'] = values
            if len(eff) == 0:
                print(len(eff), max(values), min(values))
            else:
                print(len(eff), max(eff), min(eff))
        data.pop('ref')
        data.pop('list')
        self.df_norm.append({'name_test': self.name, 'name_ref': other.name, 'df': data})
        if 'i0-norm' not in self.method:
            self.method['i0-norm'] = [{'type': 'different time', 'column': columns, 'window': f'{window}min', 'order': order, 'how': how}]
        else:
            self.method['i0-norm'].append({'type': 'different time', 'column': columns, 'window': f'{window}min', 'order': order, 'how': how})
        return self.df_norm[-1]

    def norm_rescale(self, column, columref):
        """Normalize data according to the max value of another column
        because the column is too noised
        
        column: str of the column we want to normalize
        columref: column who has the maximum at the index we want

        return the attribute df_norm
        """
        for dic in self.df_norm:
            test, ref = dic['df'][column], dic['df'][columref]
            indexref = dic['df'].loc[ref == max(ref)].index[0]
            max_ira = test.loc[indexref]
            if pd.isna(max_ira):
                raise ValueError(f"the value at the {indexref}th position of the column '{column}' is NaN and therefore cannot be used for the normalization")
            norm_ira, eff = [], []
            for value in test:
                norm_ira.append(value/max_ira)
                if value/max_ira > 2 or value/max_ira < -1:
                    eff.append(value/max_ira)
            dic['df'][f'{column} std-norm'] = norm_ira
            if len(eff) == 0:
                print(len(eff), max(norm_ira), min(norm_ira))
            else:
                print(len(eff), max(eff), min(eff))
        if 'std-norm' not in self.method:
            self.method['std-norm'] = [{'column': column, 'columnref': columref}]
        else:
            self.method['std-norm'].append({'column': column, 'columnref': columref})
        return self.df_norm

    def denoise_mea(self, column, order=1, window=7, object='df_norm'):
        """Denoise by a moving average a column of a certain attribute (df or df_norm)
        
        column: str of the name of the column we want to denoise
        order: 1 or -1, way of the moving average (left to right or the opposite) (1 by default)
        window: int of the number of minutes we use for the mean (7 minutes by default)
        object: str of the name of the attribute we want to denoise (df_norm by default)

        return the attribute denoised
        """
        dico = {1: 'L', -1: 'R'}
        def manip(data):
            y, dates = data[column].to_list(), data['date'].to_list()
            df = pd.DataFrame({'date': dates[::order], f'{column}': y[::order]})
            w = df.rolling(f'{window}T', on='date').mean()
            data[f"{column}_denoised{dico[order]}"] = w.iloc[:, 1].to_list()[::order]
            return data
        if object == 'df':
            self.df = manip(self.df)
        elif object == 'df_norm':
            for dic in self.df_norm:
                dic['df'] = manip(dic['df'])
        else:
            raise NotImplementedError(f'the method with the attribute {object} is not implemented yet')
        if 'denoise' not in self.method:
            self.method['denoise'] = [{'type': 'mean', 'column': column, 'order': order, 'window': f'{window}min'}]
        else:
            self.method['denoise'].append({'type': 'mean', 'column': column, 'order': order, 'window': f'{window}min'})

    def denoise_exp(self, column, order=1, window=7, object='df_norm'):
        """Denoise by a moving exponential average a column of a certain attribute (df or df_norm)
        
        column: str of the name of the column we want to denoise
        order: 1 or -1, way of the moving average (left to right or the opposite) (1 by default)
        window: int of the number of minutes we use for the mean (7 minutes by default)
        object: str of the name of the attribute we want to denoise (df_norm by default)

        return the attribute denoised
        """
        dico = {1: 'L', -1: 'R'}
        def manip(data):
            y, dates = data[column].to_list(), data['date'].to_list()
            df = pd.DataFrame({'date': dates[::order], f'{column}': y[::order]})
            w = df[f'{column}'].ewm(halflife=td(minutes=window*order), times=df['date'], ignore_na=True).mean()
            w = w.to_list()
            data[f"{column}_denoised{dico[order]}"] = w[::order]
            return data
        if object == 'df':
            self.df = manip(self.df)
        elif object == 'df_norm':
            for dic in self.df_norm:
                dic['df'] = manip(dic['df'])
        else:
            raise NotImplementedError(f'the method with the attribute {object} is not implemented yet')
        if 'denoise' not in self.method:
            self.method['denoise'] = [{'type': 'exponential mean', 'column': column, 'order': order, 'window': f'{window}min'}]
        else:
            self.method['denoise'].append({'type': 'exponential mean', 'column': column, 'order': order, 'window': f'{window}min'})

    def denoise_med(self, column, order=-1, window=15, object='df_norm'):
        """Denoise by a moving median a column of a certain attribute (df or df_norm)
        
        column: str of the name of the column we want to denoise
        order: 1 or -1, way of the moving median (right to left or the opposite) (default -1)
        window: int of the number of minutes we use for the mean (15 minutes by default)
        object: str of the name of the attribute we want to denoise (df_norm by default)

        return the attribute denoised
        """
        dico = {1: 'L', -1: 'R'}
        def manip(data):
            data = data.sort_values(by='date', ignore_index=True) # date must be monotonic
            y, dates = data[column].to_list(), data['date'].to_list()
            df = pd.DataFrame({'date': dates[::order], f'{column}': y[::order]}, index=data.index)
            w = df.rolling(f'{window}T', on='date').median()
            data[f"{column}_denoised{dico[order]}"] = w.iloc[:, 1].to_list()[::order]
            data.sort_index()
            return data
        if object == 'df':
            self.df = manip(self.df)
        elif object == 'df_norm':
            for dic in self.df_norm:
                dic['df'] = manip(dic['df'])
        else:
            raise NotImplementedError(f'the method with the attribute {object} is not implemented yet')
        if 'denoise' not in self.method:
            self.method['denoise'] = [{'type': 'median', 'column': column, 'order': order, 'window': f'{window}min'}]
        else:
            self.method['denoise'].append({'type': 'median', 'column': column, 'order': order, 'window': f'{window}min'})

    def check_symmetry(self, y='irr_ro_uns', days=None):
        """Calculate the mean of sknewness of the column 'irr' of df for the specified days

        y: str of the name of the column we want to check (irr_ro_uns by default)
        days: list of the day(s) we want to check the symmetry (all by default)

        return the mean of sknewness
        """
        if self.date_num is None or self.date_num['date'].equals(self.df['date']) is False:
            raise ValueError('self.date_num is not accurate')
        df = pd.concat([self.df, self.date_num['day']], axis=1)
        if days is None:
            a, all = df['day'][0], df['day'][1:]
        elif len(days) == 1:
            return df.loc[df['day'] == days[0]][y].skew(axis=0, skipna=True)
        else:
            a, all = days[0], days[1:]
        sum, days = 0, 0
        for b in all:
            if a != b:
                res = df.loc[df['day'] == a][y].skew(axis=0, skipna=True)
                sum, days = res+sum, days+1
            a = b
        res = df.loc[df['day'] == b][y].skew(axis=0, skipna=True)
        sum, days = res+sum, days+1
        return sum/days

    def dates_problem(self, column='irr_ro_uns'):
        """Find the problematic dates of the attribute df. In other words, check if the values of a day start by decreasing.

        column: str of the name of the column we want to check (irr_ro_uns by default)

        return the list of the dates corresponding to the actual beginning of the day 
        """
        df = pd.DataFrame({f'{column}': self.df[column].to_list()}, index=self.df['date'].to_list())
        date1 = df.index[0]
        self.dates_tocorrect = []
        for i, date2 in enumerate(df.index[1:]):
            if date1[:10] != date2[:10]:
                a = df[column].iloc[i+1:i+4].mean()
                b = df[column].iloc[i+4:i+7].mean()
                if (a > b and a-b > 0.0002) or date2[:10] == '2021-04-07':
                    day_am = df.loc[(df.index >= date2) & (df.index < f'{date2[:10]} 12{date2[13:]}')]
                    if day_am.empty:
                        continue
                    dmin = day_am[column].astype(float).idxmin()
                    self.dates_tocorrect.append(dmin)
            date1 = date2
        return self.dates_tocorrect

    def correct_data(self, column='irr_ro_uns'):
        """Replace the problematic dates to the proper day (the day before)

        column: str of the name of the column we want to correct (irr_ro_uns by default)

        return the new dataframe and save it if all the dates were modified only once
            if not raise a ValueError
        """
        df = pd.DataFrame({f'{column}': self.df[column].to_list()}, index=self.df['date'].astype(str).to_list())
        date1 = df.index[0]
        if self.dates_tocorrect == []:
            dates = pd.read_csv('Datainutile\\datestocorrect.csv')
            dates = dates.astype(str)
            dates['day'] = [date[:10] for date in dates['date']]
            dates = dates.loc[(dates['day'] >= date1[:10]) & (dates['day'] <= df.index[-1][:10])]
            self.dates_tocorrect = dates['date'].to_list()
        n, count, x, dates = 1, 0, len(self.dates_tocorrect), self.dates_tocorrect
        for i, date2 in enumerate(df.index[1:]):
            if date1[:10] != date2[:10]:
                for dmin in self.dates_tocorrect:
                    if date2[:10] == dmin[:10]:
                        wrongdates = df.loc[date2:dmin].iloc[:-1]
                        if wrongdates.empty:
                            continue
                        wrongstart = dt.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
                        realstart = dt.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
                        for i, date in enumerate(wrongdates.index):
                            realdate = dt.datetime.strftime((dt.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')-wrongstart+realstart+td(seconds=60)), '%Y-%m-%d %H:%M:%S')
                            self.df.loc[self.df['date'] == date, 'date'] = realdate
                        count += 1
                        dates.remove(dmin)
                        continue
            date1 = date2
            if (i+1) >= df.shape[0]*n/10:
                print((i+1)/df.shape[0]*100)
                n += 1
        if count != x or count == 0 or x == 0 or len(dates) != 0:
            raise ValueError("the correction did not work, see the lenght of the variable 'dates'")
        if 'correct_data' not in self.method:
            self.method['correct_data'] = [{'column': column, 'dates': self.dates_tocorrect}]
        else:
            self.method['correct_data'].append({'column': column, 'dates': self.dates_tocorrect})
        return self.df

    def remove_saturation(self, column):
        """Change to 'NaN' values the saturated one (max) of the attribute df
        
        column: str of the name of the column we want to correct

        return the dataframe df with the new column unsaturated
        """
        self.df[f'{column}_uns'] = self.df[column]
        data  = self.df.loc[round(self.df[f'{column}_uns'], 2) == round(max(self.df[f'{column}_uns']), 2), f'{column}_uns']
        if data.shape[0] >= 2:
            self.df.loc[round(self.df[f'{column}_uns'], 2) == round(max(self.df[f'{column}_uns']), 2), f'{column}_uns'] = np.nan
        return self.df

    def round_data(self, column, sigfigs=3, object='df'):
        """Round a specific column of a dataframe to a specific number of significant figures
        
        column: str of the name of the column we want to round
        sigfigs: int of the number of significant digit we want to keep
        object: str of the name of the object we want to modify (df by default)

        return the attribute rounded
        """
        def manip(data):
            liste = []
            for i in data[column]:
                if pd.isna(i):
                    liste.append(np.nan)
                else:
                    liste.append(rd(i, sigfigs = sigfigs))
            data[f'{column}_ro'] = liste
            return data
        if object == 'df':
            self.df =  manip(self.df)
        elif object == 'df_norm':
            for dic in self.df_norm:
                dic['df'] = manip(dic['df'])
        else:
            raise NotImplementedError(f'the method with the attribute {object} is not implemented yet')
        if 'round_data' not in self.method:
            self.method['round_data'] = [{'column': column, 'sigfigs': sigfigs}]
        else:
            self.method['round_data'].append({'column': column, 'sigfigs': sigfigs})

if __name__ == "__main__":
    pass
