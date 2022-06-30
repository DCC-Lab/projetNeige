import pandas as pd
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
    print(data)
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
    trace1 = go.Scatter(x=data1['date'], y=data1[yaxis[0]], mode='markers', name=yaxis[0], opacity=0.5)
    trace2 = go.Scatter(x=data2['date'], y=data2[yaxis[1]], yaxis="y2", mode='markers', name=yaxis[1], opacity=0.5)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace1)
    fig.add_trace(trace2,secondary_y=True)
    fig.update_layout(title_text=title, yaxis1=dict(range=scale[0]), yaxis2=dict(range=scale[1]))
    fig.update_xaxes(title_text="date")
    fig.update_yaxes(title_text=yaxis[0], secondary_y=False)
    fig.update_yaxes(title_text=yaxis[1], secondary_y=True)
    return fig


#Write info here
path1 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\'
path2 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\all_heightsF.csv'
names = {'A': 'Automatic', 'C': 'CRN4', 'M': 'Manual', 'F':'Forent'}

yaxis = 'height' #, 'irr self-norm i0-norm_denoisedL std-norm']

#show and save figure
# fig = twograhs(f'{path1}400F{c}_norm{co}.csv', f'{path1}400F{c}_norm{co}.csv', f'all_400F{c}_norm{co}L', yaxis, scale)
# fig.show()
# fig.write_html(f'all_400F{c}_norm{co}L.html')

fig = graphheight(path2, yaxis, color='method', realnames=names, title='test')
fig.show()
fig.write_html(f'all_heightsF.html')