import datetime as dt
import os
import warnings
import webbrowser

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from manipfiles import fit_expo, get_night_datetime, truncate
from snow_class import SnowData

warnings.filterwarnings('ignore', category=RuntimeWarning)

def onegraph(path, axis, color=None, size=None, realnames=None, title=None, log=False, scale=[None, None]):
    """Make a plotly scatter with a csv file
    
    path: str of the path of the file
    axis: list of the names of the horizontal and vertical axis
    color: str of the column of the file which separates by color the data (None by default)
    size: str of the column of the file which separates by size the data (None by default)
    realnames: dict of the data in the column 'color' and the associated labels who will appear in the legend (None by default)
    title: str of the title of the graph (None by default)
    log: bool to determine if the yaxis is in log or not (False by default)
    scale: list of 2 lists representing the range of the horizontal and vertical axis (min and max) ([None, None] by default)

    return the figure
    """
    data = pd.read_csv(path)
    fig = px.scatter(data, x=axis[0], y=axis[1], color=color, size = size, size_max=7, title=title, log_y=log, 
    hover_data=data.columns, template='simple_white')
    fig.update_traces(marker=dict(line=dict(width=0.2, color='black')), selector=dict(mode='markers'))
    fig.update_layout(yaxis=dict(range=scale[1]), xaxis=dict(range=scale[0]))
    if realnames:
        for i, dicto in enumerate(fig.data):
            for elem in dicto:
                if elem == 'name':
                    fig.data[i][elem] = realnames[dicto[elem]]
    return fig

def twograhs(path1, path2, yaxis, xaxis='date', scale=[None, None], color=None, size=None, title=None, log=False, df1=None, df2=None):
    """Make a plotly scatter with 2 csv files on the same graph
    
    path1: str of the path of the first file 
    path2: str of the path of the second file
    yaxis: list of the names of the data column of each file
    xaxis: str of the horizontal axis (date by default)
    scale: list of the range of the vertical axis for each file ([None, None] by default)
    color: str of the column of the first file which separates by color the data (None by default)
    size: str of the column of the first file which separates by size the data (None by default)
    title: title ot the graph (None by default)
    log: bool to determine if the yaxis is in log or not (False by default)
    df1: dataframe of the first file if we don't want to take the whole file (None by default)
    df2: dataframe of the second file if we don't want to take the whole file (None by default)

    return the figure
    """
    data1 = pd.read_csv(path1) if df1 is None else df1
    data2 = pd.read_csv(path2) if df2 is None else df2
    color = data1[color] if color is not None else None
    size = data1[size] if size is not None else None
    liste, hovertext = [], ""
    for i, col in enumerate(data1.columns):
        data = data1[col].to_list()
        liste.append(data)
        hovertext += f"<b>{col}:</b> %{{customdata[{i}]}} <br>"
    all_data = np.stack(tuple(liste), axis=-1)
    trace1 = go.Scatter(x=data1[xaxis], y=data1[yaxis[0]], yaxis='y', mode='markers', name=yaxis[0], opacity=0.7, 
        marker_color=color, marker_size=size, customdata=all_data, hovertemplate=hovertext)
    trace2 = go.Scatter(x=data2[xaxis], y=data2[yaxis[1]], yaxis="y2", mode='markers', name=yaxis[1], opacity=0.6)

    fig = make_subplots(specs=[[{"secondary_y": True}]], shared_yaxes='all', shared_xaxes='all')
    fig.add_trace(trace1)
    fig.add_trace(trace2, secondary_y=True)
    fig.update_traces(marker=dict(line=dict(width=0.2, color='black')), selector=dict(mode='markers'))
    fig.update_layout(title_text=title, yaxis1=dict(title=yaxis[0], range=np.log(scale[0]) if log else scale[0], type=("log" if log else None)), yaxis2=dict(title=yaxis[1], range=np.log(scale[1]) if log else scale[1], type=("log" if log else None)), template='simple_white')
    fig.update_xaxes(title_text=xaxis)
    return fig

def graph_exp(path, axis, color=None, size=None, title=None, log=False, scale=[None, None], specifications=None, offset=[0, 0]):
    """Make a plotly scatter and decreasing exponential curve fit with a csv file
    
    path: str of the path of the file
    axis: list of the names of the horizontal and vertical axis
    color: str of the column of the file which separates by color the data (None by default)
    size: str of the column of the file which separates by size the data (None by default)
    title: str of the title of the graph (None by default)
    log: bool to determine if the yaxis is in log or not (False by default)
    scale: list of 2 lists representing the range of the horizontal and vertical axis (min and max) ([None, None] by default)
    specifications: dict where the keys are the name of the columns of the file and the values are a list of the two bounds (min and max) 
                    we want to keep (0 to infinity for all the columns by default)
    offset: list of the horizontal and vertical offset we need to substract the data
    
    return the figure
    """
    df = truncate(path, keepnan=False, specifications=specifications)
    exp = fit_expo(df=df, offset=offset)
    color = df[color] if color is not None else None
    size = df[size] if size is not None else None
    # exp.to_csv(f'{title}_curvefit.csv', index=False)
    liste, hovertext = [], ""
    for i, col in enumerate(df.columns):
        data = df[col].to_list()
        liste.append(data)
        hovertext += f"<b>{col}:</b> %{{customdata[{i}]}} <br>"
    all_data = np.stack(tuple(liste), axis=-1)
    fig = make_subplots()
    fig.add_trace(go.Scatter(x=df[axis[0]]-offset[0], y=df[axis[1]]-offset[1], mode='markers', marker_color=color, 
    marker_size = size, name='Data', customdata=all_data, hovertemplate=hovertext, hoverlabel={'namelength': 0}))
    fig.add_trace(go.Scatter(x=exp['height'], y=exp['irr_pred'], mode='lines', line_color='red', name='Curve-fit'))
    fig.update_traces(marker=dict(line=dict(width=0.2, color='black')), selector=dict(mode='markers'))
    fig.update_layout(title_text=title, yaxis=dict(title='irradiance normalized', range=np.log(scale[1]) if log else scale[1]), 
    xaxis=dict(title=axis[0], range=scale[0]), yaxis_type=("log" if log else None), template='simple_white')
    return fig

def sixgraphs(traces, logs=[1, 0, 0, 0, 0, 0], title=None):
    """Make a graph of 6 subplots of all the relevant features regarding a certain sensor
    
    traces: dictionary of all the traces with keys as the position in the graph
    logs: list of 6 int (0 or 1) to determine if the sublot corresponding has a yaxis in log or not (only for the first plot by default)
    title: str of the title of the graph (None by default)

    return the figure
    """
    fig = make_subplots(rows=3, cols=2, specs=[[{"secondary_y": True}, {}], [{}, {}], [{}, {}]], subplot_titles=tuple(str(key) for key in traces.keys()))
    axis = {'x': 'date', '2': 'height (cm)', '3': 'irradiance', '4':'irradiance_norm', '5':'temperature (°C)', '6':'wind speed (m/s)'}
    titles = {}
    for i, trace in traces.items():
        if i % 2 == 0:
            col=1
        else:
            col=2
        row = int((-col+3+i)/2)
        for tra in trace:
            fig.add_trace(tra, row=row, col=col)
        if logs[i]:
            fig.update_yaxes(type='log', row=row, col=col)
        fig.update_yaxes(title_text=axis[trace[0]['yaxis'][1]], row=row, col=col)
        fig.update_xaxes(title_text=(axis[trace[0]['xaxis'][1]] if trace[0]['xaxis'] != 'x' else axis['x']), row=row, col=col)
        titles[i] = trace[0]['name']
    fig.for_each_annotation(lambda a: a.update(text = titles[int(a.text)]))
    fig.update_layout(template='simple_white', title=title)
    fig.update_traces(marker=dict(line=dict(width=0.2, color='black')), selector=dict(mode='markers'))
    return fig

class Graphs_Snowdata():
    def __init__(self, shift, soot_value):
        self.list_sensors = []
        self.shift = shift
        self.soot = soot_value

    def graph_dailydata(self, days):
        """Make a graph of all the relevant features of (a) certain day(s)
        
        days: list of string of the dates we want to keep (string format: '%Y-%m-%d %H:%M:%S')
            (ex. ['2021-01', '2021-03-11 07:'] represent all the values from January 2021 and those taken the hour following 7 a.m. on March 11 2021)

        return the figure
        """
        traces = self.initialize_classes_dailydata(days)
        fig = make_subplots(rows=2, cols=2, specs=[[{}, {"secondary_y": True}], [{}, {}]], subplot_titles=tuple(str(key) for key in traces.keys()))
        axis = {'x': 'date', '2': 'height (cm)', '3': 'irradiance', '4':'irradiance_norm', '5':'temperature (°C)', '6':'wind speed (m/s)'}
        titles = {}
        for i, trace in traces.items():
            if i % 2 == 0:
                col=1
            else:
                col=2
            row = int((-col+3+i)/2)
            for tra in trace:
                fig.add_trace(tra, row=row, col=col)
            fig.update_yaxes(title_text=axis[trace[0]['yaxis'][1]], row=row, col=col)
            fig.update_xaxes(title_text=(axis[trace[0]['xaxis'][1]] if trace[0]['xaxis'] != 'x' else axis['x']), row=row, col=col)
            titles[i] = trace[0]['name']
        fig.for_each_annotation(lambda a: a.update(text = titles[int(a.text)]))
        fig.update_layout(template='simple_white', title=f'{days} daily measurements data')
        fig.update_traces(marker=dict(line=dict(width=0.2, color='black')), selector=dict(mode='markers'))
        for x0, x1 in get_night_datetime(days):
            fig.add_vrect(x0=x0, x1=x1, row="all", col="all", 
                annotation_text="night", annotation_position="top left", fillcolor='rgb(217, 217, 217)', opacity=1, line_width=0)
        return fig

    def graphs_sensors_height(self, days):
        """Make a graph of the irradiance according to the height with all the buried sensors of (a) certain day(s)
        
        days: list of string of the dates we want to keep (string format: '%Y-%m-%d %H:%M:%S')
            (ex. ['2021-01', '2021-03-11 07:'] represent all the values from January 2021 and those taken the hour following 7 a.m. on March 11 2021)

        return the figure
        """
        traces = []
        for h in ['325', '485', '650']:
            for L in ['F', 'S']:
                list = self.initialize_classes_sensor(f'400{L+h}', days)
                if list is False:
                    continue
                else:
                    traces.append(list)
        if len(traces) % 2 != 0:
            raise ValueError('The number of traces is not even')
        specs = [[{"secondary_y": True}, {"secondary_y": True}] for _ in range(len(traces)//2)]
        fig = make_subplots(rows=len(traces)//2, cols=2, specs=specs, subplot_titles=tuple(str(i) for i in range(len(traces))))
        axis = {'x': 'date', '2': 'height (cm)', '3': 'irradiance', '4':'irradiance_norm'}
        titles = {}

        test = SnowData(from_database=True, relevant=False)
        data = test.simul_irradiance()
        for column in data.columns:
            fig.add_trace(go.Scatter(x=data.index*100, y=data[column], name=column), row=1, col=1)

        for i, trace in enumerate(traces):
            if i % 2 == 0:
                col=1
            else:
                col=2
            row = int((-col+3+i)/2)
            for tra in trace:
                fig.add_trace(tra, row=row, col=col)
            fig.update_yaxes(title_text=axis[trace[0]['yaxis'][1]], type='log', row=row, col=col)
            fig.update_xaxes(title_text=(axis[trace[0]['xaxis'][1]] if trace[0]['xaxis'] != 'x' else axis['x']), row=row, col=col)
            titles[i] = trace[0]['name']
        fig.for_each_annotation(lambda a: a.update(text = titles[int(a.text)]))
        fig.update_layout(template='simple_white', title=f'Irradiance normalized according to the snow height over the sensors on {days}')
        fig.update_traces(marker=dict(line=dict(width=0.2, color='black')), selector=dict(mode='markers'))
        return fig

    def graphs_sensors_date(self, days):
        """Make a graph of the irradiance according to the date with all the buried sensors of (a) certain day(s)

        days: list of string of the dates we want to keep (string format: '%Y-%m-%d %H:%M:%S')
            (ex. ['2021-01', '2021-03-11 07:'] represent all the values from January 2021 and those taken the hour following 7 a.m. on March 11 2021)
        
        return the figure
        """
        traces = []
        for h in ['325', '485', '650']:
            for L in ['F', 'S']:
                list = self.initialize_classes_sensor(f'400{L+h}', days, x='date')
                if list is False:
                    continue
                else:
                    traces.append(list)
        if len(traces) % 2 != 0:
            raise ValueError('The number of traces is not even')
        specs = [[{"secondary_y": True}, {"secondary_y": True}] for _ in range(len(traces)//2)]
        fig = make_subplots(rows=len(traces)//2, cols=2, specs=specs, subplot_titles=tuple(str(i) for i in range(len(traces))))
        axis = {'x': 'date', '2': 'height (cm)', '3': 'irradiance', '4':'irradiance_norm'}
        titles = {}
        for i, trace in enumerate(traces):
            if i % 2 == 0:
                col=1
            else:
                col=2
            row = int((-col+3+i)/2)
            for tra in trace:
                fig.add_trace(tra, row=row, col=col)
            fig.update_xaxes(title_text=(axis[trace[0]['xaxis'][1]] if trace[0]['xaxis'] != 'x' else axis['x']), row=row, col=col)
            titles[i] = trace[0]['name']
        fig.for_each_annotation(lambda a: a.update(text = titles[int(a.text)]))
        fig.update_layout(template='simple_white', title=f'Irradiance normalized according to date on {days}')
        fig.update_traces(marker=dict(line=dict(width=0.2, color='black')), selector=dict(mode='markers'))
        for x0, x1 in get_night_datetime(days):
            fig.add_vrect(x0=x0, x1=x1, row="all", col="all", 
                annotation_text="night", annotation_position="top left", fillcolor='rgb(217, 217, 217)', opacity=1, line_width=0)
        return fig

    def initialize_classes_dailydata(self, days):
        """Initialize all the scatter traces needed to make a daily data graph
        
        days: list of string of the dates we want to keep (string format: '%Y-%m-%d %H:%M:%S')
            (ex. ['2021-01', '2021-03-11 07:'] represent all the values from January 2021 and those taken the hour following 7 a.m. on March 11 2021)

        return a dictonary of the traces where the key is the position of the subplot and 
                the values are the list of the traces at this position
        """
        wind = SnowData('Wind_speed.csv', relevant=False)
        wind.find_dates(days)
        trace3 = wind.make_fig('date', 'wind_speed', 'Wind speed', color='wind_angle', axis=['1', '6'], 
                                colorscale='hsv', cmin=0, cmax=360)
        height =  SnowData('all_heightsV.csv', relevant=False)
        height.find_dates(days)
        height.datetonum()
        data = height.df
        temp = SnowData('Temperature.csv', relevant=False)
        temp.find_dates(days)
        temp.datetonum(min=data['date'].min())
        trace4 = temp.make_fig('date', 'temperature', 'Temperature', axis=['1', '5'], color='humidity', colorscale='burg')
        height.poly_fit(temp, y='height', split_date=True)
        trace2 = height.make_fig('date', 'height', 'Snow height', axis=['1', '2'])
        trace21 = height.make_fig('date', 'height', 'Snow height fitted', axis=['1', '2'], mode='lines', color='green')
        cnr4 = SnowData('ISWR-strip.csv', relevant=False)
        cnr4.find_dates(days)
        trace1 = cnr4.make_fig('date', 'irr', 'CNR4 irradiance', axis=['1', '3'])
        return {0:[trace1], 1:[trace2, trace21], 2:[trace3], 3:[trace4]}

    def initialize_classes_sensor(self, sensor, days, x='height_moved'):
        """Initialize all the scatter traces needed to make a sensor graph 
        
        sensor: str of the name of the sensor (ex. '400F325')
        days: list of string of the dates we want to keep (string format: '%Y-%m-%d %H:%M:%S')
            (ex. ['2021-01', '2021-03-11 07:'] represent all the values from January 2021 and those taken the hour following 7 a.m. on March 11 2021)
        x: str of the name of the column we want to use as x axis (default: 'height_moved')

        return a list of the traces
        """
        height =  SnowData('all_heightsV.csv')
        height.find_dates(days)
        height.modify_data('height', -int(sensor[4:])/10)
        height.datetonum()
        data = height.df
        if data['height_moved'].le(3).any():
            return False
        if sensor not in self.list_sensors:
            self.normalize_sensor(sensor, days, denoise=False)
            self.list_sensors.append(sensor)
        classnorm = SnowData(f'{sensor}_g_normFrefs.csv', relevant=False if x == 'date' else True)
        classnorm.find_dates(days)
        classnorm.add_luminosity()
        classnorm.classify_dates()
        classnorm.datetonum(min=data['date'].min())
        if x == 'height_moved':
            height.poly_fit(classnorm, split_date=True)
            classnorm.add_column(height)
            classnorm.remove_highangles()
            trace0 = classnorm.make_fig('height_moved', 'irr_ro i0-norm_ro', f'{sensor}_normFrefs', axis=['2', '4'], color='zenith angle')
            param, r = classnorm.fit_exp(y='irr_ro i0-norm_ro')
            trace01 = classnorm.make_fig('height_moved', 'irr_pred', f'm={param[0]:.3g}\n R^2={r:.4g}', axis=['2', '4'], mode='lines', color='red')
            return [trace0, trace01]
        elif x == 'date':
            classnorm.remove_highangles()
            trace0 = classnorm.make_fig('date', 'irr', f'{sensor}', axis=['1', '3'])
            trace01 = classnorm.make_fig('date', 'irr_ro i0-norm_ro', f'{sensor}_normFrefs', axis=['1', '3'], color='hour-min')
            return [trace0, trace01]

    def normalize_sensor(self, sensor, days, denoise=False):
        """Normalize the data of a sensor with the data of the reference sensor

        sensor: str of the name of the sensor (ex. '400F325')
        days: list of string of the dates we want to keep (string format: '%Y-%m-%d %H:%M:%S')
            (ex. ['2021-01', '2021-03-11 07:'] represent all the values from January 2021 and those taken the hour following 7 a.m. on March 11 2021)
        denoise: bool to know if we want to denoise the data (default: False)
        shift: list of 2 int of the shift we want to apply to the reference sensor (default: [0, 0])
            (ex. [10, 5] means we want to shift the reference sensor 10 units to the north and 5 units to the east (negative values for south and west))
        """

        cap = SnowData(f'{sensor}_g.csv', name=sensor)
        ref = SnowData('400Frefs_g.csv', name='400Frefs', relevant=False)
        cap.correct_accordingtoalbedo(soot_value=self.soot)
        cap.round_data('irr')
        ref.round_data('irr')
        ref.add_luminosity()
        ref.rectify_data(x='irr_ro', north=self.shift[0], east=self.shift[1])
        cap.norm_i0(ref, 'irr_ro')
        cap.round_data('irr_ro i0-norm', object='df_norm')
        if denoise:
            cap.denoise_med('irr_ro i0-norm_ro')
        cap.save(f'{sensor}_g', object='df_norm')

def final_graph(days, name=None, shift=[0, 0], soot=1000e-9):
    """Make the final graph with all the traces
    
    days: list of string of the dates we want to keep (string format: '%Y-%m-%d %H:%M:%S')
        (ex. ['2021-01', '2021-03-11 07:'] represent all the values from January 2021 and those taken the hour following 7 a.m. on March 11 2021)
    name: str of the name of the file we want to save the graph (dailydata-"days".html by default
    shift: list of 2 int of the shift we want to apply to the reference sensor (default: [0, 0])
        (ex. [10, 5] means we want to shift the reference sensor 10 units to the north and 5 units to the east (negative values for south and west))
    soot: float of the soot concentration (default: 1000e-9)
    
    save all the traces in a graph and open it"""
    param = Graphs_Snowdata(shift=shift, soot_value=soot)
    #fig1 = param.graph_dailydata(days)
    fig2 = param.graphs_sensors_height(days)
    #fig3 = param.graphs_sensors_date(days)
    l = [dt.datetime.strptime(day, '%Y-%m-%d') for day in days]
    l = [(day-min(l)).days for day in l]
    if name is None:
        if len(days) == 1:
            d = days[0].replace('2021-', '')
            name = f'dailydata-{d}.html'
        elif sorted(l) == list(range(min(l), max(l)+1)):
            d1 = days[0].replace('2021-', '')
            d2 = days[-1].replace('2021-', '')
            name = f'dailydata-{d1}to{d2}.html'
        else:
            d1 = days[0].replace('2021-', '')
            d2 = days[-1].replace('2021-', '')
            name = f'dailydata-{d1}and{d2}.html'
    
    if os.path.exists(name):
        os.remove(name)
    with open(name, 'a') as f:
        #f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn'))
        #f.write(fig3.to_html(full_html=False, include_plotlyjs='cdn'))
    
    new = 2 # open in a new tab, if possible
    url = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage I\\Data\\' + name
    webbrowser.open(url,new=new)

#Write info here
names = {'A': 'Automatic', 'B': 'Benjamin', 'C': 'CRN4', 'M': 'Manual', 'F':'Forent', 'V': 'Valérie'}
axis = ['irr', 'irr_pred']
scale=[[0.01, 1.6], [0.01, 1.6]]
arr = np.array([[0, 5, 10, 15, 20, 25, 30],
                [1, 6, 11, 16, 21, 26, 31],
                [2, 7, 12, 17, 22, 27, 32], 
                [3, 8, 13, 18, 23, 28, 33], 
                [4, 9, 14, 19, 24, 29, 34]])
cols = [('325', 'B'), ('485', 'D'), ('650', 'F'), ('1000', 'J')] # , ('1200', 'L'), ('1375', 'N'), ('1500', 'P')

# show and save figure
days = ['2021-03-20', '2021-03-21', '2021-03-22', '2021-03-23']
# print(final_graph(days))
print(final_graph(days, 'test.html', soot=1000e-9))

