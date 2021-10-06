import dash
import numpy as np
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
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
from geopy.geocoders import Nominatim

# importing datasets

df1 = pd.read_csv('athlete_events.csv')
df1 = df1.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

# creating dataframe of golden medals by country (only the first 20)

gold = df1[['NOC', 'Medal']]
gold = gold[gold['Medal'] == 'Gold']
gold = gold.NOC.value_counts()
gold = gold[:20]
gold = pd.DataFrame({'Country': gold.index, 'Number of golden medals': gold.values})

# creating dataframe of all medals by country (only the first 20)

medals = df1[['NOC', 'Medal']].dropna()
medals = medals.value_counts()
medals = pd.DataFrame({'Country': medals.index.get_level_values(0),
                       'medal': medals.index.get_level_values(1), 'count': medals.values})
medals = medals[medals['Country'].isin(gold['Country'])]

# creating data for the map

world_medals = df1[['NOC', 'Medal']].dropna().value_counts()
world_medals = pd.DataFrame({'Country': world_medals.index.get_level_values(0),
                             'medal': world_medals.index.get_level_values(1), 'count': world_medals.values})
print(world_medals)
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

world_fig = px.choropleth(world_medals, locations='Country',
                          color="count",  # lifeExp is a column of gapminder
                          hover_name="Country",  # column to add to hover information
                          color_continuous_scale=px.colors.sequential.Plasma)


# Start of the application

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div([
        html.H1(children='Jeux olympiques mageule', style={
            'textAlign': 'center', 'padding': '15px'
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
    ]),
    html.Div([
        dcc.Graph(
            figure=world_fig,
            id='world_fig'
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
