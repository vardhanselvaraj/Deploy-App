import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input
import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

df = pd.read_csv('Red_Light_Camera_Violations.csv')
df.head()

df.dropna(how = 'any', inplace = True)

map = px.density_mapbox(df,  lat = 'LATITUDE', lon = 'LONGITUDE', z = 'VIOLATIONS',
                        radius = 10 , center = dict(lat = 41.8781, lon = -87.6298), zoom = 8,
                        mapbox_style = "open-street-map")
# map.show()

df['VIOLATION DATE'] = df['VIOLATION DATE'].astype('datetime64[ns]')

df1 = df[['VIOLATION DATE','VIOLATIONS']].groupby('VIOLATION DATE').count()
df1['violation_date'] = df1.index

df2 = df[['INTERSECTION','VIOLATION DATE','VIOLATIONS']].groupby(['VIOLATION DATE','INTERSECTION']).count().reset_index()
df2.index = df2['VIOLATION DATE']

app = dash.Dash(external_stylesheets = [dbc.themes.YETI] )
server = app.server
app.title = 'Traffic App'

navbar = dbc.Nav(className="nav vardhan",
                 children=[
                     dbc.NavItem(html.Img(src = "assets/traffic-light.png", height  = "40px"),id = "navbarColor02"),
                     dbc.NavItem(html.Div([
                         html.H3('')
                     ]))
                 ])
inputs = dbc.FormGroup([
    html.H3("Select the Date Range"),
    dcc.DatePickerRange(id = 'Date_Input',  initial_visible_month = dt(2014,7,4))
])

app.layout = dbc.Container(fluid = True, children=[
    html.H1("Chicago Traffic Violations Tracker", id = "vardhan"),
    navbar,
    html.Br(),html.Br(),

    dbc.Row([
        dbc.Col(md=3, children = [
            inputs,
            html.Br(),html.Br(), html.Br()
        ]),
        dbc.Col(md = 9, children= [
            dbc.Col(html.H5('Total Violations per Day and Major Intersections for a Date Range'),
                    width={"size":6,"offset":3}),
            html.Br(),
            dbc.Tabs(className="nav vardhan",children=[
                dbc.Tab(dcc.Graph(id = "first_graph"),label = "Total Violations per day"),
                dbc.Tab(dcc.Graph(id = 'second_chart'),label = "Intersections Causing the Most Violations")
            ])
        ])
    ])
])

@app.callback(dash.dependencies.Output("first_graph","figure"),
              [dash.dependencies.Input('Date_Input','start_date'),
               dash.dependencies.Input('Date_Input','end_date')],
)

def update_output(start_date, end_date):
    start = start_date
    end = end_date
    data = []
    violations_chart = go.Scatter(x=list(df1['violation_date'].loc[start:end]),
                                  y=list(df1['VIOLATIONS']),
                                  name='Number of Violations',
                                  mode='markers',
                                  marker=dict(color='#d4af4a',
                                              size =12),
                                  line=dict(color = 'DarkSlateGrey',
                                            width = 1),

                                  )

    data.append(violations_chart)

    layout = dict(title='Violations Chart',
                  showlegend=True,
                  xaxis_title = "Date Ranges",
                  yaxis_title = 'Total Violations',
                  template = 'plotly_white',
                  font = dict(family = 'Avenir', size = 15, color = 'black'))

    return {
        'data' : data,
        'layout':layout
    }

@app.callback(
    Output('second_chart','figure'),
    [Input('Date_Input','start_date'),
     Input('Date_Input','end_date')]
)
def update_output_1(start_date, end_date):
    updated_df = df2[['INTERSECTION','VIOLATIONS']].loc[start_date:end_date]
    updated_df = updated_df[['INTERSECTION','VIOLATIONS']].groupby('INTERSECTION')\
        .sum().reset_index()\
        .sort_values(by='VIOLATIONS', ascending=False)

    data2  = []
    bar_chart = go.Bar(x = updated_df['INTERSECTION'].head(),
                       y = updated_df['VIOLATIONS'].head(),
                       marker_color = '#d4af4a',
                       width = 0.4 ,
                       text = 'No. Of Violations')

    data2.append(bar_chart)
    layout = dict(title = 'Intersections with Maximum Violations',
                  showlegend = False
                  # font=dict(family='Avenir', size=15, color='black')
                  )
    return{
        'data': data2,
        'layout': layout
    }

if __name__ == "__main__":
    app.run_server(port = 4030)