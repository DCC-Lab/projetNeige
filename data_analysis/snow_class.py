import os
import datetime as dt
from datetime import timedelta as td
import numpy as np
import pandas as pd
import scipy.interpolate as sint
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
import plotly.graph_objects as go
from sklearn.preprocessing import scale
import matplotlib.dates as mdates

class Snow:
    def __init__(self, path, date=True):
        if date:
            self.df = pd.read_csv(path, parse_dates=['date'])
        else:
            self.df = pd.read_csv(path)
        self.fit, self.trace, self.date_num = None, None, None
    
    def display(self, object='df'):
        if object == 'df':
            data = self.df
        elif object == 'fit':
            data = self.fit
        print(data.to_string())

    def find_date(self, dates):
        self.df['date'] = self.df['date'].astype(str)
        all_df = pd.DataFrame()
        for date in dates:
            df1 = self.df.loc[(date in datetime for datetime in self.df['date'])]
            all_df = pd.concat([all_df, df1], axis=0)
        self.df = all_df
        self.df['date'] = self.df['date'].apply(pd.to_datetime)
        return self.df

    def truncate_col(self, column, window, keepnan=True):
        if type(window) is tuple:
            self.df = self.df.loc[((self.df[column] >= window[0]) & (self.df[column] <= window[1])) | (np.isnan(self.df[column]) & keepnan)]
        elif type(window) is list:
            self.df = self.df.loc[(((i in window) or (np.isnan(i) & keepnan)) for i in self.df[column])]
        else:
            raise NotImplementedError(f'the type {type(window)} is not Implemented yet')
        return self.df

    def move_data(self, column, offset):
        self.df[f'{column}_moved'] = self.df[column] + offset
        return self.df

    def datetonum(self, min=None):
        if min is None:
            min = self.df['date'].min()
        self.date_num = pd.DataFrame({'date': self.df['date'], 'date_norm': self.df['date']-min})
        self.date_num.reset_index(inplace = True, drop = True)
        self.date_num["date_num"] = self.date_num["date_norm"].dt.days*24+self.date_num["date_norm"].dt.seconds/3600
        self.date_num.pop('date_norm')
        return self.date_num

    def fit_exp(self, x='height_moved', y='irr'):
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
        if self.date_num is None or self.date_num[x].equals(self.df[x]):
            raise ValueError('self.date_num is not accurate')
        self.df.reset_index(inplace = True, drop = True)
        self.fit = pd.DataFrame({x: self.date_num['date_num'], y: self.df[y]}).sort_values(by=x)
        poly = np.polyfit(self.fit[x], self.fit[y], 3)
        fct = np.poly1d(poly)
        self.fit = pd.DataFrame({x:other.date_num[x], y: fct(other.date_num['date_num'])})
        return poly

    def modify_column(self, other, x='date', y='height_moved'):
        if other.fit[x].equals(self.df[x]):
            raise ValueError(f'the column {x} is not the same between self.df and other.fit')
        self.df[y] = other.fit[y].to_list()
        return self.df

    def save(self, newname, object='df'):
        if object == 'df':
            self.df.to_csv(f'{newname}.csv', index=False)
        elif object == 'fit':
            self.fit.to_csv(f'{newname}.csv', index=False)

    def make_fig(self, x, y, name=None, color=None, size=None, axis = ['', ''], mode='markers', colorscale='haline_r', cmin=None, cmax=None):
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