import pandas as pd
import numpy as np
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sklearn.preprocessing import scale
from manipfiles import truncate, curve_fitting

def onegraph(path, axis, color=None, size=None, realnames=None, title=None, log=False, scale=[None, None]):
    """make a plotly scatter with a csv file
    
    path: str of the path of the file
    axis: list of the names of the horizontal and vertical axis
    color: str of the colum of the file which separates by color the data (None by default)
    size: str of the colum of the file which separates by size the data (None by default)
    realnames: dict of the data in the colum 'color' and the associated labels who will appear in the legend (None by default)
    title: str of the title of the graph (None by default)
    log: bool to determine if the yaxis is in log or not
    scale: list of 2 lists representing the range of the horizontal and vertical axis (min and max)

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

def twograhs(path1, path2, title, yaxis, scale):
    """make a plotly scatter with 2 csv files on the same graph
    
    path1: str of the path of the first file 
    path2: str of the path of the second file
    title: title ot the graph
    yaxis: list of the names of the data column of each file
    scale: range of the vertical axis for each file

    return the figure
    """
    data1 = pd.read_csv(path1)
    data2 = pd.read_csv(path2)
    trace1 = go.Scatter(x=data1['date'], y=data1[yaxis[0]], yaxis='y', mode='markers', name=yaxis[0], opacity=0.5)
    trace2 = go.Scatter(x=data2['date'], y=data2[yaxis[1]], yaxis="y2", mode='markers', name=yaxis[1], opacity=0.5)

    fig = make_subplots(specs=[[{"secondary_y": True}]], shared_yaxes='all', shared_xaxes='all')
    fig.add_trace(trace1)
    fig.add_trace(trace2, secondary_y=True)
    fig.update_layout(title_text=title, yaxis1=dict(title=yaxis[0], range=scale[0]), yaxis2=dict(title=yaxis[1], range=scale[1]))
    fig.update_xaxes(title_text="date")
    return fig

def graph_exp(path, axis, color=None, size=None, title=None, log=False, scale=[None, None], specifications=None, offset=[0, 0]):
    """make a plotly scatter with a csv file
    
    path: str of the path of the file
    axis: list of the names of the horizontal and vertical axis
    color: str of the colum of the file which separates by color the data (None by default)
    size: str of the colum of the file which separates by size the data (None by default)
    title: str of the title of the graph (None by default)
    log: bool to determine if the yaxis is in log or not
    scale: list of 2 lists representing the range of the horizontal and vertical axis (min and max)
    specifications: dict where the keys are the name of the columns of the file and the values are a list of the two bounds (min and max) 
                    we want to keep (0 to infinity for all the columns by default)
    offset: list of the horizontal and vertical offset we need to substract the data
    
    return the figure
    """
    df = truncate(path, keepnan=False, specifications=specifications)
    exp = curve_fitting(df=df, offset=offset)
    liste, hovertext = [], ""
    for i, col in enumerate(df.columns):
        data = df[col].to_list()
        liste.append(data)
        hovertext += f"<b>{col}:</b> %{{customdata[{i}]: .2f}} <br>"
    all_data = np.stack(tuple(liste), axis=-1)
    fig = make_subplots()
    fig.add_trace(go.Scatter(x=df[axis[0]]-offset[0], y=df[axis[1]]-offset[1], mode='markers', marker_color=df[color], 
    marker_size = df[size], name='Data', customdata=all_data, hovertemplate=hovertext, hoverlabel={'namelength': 0}))
    fig.add_trace(go.Scatter(x=exp['height'], y=exp['irr_pred'], mode='lines', line_color='red', name='Curve-fit'))
    fig.update_traces(marker=dict(line=dict(width=0.2, color='black')), selector=dict(mode='markers'))
    fig.update_layout(title_text=title, yaxis=dict(title='irradiance normalized', range=np.log(scale[1]) if log else scale[1]), 
    xaxis=dict(title=axis[0], range=scale[0]), yaxis_type=("log" if log else None), template='simple_white')
    return fig


#Write info here
path1 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\400F325_norm1000+heightsV.csv'
path2 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\400F650-sunny.csv'
names = {'A': 'Automatic', 'B': 'Benjamin', 'C': 'CRN4', 'M': 'Manual', 'F':'Forent', 'V': 'Valérie'}

axis = ['date', 'irr']
scale=[[None, None], [-0.1, 1.5]]
# speci={'sun level': [3.5, 5], 'id-hour': [4.5, np.infty], 'height': [32.5, np.infty]}

# show and save figure
# fig = twograhs(path2, path1, 'corr', yaxis, scale)
# fig.show()
# fig.write_html(f'all_400F650-corr.html')
# cols = [('325', 'B'), ('485', 'D'), ('650', 'F'), ('1000', 'J'), ('1200', 'L'), ('1375', 'N')] # 
# for c, i in cols[:3]:
#     for co, il in cols[3:]:

fig = onegraph(path2, axis)
fig.show()
# fig = graph_exp(path1, axis, title=f'400F325_norm1000 irr according to the height', color='id-day', size='id-hour', scale=scale, specifications=None, log=True, offset=[32.5, 0])
# fig.show()
# fig.write_html(f'all_400F{c}_norm{co}+heightsV.html')