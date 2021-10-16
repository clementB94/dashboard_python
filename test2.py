import dash
import pandas as pd
import plotly.express as px
import numpy as np
from dash import Input
from dash import Output
from dash import dcc
from dash import html
import plotly.graph_objects as go
from scipy import stats

pd.options.mode.chained_assignment = None

# importing datasets

df1 = pd.read_csv('athlete_events.csv')
df1 = df1.drop_duplicates(subset=['Team', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

df2 = pd.read_csv('running_times.csv')

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

# NOC codes by region

africa = ['ALG', 'LBA', 'EGY', 'MAR', 'SUD', 'TUN', 'BEN', 'BUR', 'GAM', 'GHA', 'GUI', 'GBS', 'CIV', 'LBR', 'MTN',
          'MLI', 'MTN', 'NIG', 'NGR', 'SEN', 'CMR', 'GAB', 'KEN', 'RWA', 'ETH', 'ANG', 'BOT', 'RSA', 'ZAM', 'ZIM', ]

europe = ['AUT', 'BEL', 'BIH', 'BUL', 'CRO', 'CZE', 'DEN', 'EST', 'FIN', 'FRA', 'GER', 'GBR', 'GRE', 'HUN', 'ISL',
          'IRL', 'ITA', 'LAT', 'LTU', 'NED', 'NOR', 'POL', 'POR', 'ROU', 'RUS', 'AUT', 'SRB', 'SVK', 'SLO', 'ESP',
          'SWE', 'SUI', 'IRL', 'TUR', 'UKR']

america = ['USA', 'ARG', 'BRA', 'CAN', 'CHI', 'COL', 'CRC', 'CUB', 'DOM', 'HAI', 'JAM', 'MEX', 'NCA', 'PAN', 'PAR',
           'PUR', 'URU', 'VEN']

asia = ['IRI', 'IRQ', 'QAT', 'KSA', 'UAE', 'KAZ', 'IND', 'NEP', 'PAK', 'SRI', 'TPE', 'CHN', 'HKG', 'JPN', 'PRK', 'KOR',
        'MGL', 'CAM', 'INA', 'MAS', 'MYA', 'PHI', 'SGP', 'THA', 'VIE', 'ISR']

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
africa_medals = medals[medals['Country'].isin(africa)]
europe_medals = medals[medals['Country'].isin(europe)]
america_medals = medals[medals['Country'].isin(america)]
asia_medals = medals[medals['Country'].isin(asia)]
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

df2 = pd.read_csv('running_times.csv')
df2['seconds'] = pd.to_timedelta(df2['results']).dt.total_seconds()
fig_time_year = px.box(df2, x="year", y="seconds")
fig_time_year.update_traces(quartilemethod="exclusive")
fig = px.histogram(df2, x="seconds")

# Convert NOC into countries names

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

# Weight/Height by sport

grouped_df = df1[df1["Season"] == "Summer"][["Sex", "Sport", "Weight", "Height", "Age"]]
grouped_df = grouped_df.groupby(["Sex", "Sport"])
mean_df = grouped_df.mean().round(2).reset_index()
fig_weight_height = px.scatter(mean_df, x="Weight", y="Height", color="Sport", text="Sport", facet_col="Sex")
fig_weight_height.layout.yaxis2.update(matches=None)
fig_weight_height.layout.xaxis2.update(matches=None)
fig_weight_height.update_traces(textposition='middle right', textfont_size=8)

# Building Figures

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

app.layout = html.Div(className='background', children=[
    html.Div([
        html.H1(children='Olympic Games Dashboard', style={'textAlign': 'center'}),
    ]),
    html.Div([
        html.H1(children='Total amount of medals', style={'textAlign': 'center'}),
        dcc.Tabs(id="graph_type", value='world', children=[
            dcc.Tab(label='Worldwide', value='world'),
            dcc.Tab(label='Europe', value='europe_medals'),
            dcc.Tab(label='America', value='america_medals'),
            dcc.Tab(label='Asia', value='asia_medals'),
            dcc.Tab(label='Africa', value='africa_medals')
        ]),
        dcc.Graph(
            id='medal_fig'
        )
    ], className='container'),
    html.Div([
        html.H1(children='map of the evolution of medals won', style={'textAlign': 'center'}),
        html.Div(id='slider-output-container', style={'textAlign': 'center'}),
        html.Div([
            dcc.Graph(
                id='world_fig', style={'margin-left': '8%'}
            ),
        ]),
        html.Div([
            html.Button('play', id='play'),
            html.Button('pause', id='pause')
        ], style={'textAlign': 'center'}),
        dcc.Slider(id="year_slider", marks=year_slider, step=None, min=1896, max=2016, value=2016, className='slider'),
        dcc.Interval(id='interval', interval=500, n_intervals=0, disabled=True),
    ], className='container'),

    html.Div([
        html.H1(children='Map of medals won by sport', style={'textAlign': 'center'}),
        dcc.RadioItems(
            id='map_type',
            options=[{'label': i, 'value': i} for i in ['Athletics', 'Gymnastics', 'Swimming', 'Cycling', 'Skiing']],
            value='Athletics',
            labelStyle={'display': 'inline-block'},
            style={'fontSize': 20, 'textAlign': 'center'},
        ),
        html.Div([
            dcc.Graph(
                id='sport_fig', style={'margin-left': '8%'}
            )
        ])
    ], className='container'),
    html.Div([
        html.H1(children='Performances by edition', style={'textAlign': 'center'}),
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
            dcc.RadioItems(options=[{'label': 'men', 'value': 'M'}, {'label': 'women', 'value': 'W'}],
                           value='M', labelStyle={'display': 'inline-block'}, id='men_women')
        ], style={'width': '20%', 'textAlign': 'center'}),

        dcc.Graph(
            id='fig_time_year'
        ),
        dcc.Graph(
            id='histogram'
        ),
    ], className='container'),
    html.Div([
        html.Div([
            html.H1(children='Weight/Height by sport (summer editions)'),
            html.P(children='click on legend to display particular sports', style={'margin': '15px'}),
        ], style={'textAlign': 'center'}),
        html.Div([
            dcc.Graph(figure=fig_weight_height),
        ])
    ], className='container')
])


@app.callback(
    Output('medal_fig', 'figure'),
    [Input('graph_type', 'value')])
def build_graph(graph_type):
    if graph_type == 'world':
        return medal_fig
    if graph_type == 'europe_medals':
        return px.bar(europe_medals, x='Country', y='count', color='medal',
                      color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#c96'})
    if graph_type == 'america_medals':
        return px.bar(america_medals, x='Country', y='count', color='medal',
                      color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#c96'})
    if graph_type == 'asia_medals':
        return px.bar(asia_medals, x='Country', y='count', color='medal',
                      color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#c96'})
    if graph_type == 'africa_medals':
        return px.bar(africa_medals, x='Country', y='count', color='medal',
                      color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#c96'})


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
    Output('fig_time_year', 'figure'),
    Input('running_type', 'value'),
    Input('men_women', 'value')
)
def update_figure(value, gender_choice):
    performance_df = df2.query("sport == @value and gender == @gender_choice")
    performance_df = performance_df[(np.abs(stats.zscore(performance_df['seconds'])) < 3)]
    fig_time_year = px.box(performance_df, x="year", y="seconds")
    best_men = df2.query("sport == @value and rank == 1 and gender == @gender_choice ")
    fig_time_year.add_trace(go.Scatter(x=best_men["year"], y=best_men["seconds"], mode="lines", showlegend=False,
                                       hovertext=best_men['name'] + "\n" + best_men['country']))

    return fig_time_year


@app.callback(
    Output('histogram', 'figure'),
    Input('running_type', 'value'),
    Input('men_women', 'value')
)
def update_figure(value, gender_choice):
    performance_df = df2.query("sport == @value and gender == @gender_choice")
    performance_df = performance_df[(np.abs(stats.zscore(performance_df['seconds'])) < 3)]
    fig = px.histogram(performance_df, x="seconds")
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.6)
    return fig


@app.callback(
    dash.dependencies.Output('slider-output-container', 'children'),
    [dash.dependencies.Input('year_slider', 'value')])
def update_output(value):
    return 'Map of the year {}'.format(value)


if __name__ == '__main__':
    app.run_server(debug=True)

# TO DO LIST : premier barplot en fontion de amérique europe et asie
# les chiffres de la map evolutive qui se chevauchent pas et retravailler l'axe des couleurs
# peut etre indiquer le pays qui organise
# le 3eme graphique retravailler l'échelle et peut etre rajouter des domaines
# les meilleures performances prendre l'autre avec courbe plus boxplot, enlever les outlier, segmenter homme femme
# meilleures hover data
# generaliser ce dernier graph avec plus de domain et de sport
# sur l'histograme plus de bins
