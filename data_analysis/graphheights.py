import pandas as pd
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sklearn.preprocessing import scale

def graphheight(path, yaxis, color=None, realnames=None, title=None):
    """make a plotly scatter with a csv file
    
    path: str of the path of the file
    yaxis: str of the name of the vertial axis
    color: str of the colum of the file which separates the data (None by default)
    realnames: dict of the data in the colum 'color' and the associated labels who will appear in the legend (None by default)
    title: str of the title of the graph (None by default)

    return the figure
    """
    data = pd.read_csv(path)
    fig = px.scatter(data, x='date', y=yaxis, color=color, title=title) #, log_y=True
    if realnames:
        for i, dict in enumerate(fig.data):
            for elem in dict:
                if elem == 'name':
                    fig.data[i][elem] = realnames[dict[elem]]
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
    trace2 = go.Scatter(x=data2['date'], y=data2[yaxis[1]], yaxis="y2", mode='lines', name=yaxis[1], opacity=0.5)

    fig = make_subplots(specs=[[{"secondary_y": True}]], shared_yaxes='all', shared_xaxes='all')
    fig.add_trace(trace1)
    fig.add_trace(trace2, secondary_y=True)
    fig.update_layout(title_text=title, yaxis1=dict(title=yaxis[0], range=scale[0]), yaxis2=dict(title=yaxis[1], range=scale[1]))
    fig.update_xaxes(title_text="date")
    return fig


#Write info here
path1 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\heightsV.csv'
path2 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\all_heightsAFMV.csv'
names = {'A': 'Automatic', 'B': 'Benjamin', 'C': 'CRN4', 'M': 'Manual', 'F':'Forent', 'V': 'Valérie'}

yaxis = ['height', 'height_denoisedL moved']
scale=[[0, 90], [0, 90]]

#show and save figure
fig = twograhs(path2, path1, 'heights', yaxis, scale)
fig.show()
fig.write_html(f'all_heightsAFMV-withline.html')

# fig = graphheight(path1, yaxis, title='Heights V median', realnames=names, color='method')
# fig.show()
# fig.write_html(f'all_heightsAFMV.html')
