import dash
import numpy
import folium
import geojson
import geopandas
import pandas as pd
import plotly.express as px
# import plotly_express as px
from dash import Input
from dash import Output
from dash import dcc
from dash import html

# importing datasets

df1 = pd.read_csv('athlete_events.csv')


# creating dataframe of golden medals by country (only the first 20)

gold = pd.DataFrame(columns=['Country', 'Number of golden medals'])

for i in range(len(df1)):
    noc = df1.loc[i, 'NOC']
    if df1.loc[i, 'Medal'] == 'Gold':
        if noc in gold.values:
            gold.loc[gold[gold['Country'] == noc].index[0], 'Number of golden medals'] += 1
        else:
            gold = gold.append({'Country': noc, 'Number of golden medals': 1}, ignore_index=True)

gold = gold[gold['Number of golden medals'] >= 179]
gold = gold.sort_values(by=['Number of golden medals'])
gold.reset_index(inplace=True, drop=True)

# creating dataframe of all medals by country (only the first 20)

medals = pd.DataFrame(columns=['Country', 'Gold', 'Silver', 'Bronze'])

for i in range(len(df1)):
    noc = df1.loc[i, 'NOC']
    color = df1.loc[i, 'Medal']
    if not pd.isna(df1.loc[i, 'Medal']):
        if noc in medals['Country'].values:
            medals.loc[medals[medals['Country'] == noc].index[0], color] += 1
        else:
            medals = medals.append({'Country': noc, 'Gold': 0, 'Silver': 0, 'Bronze': 0}, ignore_index=True)
            medals.loc[medals[medals['Country'] == noc].index[0], color] += 1

medals['total'] = medals['Gold'] + medals['Silver'] + medals['Bronze']
medals = medals[medals['total'] >= 638]
medals = medals.sort_values(by=['total'])
medals.reset_index(inplace=True, drop=True)
medals.drop(labels='total', axis=1, inplace=True)
medals = medals.melt('Country', var_name='medal', value_name='count',)


# Convert NOC into countries names


country_name_table = {'USA': 'United States', 'URS': 'Soviet Union', 'GER': 'Germany', 'GBR': 'Great Britain',
                      'ITA': 'Italy', 'FRA': 'France', 'SWE': 'Sweden', 'CAN': 'Canada', 'HUN': 'Hungary',
                      'GDR': 'East Germany', 'RUS': 'Russia', 'NOR': 'Norway', 'CHN': 'China', 'AUS': 'Australia',
                      'NED': 'Netherlands', 'JPN': 'Japan', 'KOR': 'South Korea', 'FIN': 'Finland', 'DEN': 'Denmark',
                      'POL': 'Poland', 'SUI': 'Switzerland', 'ESP': 'Spain', 'AUT': 'Austria', 'ROU': 'Romania'}

gold['Country'].replace(country_name_table, inplace=True)
medals['Country'].replace(country_name_table, inplace=True)


# Couleurs qu'on va ptet utilsier plus tard

colors = {
    'background': '#2D2D2D',
    'text': '#E1E2E5',
}


# Building Figures

gold_medal_fig = px.bar(gold, x='Country', y='Number of golden medals')

medal_fig = px.bar(medals, x='Country', y='count', color='medal',
                   color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#c96'})


# Start of the application

app = dash.Dash(__name__)


app.layout = html.Div(children=[
    html.Div([
        html.H1(children='Jeux olympiques mageule', style={
            'textAlign': 'center'
        }),
    ]),
    html.Div([
        dcc.RadioItems(
                id='graph-type',
                options=[{'label': i, 'value': i} for i in ['all medals', 'only golden medals']],
                value='all medals',
                labelStyle={'display': 'inline-block'},
                style={
                    'fontSize': 20, 'textAlign': 'left'
                },
            ),
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
