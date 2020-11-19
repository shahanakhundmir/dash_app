import csv
import datetime
import pandas as pd
import os

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
#import json
'''
with open('pingstats.csv', mode='w') as pingstats:
    ping_writer = csv.writer(pingstats, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    # csv header
    ping_writer.writerow(['date_time', 'packet_loss','latency'])
pingstats.close()  
'''
# dash app
colour = {'background': '#000000', 'border' : '#2f4f4f','text': '#ffffff', 'yel': '#ffff00'}
app = dash.Dash()

df = pd.read_csv('pingstats.csv')
df.dropna(inplace = True)
df['date_time'] = pd.to_datetime(df['date_time'])
df['date'] = df.date_time.dt.date
print(df['date'])

print(df['date_time'].min())
print(df['date_time'].max())

app.layout = html.Div(['Ping Statistics',
                       
    html.Div(id='interval-div-id'),
    html.Div(
        [dcc.Interval(id = 'interval-id',
        interval = 10000,
        n_intervals = 0)]),
    
    
    # Pick Date
#    html.Div([dcc.DatePickerSingle(id='date-picker-id',
#        min_date_allowed=df['date_time'].min(),
#        max_date_allowed=df['date_time'].max(),
#        initial_visible_month=df['date_time'].max(),
#        date =df['date_time'].max())]),
                      
    html.Div([dcc.Graph(id = 'graph-id')]), 
    ],      
    
    # style for main Div                   
    style={'background-color': colour['background'], 'border-style': 'solid', 'border-width': 'medium',
           'border-color': colour['border'], 'font-style': 'bold', 'font-size': '32px', 'color': colour['text'],
           'text-align': 'center'} 
)

# Update Graphs
@app.callback(
    dash.dependencies.Output('graph-id', 'figure'),
   [dash.dependencies.Input('interval-id', 'n_intervals')])
def refresh_page(interval):
    ping_target = ' 8.8.8.8'
    results = os.popen ('ping' + ping_target).read()
    date_time = datetime.datetime.now()
    packet_loss = results.split('Lost = ')[1].split('(')[0]
    latency = results.split('Average = ')[1].split('ms')[0]

    with open('pingstats.csv', mode='a') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow([date_time,packet_loss, latency])
    file.close()
    
    df = pd.read_csv('pingstats.csv')
    
    fig = make_subplots(rows=2, cols=1, start_cell ='bottom-left', subplot_titles =['Latency', 'Packet-Loss'])
    fig.update_layout(height=650)
    
    fig.append_trace(go.Scatter(
    x=df['date_time'],
    y=df['latency'],
    ), row=1, col=1)

    fig.append_trace(go.Scatter(
    x=df['date_time'],
    y=df['packet_loss'],
    ), row=2, col=1)

    return fig

# page refresh
@app.callback(
    dash.dependencies.Output('interval-div-id', 'children'),
   [dash.dependencies.Input('interval-id', 'n_intervals')])
def refresh_counter(interval):
     return ' refreshed {} times '.format(interval)

'''
# Select Date
@app.callback(
     dash.dependencies.Output('graph-id', 'figure'),
    [dash.dependencies.Input('date-picker-id', 'date')])
def update_date(date_value): 
    # select rows for only date chosen
    
    df = pd.read_csv('pingstats.csv')
    df = df[df['date_time'] == date_value]
    fig = make_subplots(rows=2, cols=1, start_cell ='bottom-left', subplot_titles =['Latency', 'Packet-Loss'])
    fig.update_layout(height=650)
    
    fig.append_trace(go.Scatter(
    x=df['date_time'],
    y=df['latency'],
    ), row=1, col=1)

    fig.append_trace(go.Scatter(
    x=df['date_time'],
    y=df['packet_loss'],
    ), row=2, col=1)

    return fig
'''

# run the dashboard
if __name__ == '__main__':
    app.run_server()