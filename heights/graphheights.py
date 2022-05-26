import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def graphheight(path, color=None, realNames=None, constant=None):
    """make a plotly scatter with a csv file
    
    path: str of the path of the file
    color: str of the colum of the file which separates the data
    realNames: dict of the data in the colum 'color' and the associated labels who will appear in the legend
    constant: str of a caracteristic who is constant in this data (None by default)

    return the figure
    """
    data = pd.read_csv(path)
    fig = px.scatter(data, x='date', y='height', color=color, labels={"height": "height (cm)"}, title=f"Height of the snow {constant+' ' if constant else ''}over time according to the {color} (2020-2021)")
    if realNames:
        for i, dict in enumerate(fig.data):
            for elem in dict:
                if elem == 'name':
                    fig.data[i][elem] = realNames[dict[elem]]
    return fig

def twograhs(path1, path2, title, norm):
    """make a plotly scatter with 2 csv files on the same graph
    
    path1: str of the path of the file of the irradiance
    path2: str of the path of the file of the height

    return the figure
    """
    data1 = pd.read_csv(path1)
    data2 = pd.read_csv(path2)

    trace1 = go.Scatter(x=data1['date'], y=data1[f'irradiance {norm}-normalized'], mode='markers', name='irradiance')
    trace2 = go.Scatter(x=data2['date'], y=data2['height'], yaxis="y2", mode='markers', name='height')

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace1)
    fig.add_trace(trace2,secondary_y=True)
    fig.update_layout(title_text=title)
    fig.update_xaxes(title_text="date")
    fig.update_yaxes(title_text=f"irradiance {norm}-normalized", secondary_y=False)
    fig.update_yaxes(title_text="height (cm)", secondary_y=True)
    return fig


#Write info here
path1 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\400F650_normalizedwith1200.csv'
path2 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\all_heightsACFM.csv'
title = "Irradiance (400F650) and height (ACFM) of snow over time (2020-2021)"
norm = 'i0'
#show and save figure
fig = twograhs(path1, path2, title, norm)
fig.show()
# fig.write_image('all_400F650+heightsACFM_norm1200.png')