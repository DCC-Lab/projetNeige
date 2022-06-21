import pandas as pd
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def graphheight(path, color=None, realNames=None, title=None, constant=None):
    """make a plotly scatter with a csv file
    
    path: str of the path of the file
    color: str of the colum of the file which separates the data
    realNames: dict of the data in the colum 'color' and the associated labels who will appear in the legend
    title: str of the title of the graph
    constant: str of a caracteristic who is constant in this data (None by default)

    return the figure
    """
    data = pd.read_csv(path)
    fig = px.scatter(data, x='date', y='irr', color=color, title=title) #, log_y=True // f"Height of the snow {constant+' ' if constant else ''}over time according to the {color} (2020-2021)"
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
    cols = plotly.colors.qualitative.Pastel1
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
path2 = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\'
# names = {'A': 'Automatic', 'C': 'CRN4', 'M': 'Manual', 'F':'Forent'}

yaxis = ['irr', 'irr']
# df = pd.read_csv(path1)
# ira = df[yaxis[1]]
# ref = df[yaxis[0]]
# indexref = df.loc[ref == max(ref)].index[0]
# max_ira = ira.loc[indexref]
scale = [[-0.1, 2], [-0.1, 2]]
cols = [('325', 'B'), ('485', 'D'), ('650', 'F'), ('1000', 'J'), ('1200', 'L'), ('1375', 'N')] # 
for c, i in cols:
#show and save figure
    fig = twograhs(f'{path2}400F{c}-raw.csv', f'{path2}400F{c}.csv', f'400F{c}', yaxis, scale)
    fig.show()
    fig.write_html(f'all_400F{c}-corr.html')

# fig = graphheight(path2, title='400F1375')
# fig.show()
# fig.write_html('all_400F1000.html')