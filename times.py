import pandas as pd
import plotly.express as px
import dash
import numpy as np
from dash import Input
from dash import Output
from dash import dcc
from dash import html
import plotly.graph_objects as go


df = pd.read_csv('running_times.csv')
df['seconds'] = pd.to_timedelta(df['results']).dt.total_seconds()
fig_time_year = px.box(df, x="year", y="seconds", color="gender")
fig_time_year.update_traces(quartilemethod="exclusive")

fig = px.histogram(df, x="seconds", color="gender")




# Start of the application
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div([
        html.H1(children='Olympic Games Dashboard', style={'textAlign': 'center', 'margin': '15px'}),
    ]),
    html.Div([
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
            id='fig_time_year'
        ),
        dcc.Graph(
            id='histogram'
        )
    ]),
])

@app.callback(
    Output('fig_time_year', 'figure'),
    Input('running_type', 'value'),
)
def update_figure(value):
    fig_time_year = px.box(df.query("sport == @value"), x="year", y="seconds", color="gender")
    best_men = df.query("sport == @value and rank == 1 and gender == 'M' ") 
    best_women = df.query("sport == @value and rank == 1 and gender == 'W' ")
    fig_time_year.add_trace(go.Scatter(x=best_men["year"], y=best_men["seconds"], mode="lines", name="Best Men"))
    fig_time_year.add_trace(go.Scatter(x=best_women["year"], y=best_women["seconds"], mode="lines", name="Best Women"))
    return fig_time_year

@app.callback(
    Output('histogram', 'figure'),
    Input('running_type', 'value'),
)
def update_figure(value):
    fig = px.histogram(df.query("sport == @value"), x="seconds", color="gender")
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.6)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
