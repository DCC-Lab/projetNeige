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
    fig = px.scatter(data, x='date', y='irradiance_denoised', color=color, title=f"Height of the snow {constant+' ' if constant else ''}over time according to the {color} (2020-2021)") #, log_y=True
    if realNames:
        for i, dict in enumerate(fig.data):
            for elem in dict:
                if elem == 'name':
                    fig.data[i][elem] = realNames[dict[elem]]
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

    trace1 = go.Scatter(x=data1['date'], y=data1[yaxis[0]], mode='markers', name=yaxis[0])
    trace2 = go.Scatter(x=data2['date'], y=data2[yaxis[1]], yaxis="y2", mode='markers', name=yaxis[1])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace1)
    fig.add_trace(trace2,secondary_y=True)
    fig.update_layout(title_text=title, yaxis1=dict(range=scale[0]), yaxis2=dict(range=scale[1]))
    fig.update_xaxes(title_text="date")
    fig.update_yaxes(title_text=yaxis[0], secondary_y=False)
    fig.update_yaxes(title_text=yaxis[1], secondary_y=True)
    return fig


#Write info here
path1 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\400F325_norm1200-4.csv'
path2 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\400F325_norm1200-4.csv'
# names = {'A': 'Automatic', 'C': 'CRN4', 'M': 'Manual', 'F':'Forent'}

yaxis = ['irradiance self-norm', 'irradiance self-norm i0-norm_denoisedR std-norm']
df = pd.read_csv(path1)
ira = df[yaxis[1]]
ref = df[yaxis[0]]
indexref = df.loc[ref == max(ref)].index[0]
max_ira = ira.loc[indexref]
scale = [[0, max(ref)], [0, max_ira*1.5]]

#show and save figure
fig = twograhs(path1, path2, '4-B', yaxis, scale)
fig.show()
fig.write_html('all_400F325_norm1200-4B.html')

# fig = graphheight(path2)
# fig.show()