import dash
import numpy as np
import numpy
import folium
import geojson
import geopandas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input
from dash import Output
from dash import dcc
from dash import html
from datetime import datetime
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
from geopy.geocoders import Nominatim

# importing datasets

df1 = pd.read_csv('athlete_events.csv')
df1 = df1.drop_duplicates(subset=['Team', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

df2 = pd.read_csv('running_times.csv')

# df2['results'] = pd.to_datetime(df2['results'], format='%H:%M:%S.%f')

# conversion tables

noc_to_iso = {'GER': 'DEU', 'SUI': 'CHE', 'POR': 'PRT', 'NED': 'NLD', 'DEN': 'DNK', 'CRO': 'HRV', 'INA': 'IDN',
              'MAS': 'MYS', 'UAE': 'ARE', 'KSA': 'SAU', 'IRI': 'IRN', 'CHI': 'CHL', 'SLO': 'SVN', 'GRE': 'GRC',
              'BUL': 'BGR', 'LAT': 'LVA', 'OMA': 'OMN', 'MGL': 'MNG', 'NEP': 'NPL', 'RSA': 'ZAF', 'GUI': 'GIN',
              'SLE': 'SLE', 'BOT': 'BWA', 'GBS': 'GNB', 'GAM': 'GMB', 'MLI': 'RMM', 'ALG': 'DZA', 'LBA': 'LBY',
              'ZIM': 'ZWE', 'ANG': 'AGO', 'CGO': 'COG', 'PAR': 'PRY', 'MAD': 'MDG', 'NIG': 'NER', 'NGR': 'NGA',
              'TOG': 'TGO', 'SUD': 'SDN', 'SRI': 'LKA', 'VIE': 'VNM', 'TPE': 'TWN', 'PHI': 'PHL', 'URU': 'URY',
              'GUA': 'GTM', 'CRC': 'CRI', 'HAI': 'HTI'}

country_name_table = {'USA': 'United States', 'URS': 'Soviet Union', 'GER': 'Germany', 'GBR': 'Great Britain',
                      'ITA': 'Italy', 'FRA': 'France', 'SWE': 'Sweden', 'CAN': 'Canada', 'HUN': 'Hungary',
                      'GDR': 'East Germany', 'RUS': 'Russia', 'NOR': 'Norway', 'CHN': 'China', 'AUS': 'Australia',
                      'NED': 'Netherlands', 'JPN': 'Japan', 'KOR': 'South Korea', 'FIN': 'Finland', 'DEN': 'Denmark',
                      'POL': 'Poland', 'SUI': 'Switzerland', 'ESP': 'Spain', 'AUT': 'Austria', 'ROU': 'Romania'}

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

# creating dataframe of all medals by country for time series map

years = sorted(df1['Year'].unique())
world_medals_time = {year: df1.query("Year <= @year") for year in years}

for year in world_medals_time.keys():
    world_medals_time[year] = world_medals_time[year][['NOC', 'Medal']].value_counts()
    world_medals_time[year] = pd.DataFrame({'Country': world_medals_time[year].index.get_level_values(0),
                                            'medal': world_medals_time[year].index.get_level_values(1),
                                            'count': world_medals_time[year].values})
    world_medals_time[year] = world_medals_time[year].pivot(index='Country', columns='medal', values='count')
    world_medals_time[year].fillna(0, inplace=True)
    world_medals_time[year].reset_index(inplace=True)
    world_medals_time[year]['Total number of medals'] = world_medals_time[year]['Gold'] + world_medals_time[year][
        'Silver'] + world_medals_time[year]['Bronze']
    world_medals_time[year]['Country'].replace(noc_to_iso, inplace=True)

# year_slider values

year_slider = {str(year): '{}'.format(year) for year in years}

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

# creating dataframe for performances histogram

# df2 = df2[df2['rank'] == 1]
# df2['results'] = pd.to_timedelta(df2['results'])

running_sports = df2['sport'].unique()
running_bar = {sport: df2.query("sport == @sport and rank == 1") for sport in running_sports}
for sport in running_sports:
    running_bar[sport]['seconds'] = pd.to_timedelta(running_bar[sport]['results']).dt.total_seconds()
    print(running_bar[sport])

# Convert NOC into countries names

gold['Country'].replace(country_name_table, inplace=True)
medals['Country'].replace(country_name_table, inplace=True)

# Convert NOC into ISO

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

# map figures

running_fig = px.choropleth(running_medals, locations='Country',
                            color='Total number of medals',
                            hover_data=['Gold', 'Silver', 'Bronze'],
                            color_continuous_scale=px.colors.sequential.Redor, width=1100, height=550)

gym_fig = px.choropleth(gym_medals, locations='Country',
                        color='Total number of medals',
                        hover_data=['Gold', 'Silver', 'Bronze'],
                        color_continuous_scale=px.colors.sequential.Redor, width=1100, height=550)

swim_fig = px.choropleth(swim_medals, locations='Country',
                         color='Total number of medals',
                         hover_data=['Gold', 'Silver', 'Bronze'],
                         color_continuous_scale=px.colors.sequential.Redor, width=1100, height=550)

cycle_fig = px.choropleth(cycle_medals, locations='Country',
                          color='Total number of medals',
                          hover_data=['Gold', 'Silver', 'Bronze'],
                          color_continuous_scale=px.colors.sequential.Redor, width=1100, height=550)

ski_fig = px.choropleth(ski_medals, locations='Country',
                        color='Total number of medals',
                        hover_data=['Gold', 'Silver', 'Bronze'],
                        color_continuous_scale=px.colors.sequential.Redor, width=1100, height=550)

# Start of the application

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div([
        html.H1(children='Olympic Games Dashboard', style={'textAlign': 'center', 'margin': '15px'}),
    ]),
    html.Div([
        dcc.RadioItems(
            id='graph_type',
            options=[{'label': i, 'value': i} for i in ['all medals', 'only golden medals']],
            value='all medals',
            labelStyle={'display': 'inline-block'},
            style={'fontSize': 20, 'textAlign': 'center'},
        ),
        dcc.Graph(
            id='medal_fig'
        )
    ]),
    html.Div([
        html.H1(children='map of the evolution of medals won', style={'textAlign': 'center', 'margin-top': '60px'}),
        html.Div(id='slider-output-container', style={'textAlign': 'center'}),
        html.Div([
            dcc.Graph(
                id='world_fig'
            ),
        ], style={'padding-left': '15%'}),
        html.Div([
            html.Button('play', id='play', style={'fontSize': 18}),
            html.Button('pause', id='pause', style={'fontSize': 18})
        ], style={'textAlign': 'center'}),
        dcc.Slider(id="year_slider", marks=year_slider, step=None, min=1896, max=2016, value=2016),
        dcc.Interval(id='interval', interval=500, n_intervals=0, disabled=True),
    ]),

    html.Div([
        html.H1(children='Map of medals won by sport', style={'textAlign': 'center', 'margin-top': '60px'}),
        dcc.RadioItems(
            id='map_type',
            options=[{'label': i, 'value': i} for i in ['Athletics', 'Gymnastics', 'Swimming', 'Cycling', 'Skiing']],
            value='Athletics',
            labelStyle={'display': 'inline-block'},
            style={'fontSize': 20, 'textAlign': 'center'},
        ),
        html.Div([
            dcc.Graph(
                id='sport_fig'
            )
        ], style={'padding-left': '15%'})
    ]),
    html.Div([
        html.H1(children='Best performances by edition', style={'textAlign': 'center', 'margin-top': '60px'}),
        html.Div([
            dcc.Dropdown(options=[{'label': '100m', 'value': '100m'}, {'label': '200m', 'value': '200m'},
                                  {'label': '400m', 'value': '400m'}, {'label': '800m', 'value': '800m'},
                                  {'label': '110m hurdles', 'value': '110m hurdles'},
                                  {'label': '100m hurdles', 'value': '100m hurdles'},
                                  {'label': '400m hurdles', 'value': '400m hurdles'},
                                  {'label': '1500m', 'value': '1500m'}, {'label': '5000m', 'value': '5000m'},
                                  {'label': '10000m', 'value': '10000m'}, {'label': 'marathon', 'value': 'marathon'}
                                  ],
                         value='100m', id='running_type', style={'textAlign': 'center'}),
        ], style={'width': '20%'}),
        dcc.Graph(
            id='performances_hist'
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


@app.callback(
    Output('world_fig', 'figure'),  # (1)
    [Input('year_slider', 'value')]  # (2)
)
def update_figure(input_value):
    return px.choropleth(world_medals_time[input_value], locations='Country',
                         color='Total number of medals',
                         hover_data=['Gold', 'Silver', 'Bronze'],
                         color_continuous_scale=px.colors.sequential.Bluyl,
                         range_color=[0, 2700], width=1100, height=550)


@app.callback(Output('year_slider', 'value'),
              [Input('interval', 'n_intervals')]
              )
def on_tick(n_intervals):
    if n_intervals is None:
        return 0
    return years[(n_intervals + 1) % len(years)]


@app.callback(Output('interval', 'disabled'),
              Input('play', 'n_clicks'),
              Input('pause', 'n_clicks'))
def play(play, pause):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'pause' in changed_id:
        return True
    if 'play' in changed_id:
        return False


@app.callback(
    Output('performances_hist', 'figure'),
    Input('running_type', 'value'),
)
def update_figure(value):
    return px.bar(running_bar[value], x='year', y='seconds', barmode='group', color='gender',
                  hover_data=['name', 'country', 'location', 'results'],
                  range_y=[min(running_bar[value]['seconds']*0.95), max(running_bar[value]['seconds']*1.05)])


@app.callback(
    dash.dependencies.Output('slider-output-container', 'children'),
    [dash.dependencies.Input('year_slider', 'value')])
def update_output(value):
    return 'Map of the year {}'.format(value)


if __name__ == '__main__':
    app.run_server(debug=True)
