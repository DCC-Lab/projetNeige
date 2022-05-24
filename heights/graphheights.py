import pandas as pd
import plotly.express as px


def graphheight(path, color, realNames=None, constant=None):
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

#Write info here
path = 'C:\\Users\\Proprio\\Documents\\UNI\\Stage\\Data\\all_heightsM.csv'
color = 'pole'
realNames = {'A':'Automatic', 'M' : 'Manual', 'C': 'CRN4', 'F': 'Florent'}
constant = 'manually'
fig = graphheight(path, color, constant=constant)
#show and save figure
fig.show()
fig.write_image('all_heightsM.jpg')