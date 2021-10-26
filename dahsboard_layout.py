html.Div(className='background', children=[
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
            dcc.Dropdown(options=[{'label': sport, 'value': sport}
                                  for sport in df_running_times['sport'].unique()],
                         value='100m', id='running_type',
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
            dcc.Graph(figure=fig_weight_height),
        ])
    ], className='container'),
    html.Div(children=[
        html.H1(children='Sports and players wise medal Count', style={'textAlign': 'center'}),
        html.Div(children=[
            dcc.Graph(figure=fig_sport_wise, style={'display': 'inline-block', 'width': '50%'}),
            dcc.Graph(figure=fig_player_wise, style={'display': 'inline-block', 'width': '50%'}),
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
    ], className='container')
])