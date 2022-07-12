import pandas as pd
import numpy as np
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sklearn.preprocessing import scale
from manipfiles import truncate, curve_fitting

def graphheight(path, axis, color=None, size=None, realnames=None, title=None, log=False, scale=None):
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
    data = truncate(path, specifications={'sun level': [3.5, 5], 'id-hour': [4.5, np.infty], 'height': [30, np.infty]})
    fig = px.scatter(data, x=axis[0], y=axis[1], color=color, size = size, size_max=7, title=title, log_y=log, hover_data=data.columns)
    fig.update_traces(marker=dict(line=dict(width=0)), selector=dict(mode='markers'))
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


#Write info here
path1 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\400F325_norm1000+heightsV.csv'
path2 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\'
names = {'A': 'Automatic', 'B': 'Benjamin', 'C': 'CRN4', 'M': 'Manual', 'F':'Forent', 'V': 'Valérie'}

axis = ['height', 'irr']
scale=[[None, None], [-0.1, 1.5]]

# show and save figure
# fig = twograhs(path2, path1, 'corr', yaxis, scale)
# fig.show()
# fig.write_html(f'all_400F650-corr.html')
# cols = [('325', 'B'), ('485', 'D'), ('650', 'F'), ('1000', 'J'), ('1200', 'L'), ('1375', 'N')] # 
# for c, i in cols[:3]:
#     for co, il in cols[3:]:

fig = graphheight(path1, axis, title=f'400F325_norm1000 irr according to the height', color='id-day', size='id-hour', scale=scale)
fig.show()
# fig.write_html(f'all_400F{c}_norm{co}+heightsV.html')
