import pandas as pd
import plotly.express as px
import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Input
from dash import Output
from dash import dcc
from dash import html
import plotly.graph_objects as go

df1 = pd.read_csv('athlete_events.csv')

df1 = df1.drop_duplicates(subset=['Team', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])


# fig_year_sport = px.scatter(df1[df1["Season"]=="Summer"], x="Year", y="Sport")
fig_year_sport = px.scatter(df1.query("Season=='Summer'"), x="Year", y="Sport")

fig_year_sport['data'][0]['marker']['symbol'] = "square"
fig_year_sport.update_layout(
    height=800,
    yaxis = dict(
    tickfont = dict(size=8))
    )



    


# fig.show()



# importing datasets

df_athlete_event = pd.read_csv('athlete_events.csv')
df_athlete_event = df_athlete_event.drop_duplicates(subset=['Team', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

#Poid/Taille en fonction du sport
df2 = df_athlete_event.query("Season=='Summer'")[["Sex", "Sport","Weight","Height"]]
grouped_df = df2.groupby(["Sex","Sport"])
mean_df = grouped_df.mean().reset_index()
fig_weight_height = px.scatter(mean_df,x="Weight",y="Height",color="Sport",text="Sport", facet_col="Sex")
fig_weight_height.update_traces(textposition='middle right', textfont_size=8)
fig_weight_height.update_layout(
    height=600,
)
#Poid Taille age
df2 = df_athlete_event.query("Season=='Summer'")[["Sex", "Sport","Weight","Height","Age"]]
grouped_df = df2.groupby(["Sex","Sport"])
mean_df = grouped_df.mean().reset_index()
fig_3d_w_h_a = px.scatter_3d(mean_df,x="Weight",z="Height",y="Age",color="Sex",text="Sport")
fig_3d_w_h_a.update_traces(textposition='middle right', textfont_size=8)
fig_3d_w_h_a.update_layout(
    height=700,
)





# Start of the application
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div([
        html.H1(children='Olympic Games Dashboard', style={'textAlign': 'center', 'margin': '15px'}),
    ]),
    html.Div([
        dcc.Graph(
            figure=fig_year_sport
        )
    ]),
    html.Div([
        html.H2(children='Poids/Taille en fonction du sport (Editions d\'été)', style={'margin': '15px'}),
        html.P(children='Double clic sur la légende pour sélectionner les sports voulus', style={'margin': '15px'}),
    ]),
    html.Div([
        dcc.Graph(
            figure=fig_weight_height
        )
    ]),
    html.Div([
        dcc.Graph(
            figure=fig_3d_w_h_a
        )
    ]),
])



if __name__ == '__main__':
    app.run_server(debug=True)
