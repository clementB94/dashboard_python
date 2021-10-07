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

# creating dataframe of all medals by country but in wide format

world_medals = df1[['NOC', 'Medal']].dropna().value_counts()
world_medals = pd.DataFrame({'Country': world_medals.index.get_level_values(0),
                             'medal': world_medals.index.get_level_values(1), 'count': world_medals.values})
world_medals = world_medals.pivot(index='Country', columns='medal', values='count')
world_medals.fillna(0, inplace=True)
world_medals.reset_index(inplace=True)
world_medals['Total number of medals'] = world_medals['Gold'] + world_medals['Silver'] + world_medals['Bronze']

# creating dataframe of medals by country but only on specific events type

running_medals = df1[['NOC', 'Medal']].loc[df1['Sport'] == 'Athletics'].dropna().value_counts()
running_medals = pd.DataFrame({'Country': running_medals.index.get_level_values(0),
                               'medal': running_medals.index.get_level_values(1), 'count': running_medals.values})
running_medals = running_medals.pivot(index='Country', columns='medal', values='count')
running_medals.fillna(0, inplace=True)
running_medals.reset_index(inplace=True)
running_medals['Total number of medals'] = running_medals['Gold'] + running_medals['Silver'] + running_medals['Bronze']

gym_medals = df1[['NOC', 'Medal']].loc[df1['Sport'] == 'Gymnastics'].dropna().value_counts()
gym_medals = pd.DataFrame({'Country': gym_medals.index.get_level_values(0),
                           'medal': gym_medals.index.get_level_values(1), 'count': gym_medals.values})
gym_medals = gym_medals.pivot(index='Country', columns='medal', values='count')
gym_medals.fillna(0, inplace=True)
gym_medals.reset_index(inplace=True)
gym_medals['Total number of medals'] = gym_medals['Gold'] + gym_medals['Silver'] + gym_medals['Bronze']

swim_medals = df1[['NOC', 'Medal']].loc[df1['Sport'] == 'Swimming'].dropna().value_counts()
swim_medals = pd.DataFrame({'Country': swim_medals.index.get_level_values(0),
                            'medal': swim_medals.index.get_level_values(1), 'count': swim_medals.values})
swim_medals = swim_medals.pivot(index='Country', columns='medal', values='count')
swim_medals.fillna(0, inplace=True)
swim_medals.reset_index(inplace=True)
swim_medals['Total number of medals'] = swim_medals['Gold'] + swim_medals['Silver'] + swim_medals['Bronze']

cycle_medals = df1[['NOC', 'Medal']].loc[df1['Sport'] == 'Cycling'].dropna().value_counts()
cycle_medals = pd.DataFrame({'Country': cycle_medals.index.get_level_values(0),
                             'medal': cycle_medals.index.get_level_values(1), 'count': cycle_medals.values})
cycle_medals = cycle_medals.pivot(index='Country', columns='medal', values='count')
cycle_medals.fillna(0, inplace=True)
cycle_medals.reset_index(inplace=True)
cycle_medals['Total number of medals'] = cycle_medals['Gold'] + cycle_medals['Silver'] + cycle_medals['Bronze']

ski_medals = df1[['NOC', 'Medal']].loc[df1['Sport'].str.contains('Skiing')].dropna().value_counts()
ski_medals = pd.DataFrame({'Country': ski_medals.index.get_level_values(0),
                           'medal': ski_medals.index.get_level_values(1), 'count': ski_medals.values})
ski_medals = ski_medals.pivot(index='Country', columns='medal', values='count')
ski_medals.fillna(0, inplace=True)
ski_medals.reset_index(inplace=True)
ski_medals['Total number of medals'] = ski_medals['Gold'] + ski_medals['Silver'] + ski_medals['Bronze']

# Convert NOC into countries names


country_name_table = {'USA': 'United States', 'URS': 'Soviet Union', 'GER': 'Germany', 'GBR': 'Great Britain',
                      'ITA': 'Italy', 'FRA': 'France', 'SWE': 'Sweden', 'CAN': 'Canada', 'HUN': 'Hungary',
                      'GDR': 'East Germany', 'RUS': 'Russia', 'NOR': 'Norway', 'CHN': 'China', 'AUS': 'Australia',
                      'NED': 'Netherlands', 'JPN': 'Japan', 'KOR': 'South Korea', 'FIN': 'Finland', 'DEN': 'Denmark',
                      'POL': 'Poland', 'SUI': 'Switzerland', 'ESP': 'Spain', 'AUT': 'Austria', 'ROU': 'Romania'}

gold['Country'].replace(country_name_table, inplace=True)
medals['Country'].replace(country_name_table, inplace=True)

# Convert NOC into ISO

noc_to_iso = {'GER': 'DEU', 'SUI': 'CHE', 'POR': 'PRT', 'NED': 'NLD', 'DEN': 'DNK', 'CRO': 'HRV', 'INA': 'IDN',
              'MAS': 'MYS', 'UAE': 'ARE', 'KSA': 'SAU', 'IRI': 'IRN', 'CHI': 'CHL', 'BUL': 'BLR'}

world_medals['Country'].replace(noc_to_iso, inplace=True)
running_medals['Country'].replace(noc_to_iso, inplace=True)
gym_medals['Country'].replace(noc_to_iso, inplace=True)
swim_medals['Country'].replace(noc_to_iso, inplace=True)
cycle_medals['Country'].replace(noc_to_iso, inplace=True)
ski_medals['Country'].replace(noc_to_iso, inplace=True)

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
                          color='Total number of medals',
                          hover_data=['Gold', 'Silver', 'Bronze'],
                          color_continuous_scale=px.colors.sequential.amp)

running_fig = px.choropleth(running_medals, locations='Country',
                            color='Total number of medals',
                            hover_data=['Gold', 'Silver', 'Bronze'],
                            color_continuous_scale=px.colors.sequential.Redor)

gym_fig = px.choropleth(gym_medals, locations='Country',
                        color='Total number of medals',
                        hover_data=['Gold', 'Silver', 'Bronze'],
                        color_continuous_scale=px.colors.sequential.Redor)

swim_fig = px.choropleth(swim_medals, locations='Country',
                         color='Total number of medals',
                         hover_data=['Gold', 'Silver', 'Bronze'],
                         color_continuous_scale=px.colors.sequential.Redor)

cycle_fig = px.choropleth(cycle_medals, locations='Country',
                          color='Total number of medals',
                          hover_data=['Gold', 'Silver', 'Bronze'],
                          color_continuous_scale=px.colors.sequential.Redor)

ski_fig = px.choropleth(ski_medals, locations='Country',
                        color='Total number of medals',
                        hover_data=['Gold', 'Silver', 'Bronze'],
                        color_continuous_scale=px.colors.sequential.Redor)

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
            id='graph_type',
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
    ]),
    html.Div([
        html.H1(children='Map of medals won by sport'),
        dcc.RadioItems(
            id='map_type',
            options=[{'label': i, 'value': i} for i in ['Athletics', 'Gymnastics', 'Swimming', 'Cycling', 'Skiing']],
            value='Athletics',
            labelStyle={'display': 'inline-block'},
            style={
                'fontSize': 20
            },
        ),
        dcc.Graph(
            id='sport_fig'
        )
    ])
])


@app.callback(
    Output('medal_fig', 'figure'),
    [Input('graph_type', 'value')])
def build_graph(graph_type):
    if graph_type == 'only golden medals':
        return gold_medal_fig
    else:
        return medal_fig


@app.callback(
    Output('sport_fig', 'figure'),
    [Input('map_type', 'value')])
def build_graph(map_type):
    if map_type == 'Athletics':
        return running_fig
    if map_type == 'Gymnastics':
        return gym_fig
    if map_type == 'Swimming':
        return swim_fig
    if map_type == 'Cycling':
        return cycle_fig
    if map_type == 'Skiing':
        return ski_fig


if __name__ == '__main__':
    app.run_server(debug=True)
