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

df1 = pd.read_csv('athlete_events.csv')

df1 = df1.drop_duplicates(subset=['Team', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])


# fig = px.scatter(df1[df1["Season"]=="Summer"], x="Year", y="Sport")
# fig.update_layout(
#     yaxis = dict(
#     tickfont = dict(size=10)))

# fig.show()



# importing datasets

df = pd.read_csv('athlete_events.csv')
df = df.drop_duplicates(subset=['Team', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

#Poid/Taille en fonction du sport
df2 = df[df["Season"]=="Summer"][["Sex", "Sport","Weight","Height"]]
grouped_df = df2.groupby(["Sex","Sport"])
mean_df = grouped_df.mean().reset_index()
fig = px.scatter(mean_df,x="Weight",y="Height",color="Sport",text="Sport", facet_col="Sex")
fig.update_traces(textposition='middle right', textfont_size=8)
fig.update_layout(
    height=600,
)
#Poid Taille age
df2 = df[df["Season"]=="Summer"][["Sex", "Sport","Weight","Height","Age"]]
grouped_df = df2.groupby(["Sex","Sport"])
mean_df = grouped_df.mean().reset_index()
fig2 = px.scatter_3d(mean_df,x="Weight",z="Height",y="Age",color="Sex",text="Sport")
fig2.update_traces(textposition='middle right', textfont_size=8)
fig2.update_layout(
    height=700,
)
# Start of the application

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div([
        html.H1(children='Olympic Games Dashboard', style={'textAlign': 'center', 'margin': '15px'}),
    ]),
    html.Div([
        html.H2(children='Poids/Taille en fonction du sport (Editions d\'été)', style={'margin': '15px'}),
        html.P(children='Double clic sur la légende pour sélectionner les sports voulus', style={'margin': '15px'}),
    ]),
    html.Div([
        dcc.Graph(
            figure=fig
        )
    ]),
    html.Div([
        dcc.Graph(
            figure=fig2
        )
    ]),
])



if __name__ == '__main__':
    app.run_server(debug=True)
