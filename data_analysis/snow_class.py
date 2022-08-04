import datetime as dt
from datetime import timedelta as td
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

class Snow:
    """Contains various functions to manipulate dataframes who usually have values of type 'datetime'
    
    Attributes:
        df (dataframe): the main dataframe manipulated
        fit (dataframe): dataframe resulting from the fit of df
        trace (plotly.graph_objects.Scatter): scatter object to graph later on
        date_num (dataframe): dataframe with numerical values and dates. The 'date' column 
                            is the same as the one from df.
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
        self.fit, self.trace, self.date_num = None, None, None
    
    def display(self, object='df'):
        """Print all the dataframe specified

        object: str of the name of the dataframe among the 3 possible attributes we want to print ('df' by default)      
        """
        if object == 'df':
            data = self.df
        elif object == 'fit':
            data = self.fit
        elif object == 'date_num':
            data = self.date_num
        print(data.to_string())

    def find_date(self, dates):
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
            raise NotImplementedError(f'the type {type(window)} is not Implemented yet')
        return self.df

    def move_data(self, column, offset):
        """Modify the values of a column by adding a number and add these modified values in another column

        column: str of the name of the column we want to modify
        offset: float we want to add to the column selected

        return the modified df
        """
        self.df[f'{column}_moved'] = self.df[column] + offset
        return self.df

    def datetonum(self, min=None):
        """Create the attribute date_num with the 'date' column of df. More preciseley, it transforms the datetime object
        in numerical values, that is the number of hours elapsed since the reference (min) entered.
        
        min: date (datetime object) representing the reference for the numerical values

        return the attribute date_num
        """
        if min is None:
            min = self.df['date'].min()
        self.date_num = pd.DataFrame({'date': self.df['date'], 'date_norm': self.df['date']-min})
        self.date_num.reset_index(inplace = True, drop = True)
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
        # print(f'b = {parameters[1]}, A = {np.exp(parameters[1])}\nm = {parameters[0]}\nR^2 = {r}')
        self.fit = pd.concat([x_pred, y_pred], axis=1)
        return parameters

    def poly_fit(self, other, x='date', y='height_moved'):
        """Fit a 3rd degree polynomial function on the attribute df and save it in the attribute fit

        x: indepedent variable ('date' by default)
        y: dependant variable ('height_moved' by default)

        return the 4 parameters of the fit (y(=ax^3+bx^2+cx+d)
        """
        if self.date_num is None or self.date_num[x].equals(self.df[x]):
            raise ValueError('self.date_num is not accurate')
        self.df.reset_index(inplace = True, drop = True)
        self.fit = pd.DataFrame({x: self.date_num['date_num'], y: self.df[y]}).sort_values(by=x)
        poly = np.polyfit(self.fit[x], self.fit[y], 3)
        fct = np.poly1d(poly)
        self.fit = pd.DataFrame({x:other.date_num[x], y: fct(other.date_num['date_num'])})
        return poly

    def modify_column(self, other, x='date', y='height_moved'):
        """Change all the values of a column of the attribute df for those of another attribute df

        x: common column between the 2 df ('date' by default)
        y: column we want to change in the self.df with the values of the same column in other.df

        return the modified df
        """
        if other.fit[x].equals(self.df[x]):
            raise ValueError(f'the column {x} is not the same between self.df and other.fit')
        self.df[y] = other.fit[y].to_list()
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
                        hoverlabel={'namelength': 0}, xaxis=f'x{axis[0]}', yaxis=f'y{axis[1]}', line_color='red')
        return self.trace


if __name__ == "__main__":
    pass
