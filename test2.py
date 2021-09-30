import dash
import numpy
import folium
import geojson
import geopandas
import pandas as pd
import plotly_express as px
from dash import Input
from dash import Output
from dash import dcc
from dash import html

# importing datasets

df1 = pd.read_csv('athlete_events.csv')

# creating a dict of golden medals by country for bar plot (only the first 20)

gold = dict()

for i in range(len(df1)):
    if df1.loc[i, 'Medal'] == 'Gold':
        if df1.loc[i, 'NOC'] in gold:
            gold[df1.loc[i, 'NOC']] += 1
        else:
            gold[df1.loc[i, 'NOC']] = 1

gold = {k: v for k, v in sorted(gold.items(), key=lambda item: item[1]) if v >= 175}
gold = {'Country': list(gold.keys()), 'Number of gold medals': list(gold.values())}

# creating a dict of medals by country for bar plot (only the first 20)

medals = dict()

for i in range(len(df1)):
    if df1.loc[i, 'Medal'] != 'NaN':
        if df1.loc[i, 'NOC'] in medals:
            medals[df1.loc[i, 'NOC']] += 1
        else:
            medals[df1.loc[i, 'NOC']] = 1

medals = {k: v for k, v in sorted(medals.items(), key=lambda item: item[1]) if v >= 5000}
medals = {'Country': list(medals.keys()), 'Number of medals': list(medals.values())}


# Couleurs qu'on va ptet utilsier plus tard

colors = {
    'background': '#2D2D2D',
    'text': '#E1E2E5',
}

app = dash.Dash(__name__)

gold_medal_fig = px.bar(gold, x='Country', y='Number of gold medals', color='Country')

medal_fig = px.bar(medals, x='Country', y='Number of medals', color='Country')

app.layout = html.Div(children=[
    html.H1(children='Jeux olympiques mageule', style={
        'textAlign': 'center', 'font_family': 'sans-serif'
    }),
    dcc.RadioItems(
        id='graph-type',
        options=[{'label': i, 'value': i} for i in ['only golden medals', 'all medals']],
        value='only golden medals',
        labelStyle={'display': 'inline-block'},
        style={
            'fontSize': 20, 'textAlign': 'left'
        },
    ),
    html.Div([
        dcc.Graph(
            id='medal_fig'
        )
    ])
])


@app.callback(
    Output('medal_fig', 'figure'),
    [Input('graph-type', 'value')])
def build_graph(graph_type):
    if graph_type == 'only golden medals':
        return gold_medal_fig
    else:
        return medal_fig


if __name__ == '__main__':
    app.run_server(debug=True)
