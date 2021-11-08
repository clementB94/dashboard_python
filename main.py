"""
Dashboard python about Olympics Games
After running open at http://127.0.0.1:8050/
"""

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from dash.dependencies import Output, Input
# import dash_core_components as dcc
# import dash_html_components as html
# from dash import Input
# from dash import Output
from dash import dcc
from dash import html
from scipy import stats

pd.options.mode.chained_assignment = None

################################################
# DATA IMPORTATION,PREPARATION AND AGGREGATION #
################################################

# importing the main dataset

df_athlete_events = pd.read_csv('athlete_events.csv')

# some team event count for multiples medals while in reality it counts for only one

df_athlete_events_unique = df_athlete_events.drop_duplicates(
    subset=['Team', 'NOC', 'Games', 'Season', 'Year', 'City', 'Sport', 'Event', 'Medal'])

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

# graph object layout

layout = go.Layout(margin=go.layout.Margin(l=15, r=15, t=25, b=15))

# creating dataframe of golden medals by country (only the first 20)

gold = df_athlete_events_unique[['NOC', 'Medal']]
gold = gold[gold['Medal'] == 'Gold']
gold = gold.NOC.value_counts()
gold = gold[:20]
gold = pd.DataFrame({'Country': gold.index, 'Number of golden medals': gold.values})

# creating dataframe of all medals by country (only the first 20)

medals = df_athlete_events_unique[['NOC', 'Medal']].dropna()
medals = medals.value_counts()

medals = pd.DataFrame({'Country': medals.index.get_level_values(0),
                       'medal': medals.index.get_level_values(1), 'count': medals.values})
africa_medals = medals[medals['Country'].isin(africa)]
europe_medals = medals[medals['Country'].isin(europe)]
america_medals = medals[medals['Country'].isin(america)]
asia_medals = medals[medals['Country'].isin(asia)]
medals = medals[medals['Country'].isin(gold['Country'])]

# Convert NOC into countries names

medals['Country'].replace(country_name_table, inplace=True)

# creating dataframe of all medals by country for time series map

years = sorted(df_athlete_events_unique['Year'].unique())
world_medals_time = {year: df_athlete_events_unique.query("Year <= @year") for year in years}

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


# generate map depending on sport

def gen_medals_by_sport(sport):
    """
        Generate a choropleth map of medals won by country on a specific sport.

        Args:
            sport: a sport name among all those of the Olympics

        Returns:
            a choropleth map figure
    """
    df_medals = df_athlete_events_unique[['NOC', 'Medal']].loc[
        df_athlete_events_unique['Sport'].str.contains(sport)].dropna().value_counts()
    df_medals = pd.DataFrame({'Country': df_medals.index.get_level_values(0),
                              'medal': df_medals.index.get_level_values(1), 'count': df_medals.values})
    df_medals = df_medals.pivot(index='Country', columns='medal', values='count')
    df_medals.fillna(0, inplace=True)
    df_medals.reset_index(inplace=True)
    df_medals['Total number of medals'] = df_medals['Gold'] + df_medals['Silver'] + df_medals['Bronze']
    df_medals['Country'].replace(noc_to_iso, inplace=True)
    sport_fig = px.choropleth(df_medals, locations='Country', color='Total number of medals',
                              hover_data=['Gold', 'Silver', 'Bronze'],
                              color_continuous_scale=px.colors.sequential.Redor, width=1100, height=550)
    return sport_fig


# creating dataframe for performances histogram

df_running_times = pd.read_csv('running_results.csv')
df_running_times['Performance'] = pd.to_timedelta(df_running_times['results']).dt.total_seconds()

df_athletics_results = pd.read_csv('athletics_results.csv')
for i, result in enumerate(df_athletics_results['results']):  # some results aren't in good format
    if result == 'mark unknown':
        df_athletics_results.drop(i, inplace=True)
    elif result[-1].isalpha():
        df_athletics_results['results'][i] = result[0:-1]
df_athletics_results['Performance'] = df_athletics_results['results'].astype(float)

df_swimming_results = pd.read_csv('swimming_results.csv')
df_swimming_results['Performance'] = pd.to_timedelta(df_swimming_results['results']).dt.total_seconds()

df_performance = df_athletics_results.append(df_running_times).append(df_swimming_results)

# generate dataframe for medal per gpd and medals per population

gpd_df = df_athlete_events_unique[['Team', 'Medal']].value_counts()
gpd_df = pd.DataFrame({'Country': gpd_df.index.get_level_values(0),
                       'medal': gpd_df.index.get_level_values(1), 'count': gpd_df.values})
gpd_df = gpd_df.pivot(index='Country', columns='medal', values='count')
gpd_df.fillna(0, inplace=True)
gpd_df.reset_index(inplace=True)
gpd_df['Total number of medals'] = gpd_df['Gold'] + gpd_df['Silver'] + gpd_df['Bronze']

df_GDP = pd.read_csv('GDP.csv')
df_GDP = df_GDP[['Country Name', '2020']]
gpd_df = pd.merge(left=gpd_df, right=df_GDP, left_on='Country', right_on='Country Name')
gpd_df = gpd_df.rename(columns={'2020': 'GDP 2020'})
gpd_df['Log GDP'] = np.log(gpd_df['GDP 2020'])

df_population = pd.read_csv('Population.csv')
df_population = df_population[['Country', 'Year_2016']]
gpd_df = pd.merge(left=gpd_df, right=df_population, left_on='Country', right_on='Country')
gpd_df = gpd_df.rename(columns={'Year_2016': 'Population 2016'})
gpd_df['Log Population'] = np.log(gpd_df['Population 2016'])


# dataframe of sports and player wise medal count

# df_wise = pd.read_csv('athlete_events.csv')  # we don't need to remove duplicates


# creating sports and player wise figures
def gen_fig_count(df, count_by, column_width):
    """
            Generate a datatable of medals won by player/sport

            Args:
                df: a dataframe we want to display
                count_by: which variable we want to count by
                column_width: width of the columns in px

            Returns:
                the datatable
        """
    count_df = df[[count_by, 'Medal']].dropna().value_counts()
    count_df = pd.DataFrame({'Name': count_df.index.get_level_values(0),
                             'medal': count_df.index.get_level_values(1), 'count': count_df.values})
    count_df = count_df.pivot(index='Name', columns='medal', values='count')
    count_df = count_df.fillna(0).astype(int)
    count_df.reset_index(inplace=True)
    count_df['Total_number_of_medals'] = count_df['Bronze'] + count_df['Gold'] + count_df['Silver']
    count_df = count_df.sort_values(by='Total_number_of_medals', ascending=False)
    if count_by == 'Sport':
        merge = df['Sport'].value_counts().rename_axis('Sport').reset_index(name='counts')
        count_df = pd.merge(left=count_df, right=merge, left_on='Name', right_on='Sport')
        return go.Figure(data=[go.Table(columnwidth=column_width,
                                        header=dict(values=['Sport', 'Gold', 'Silver', 'Bronze',
                                                            'Total number of medals']),
                                        cells=dict(values=[count_df.Name + ', ' +
                                                           count_df.counts.astype(str) + ' times',
                                                           count_df.Gold, count_df.Silver,
                                                           count_df.Bronze,
                                                           count_df.Total_number_of_medals]))
                               ], layout=layout)
    elif count_by == 'Name':
        merge = df[['Name', 'Team']].groupby('Name').first().reset_index()
        count_df = pd.merge(left=count_df, right=merge, left_on='Name', right_on='Name')
        return go.Figure(data=[go.Table(columnwidth=column_width,
                                        header=dict(values=['Player', 'Gold', 'Silver', 'Bronze',
                                                            'Total number of medals']),
                                        cells=dict(values=[count_df.Name + ', ' + count_df.Team,
                                                           count_df.Gold, count_df.Silver,
                                                           count_df.Bronze,
                                                           count_df.Total_number_of_medals],
                                                   align='center'))
                               ], layout=layout)
    return


# Weight/Height by sport dataframe and figure
def gen_fig_weight_height():
    grouped_df = df_athlete_events[df_athlete_events["Season"] == "Summer"][
        ["Sex", "Sport", "Weight", "Height", "Age"]]
    grouped_df = grouped_df.groupby(["Sex", "Sport"])
    mean_df = grouped_df.mean().round(2).reset_index()
    mean_df['Sex'] = mean_df['Sex'].replace('F', 'W')
    fig_weight_height = px.scatter(mean_df, x="Weight", y="Height", color="Sport", text="Sport",
                                   facet_col="Sex", hover_data=["Age"], labels={"Weight": "Weight (kg)",
                                                                                "Height": "Height (cm)"})
    fig_weight_height.layout.yaxis2.update(matches=None)
    fig_weight_height.layout.xaxis2.update(matches=None)
    fig_weight_height.update_traces(textposition='middle right', textfont_size=8)
    return fig_weight_height


# Sports history trough time
df_sports = df_athlete_events[["Sport", "Year", "Season"]].drop_duplicates(subset=["Year", "Sport", "Season"])
df_sports_year = df_sports.groupby(["Sport"]).describe()["Year"]

sports_historic_categories = {"all": df_sports_year.index.tolist(),
                              "<1950": df_sports_year[df_sports_year["max"] <= 1950].index.tolist(),
                              ">1950": df_sports_year[df_sports_year["min"] >= 1950].index.tolist(),
                              "always_summer": df_sports_year[
                                  (df_sports_year["min"] <= 1900) & (df_sports_year["max"] == 2016)].index.tolist(),
                              "always_winter": df_sports_year[
                                  (df_sports_year["min"] == 1924) & (df_sports_year["max"] >= 2013)].index.tolist()}

#####################################
# APPLICATION ARCHITECTURE AND HTML #
#####################################

# Start of the application

app = dash.Dash(__name__)
app.layout = html.Div(className='background', children=[
    html.Div([
        html.H1(children='Olympic Games Dashboard', style={'textAlign': 'center', 'font-size': '48px'}),
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
        dcc.Slider(id="year_slider", marks=year_slider, step=None, min=1896, max=2016, value=2016),
        dcc.Interval(id='interval', interval=500, n_intervals=0, disabled=True),
    ], className='container'),

    html.Div([
        html.H1(children='Map of medals won by sport', style={'textAlign': 'center'}),
        dcc.RadioItems(
            id='map_type',
            options=[{'label': i, 'value': i} for i in ['Athletics', 'Gymnastics', 'Swimming', 'Cycling', 'Ski',
                                                        'Wrestling', 'Shooting', 'Canoeing', 'Skating', 'Fencing',
                                                        'Archery', 'Rowing', 'Football', 'Volleyball', 'Diving',
                                                        'Equestrianism', 'Sailing', 'Weightlifting', 'Basketball',
                                                        'Hockey', 'Boxing', 'Art Competitions', 'Judo', 'Tennis']],
            value='Athletics',
            labelStyle={'display': 'inline-block'},
            style={'fontSize': 20, 'textAlign': 'center', 'width': '95%'},
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
            html.Div(children=['Type of sport : '], style={'display': 'inline-block', 'margin-right': '15px'}),
            dcc.Dropdown(options=[{'label': 'running', 'value': 'running'},
                                  {'label': 'athletics', 'value': 'athletics'},
                                  {'label': 'swimming', 'value': 'swimming'}],
                         value='running', id='sport_type',
                         style={'display': 'inline-block', 'width': '150px',
                                'margin-right': '35px', 'verticalAlign': 'middle'}),
            html.Div(children=['Sport : '], style={'display': 'inline-block', 'margin-right': '15px'}),
            dcc.Dropdown(value='100m', id='running_type',
                         style={'display': 'inline-block', 'width': '150px',
                                'margin-right': '55px', 'verticalAlign': 'middle'}),
            dcc.RadioItems(options=[{'label': 'men', 'value': 'M'}, {'label': 'women', 'value': 'W'}],
                           value='M', labelStyle={'display': 'inline-block'}, id='men_women',
                           style={'display': 'inline-block'})
        ], style={'textAlign': 'center'}),

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
            # dcc.Graph(figure=fig_weight_height),
            dcc.Graph(figure=gen_fig_weight_height()),

        ])
    ], className='container'),
    html.Div(children=[
        html.H1(children='Sports and players wise medal Count', style={'textAlign': 'center'}),
        html.Div(children=[
            dcc.Graph(figure=gen_fig_count(df_athlete_events_unique, 'Sport', [200, 90, 90, 90, 250]),
                      style={'display': 'inline-block', 'width': '50%'}),
            dcc.Graph(figure=gen_fig_count(df_athlete_events, 'Name', [180, 90, 90, 90, 250]),
                      style={'display': 'inline-block', 'width': '50%'}),
        ]),
    ], className='container'),
    html.Div(children=[
        html.H1(children='Medal count by GDP and Population', style={'textAlign': 'center'}),
        html.Div(children=[
            dcc.Graph(figure=px.scatter(gpd_df, x='Log GDP', y='Total number of medals',
                                        hover_data=['GDP 2020', 'Country'],
                                        trendline="ols"),
                      style={'display': 'inline-block', 'width': '50%'}),
            dcc.Graph(figure=px.scatter(gpd_df, x='Log Population', y='Total number of medals',
                                        hover_data=['Population 2016', 'Country'],
                                        trendline="ols"),
                      style={'display': 'inline-block', 'width': '50%'})
        ]),
    ], className='container'),

    html.Div([
        html.H1(children='Sport history', style={'textAlign': 'center'}),
        html.Div([
            dcc.Tabs(id="sport_history_choice", value='all', children=[
                dcc.Tab(label='All sports', value='all'),
                dcc.Tab(label='Practiced since the beginning (Summer)', value='always_summer'),
                dcc.Tab(label='Practiced since the beginning (Winter)', value='always_winter'),
                dcc.Tab(label='Before 1950', value='<1950'),
                dcc.Tab(label='After 1950', value='>1950')
            ]),
        ], style={'textAlign': 'center'}),

        dcc.Graph(
            id='sport_history'
        ),

    ], className='container')

])


##############################
# INTERACTIONS AND CALLBACKS #
##############################

@app.callback(
    Output('medal_fig', 'figure'),
    [Input('graph_type', 'value')])
def build_graph(graph_type):
    # returns either the bar graph of the 20 greatest countries or only Europe or only America or only Africa
    medal_choice = {
        'world': medals,
        'europe_medals': europe_medals,
        'america_medals': america_medals,
        'asia_medals': asia_medals,
        'africa_medals': africa_medals,
    }
    return px.bar(medal_choice[graph_type], x='Country', y='count', color='medal',
                  color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#c96'})


@app.callback(
    Output('sport_fig', 'figure'),
    [Input('map_type', 'value')])
def build_map(value):
    # return a choropleth map of medals won by country on a specific sport
    return gen_medals_by_sport(value)


@app.callback(
    Output('world_fig', 'figure'),
    [Input('year_slider', 'value')]
)
def update_figure(input_value):
    """
    return a choropleth map of medals won by country until a specific year
    """
    return px.choropleth(world_medals_time[input_value], locations='Country',
                         color='Total number of medals',
                         hover_data=['Gold', 'Silver', 'Bronze'],
                         color_continuous_scale=px.colors.sequential.Bluyl,
                         range_color=[0, 2700], width=1100, height=550)


@app.callback(Output('year_slider', 'value'),
              [Input('interval', 'n_intervals')]
              )
def on_tick(n_intervals):
    """
    make the slider scrolls the choropleth map
    """
    if n_intervals is None:
        return 0
    return years[(n_intervals + 1) % len(years)]


@app.callback(
    Output('slider-output-container', 'children'),
    Input('year_slider', 'value')
)
def update_output(value):
    # update the year prompt
    return 'Map of the year {}'.format(value)


@app.callback(Output('interval', 'disabled'),
              Input('play', 'n_clicks'),
              Input('pause', 'n_clicks'))
def play(play, pause):
    """
    pause or play the slider
    """
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'pause' in changed_id:
        return True
    if 'play' in changed_id:
        return False


@app.callback(
    Output('running_type', 'options'),
    Output('running_type', 'value'),
    Input('sport_type', 'value')
)
def update_dropdown(value):
    """
    update the sport dropdown
    """
    if value == 'running':
        options = [{'label': sport, 'value': sport}
                   for sport in df_running_times['sport'].unique()]
        return options, '100m'
    if value == 'swimming':
        options = [{'label': sport, 'value': sport}
                   for sport in df_swimming_results['sport'].unique()]
        return options, '100m backstroke'
    if value == 'athletics':
        options = [{'label': sport, 'value': sport}
                   for sport in df_athletics_results['sport'].unique()]
        return options, 'discus throw'


@app.callback(
    Output('fig_time_year', 'figure'),
    Input('running_type', 'value'),
    Input('men_women', 'value'),
    Input('sport_type', 'value')
)
def update_figure(value, gender_choice, sport_type):
    """
    return a performance graph for each year
    """
    performance_df = df_performance.query("sport == @value and gender == @gender_choice")
    if sport_type == 'running':
        performance_df = performance_df[(np.abs(stats.zscore(performance_df['Performance'])) < 3)]
    fig_box_performance = px.box(performance_df, x="year", y="Performance")
    fig_box_performance.update_traces(quartilemethod="exclusive")
    best = performance_df.query("sport == @value and rank == 1 and gender == @gender_choice ")
    fig_box_performance.add_trace(go.Scatter(x=best["year"], y=best["Performance"], mode="lines", showlegend=False,
                                             hovertext=best['name'] + " " + best['country'] + " " + best['results']))
    return fig_box_performance


@app.callback(
    Output('histogram', 'figure'),
    Input('running_type', 'value'),
    Input('men_women', 'value'),
    Input('sport_type', 'value')
)
def update_histogram(value, gender_choice, sport_type):
    """
    return a performance histogram on a specific sport and gender
    """
    performance_df = df_performance.query("sport == @value and gender == @gender_choice")
    if sport_type == 'running':
        performance_df = performance_df[(np.abs(stats.zscore(performance_df['Performance'])) < 3)]  # remove outliers
    fig_hist_performance = px.histogram(performance_df, x="Performance")
    fig_hist_performance.update_layout(barmode='overlay')
    return fig_hist_performance


@app.callback(
    Output('sport_history', 'figure'),
    Input('sport_history_choice', 'value'),
)
def update_sport_history(value):
    """
    return a historic of sports in each editions
    """
    sport_list = sports_historic_categories[value]
    fig_year_sport = px.scatter(df_sports.query("Sport in @sport_list"), x="Year", y="Sport", color="Season")
    fig_year_sport.update_traces(marker=dict(size=9, symbol='square'))

    return fig_year_sport


if __name__ == '__main__':
    app.run_server(debug=True)
