# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 21:18:14 2020

@author: shaha
"""
import csv
import datetime
import pandas as pd

import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import dash_auth

#import subprocess
#p = subprocess.Popen(["ping.exe","www.google.com"], stdout = subprocess.PIPE)
#print (p.communicate()[0])

# read csv
file_object  = open('C:/Users/shaha/OneDrive/Documents/data/pingstats', 'r') 

# open ping file to read from 
with open('pingstats.csv', mode='w') as pingstats:
    ping_writer = csv.writer(pingstats, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    # csv header
    ping_writer.writerow(['date_time','date', 'time', 'transmitted', 'received', 'packet_loss', 'minimum', 'maximum', 'avg', 'stddev'])
    
    # open csv file to write to 
    with open('C:/Users/shaha/OneDrive/Documents/data/pingstats') as input_file:
        for line in input_file:
            # timestamp denotes start of block, convert to datetime
            if 'GMT' in line:
                date_time = datetime.datetime.strptime(line[5:][:-5],'%d %b %Y %H:%M:%S')
                date = date_time.date()
                time = date_time.time()
            
            # split packet data
            elif 'packets transmitted' in line:
                metrics = line.split()
                transmitted = metrics[0]
                received = metrics[3]
                packet_loss = metrics[6][:-1]
            
            # split metric data
            elif 'round-trip' in line:
                stats = line.split('=')[1].split('/')
                minimum = stats[0][1:]
                maximum = stats[1]
                avg = stats[2]
                stddev = stats[3][:-4]
                #print([date, transmitted, received, packet_loss, minimum, maximum, avg, stddev])
                # write row to csv
                ping_writer.writerow([date_time, date,time, transmitted, received, packet_loss, minimum, maximum, avg, stddev])
    input_file.close()
pingstats.close()

# create a DataFrame from the .csv file:
df = pd.read_csv('C:/Users/shaha/OneDrive/Documents/Jupyter/pingstats.csv')


####
# need to substitue missing data / sleep time with 0
###
# dash app

colour = {'background': '#000000', 'border' : '#2f4f4f','text': '#ffffff', 'yel': '#ffff00'}

app = dash.Dash()

USER_PASSWORD_PAIRS = [['name', 'pass']]
auth = dash_auth.BasicAuth(app, USER_PASSWORD_PAIRS )
server = app.server

app.layout = html.Div(['Ping Statistics',
    html.Div(id='interval-div-id'),
    html.Div(
        [dcc.Interval(id = 'interval-id',
        interval = 60000,
        n_intervals = 0)
       ]),
    
                       
    # Pick Date
    html.Div([dcc.DatePickerSingle(id='date-picker-id',
        min_date_allowed=df['date'].min(),
        max_date_allowed=df['date'].max(),
        initial_visible_month=df['date'].max(),
        date=df['date'].max())]),
    # Pick Time            
   # html.Div([dcc.RangeSlider (id='slider-id', min = df['time'].min(), max = df['time'].max())]),
    
    # Graph 1
    html.Div([dcc.Graph(id = 'avg-id')],       
    style = {'background-color': colour['background'], 'border-style': 'solid', 'border-width': 'thin',
             'border-color': colour['border'], 'font-style': 'bold', 'font-size': '24px', 'color': colour['text'],
             'text-align': 'left'}),
    
    html.Div(id='avg-header-id'),
    
    # Graph 2   
    html.Div([dcc.Graph(id = 'packet-id')],  
    style = {'background-color':colour['background'], 'border-style': 'solid', 'border-width': 'thin',
             'border-color': colour['border'], 'font-style': 'bold', 'font-size': '24px', 'color': colour['text'],
             'text-align': 'left' }),
    
    html.Div(id='packet-header-id'),
    ],
    
    # style for main Div                   
    style={'background-color': colour['background'], 'border-style': 'solid', 'border-width': 'medium',
           'border-color': colour['border'], 'font-style': 'bold', 'font-size': '32px', 'color': colour['text'],
           'text-align': 'center'} 
)

# select Avg graph data base on  date 
@app.callback(
    Output('avg-id', 'figure'),
    [Input('date-picker-id', 'date')])
def update_avg(date_value): 
    # select rows for only date chosen
    selected_date = df[df['date']==date_value]
    return {
      'data':[go.Scatter(x = selected_date['date_time'],
                       y = selected_date['avg'],
                       mode='lines')],
      'layout': go.Layout(title = 'average', plot_bgcolor = colour['background'],paper_bgcolor = colour['background'],
                        yaxis = {'color' : colour['text']}, xaxis = {'color': colour['text']}, height = 350)
      }
    
# select packet loss graph data base on  date 
@app.callback(
    Output('packet-id', 'figure'),
    [Input('date-picker-id', 'date')])
def update_packet(date_value): 
    # select rows for only date chosen
    selected_date = df[df['date']==date_value]
    return {
      'data':[go.Scatter(x = selected_date['date_time'],
                       y = selected_date['packet_loss'],
                       mode='lines')],
      'layout': go.Layout(title = 'packet loss', plot_bgcolor = colour['background'],paper_bgcolor = colour['background'],
                        yaxis = {'color' : colour['text']}, xaxis = {'color': colour['text']}, height = 350)
      } 

# click data for average graph
@app.callback(
    dash.dependencies.Output('avg-header-id', 'children'),
    [dash.dependencies.Input('avg-id', 'clickData')])
def hover_data_avg(hoverData):
    time = hoverData['points'][0]['x']
    avg = hoverData['points'][0]['y']
    return 'the average was {} at:  {} '.format(round(avg, 3),time)

# click data for packet loss graph
@app.callback(
    dash.dependencies.Output('packet-header-id', 'children'),
    [dash.dependencies.Input('packet-id', 'clickData')])
def hover_data_packet(hoverData):
    time = hoverData['points'][0]['x']
    packet_loss = hoverData['points'][0]['y']
    return 'the packet loss was {} at:  {} '.format(round(packet_loss,3),time)

# page refresh
@app.callback(
    dash.dependencies.Output('interval-div-id', 'children'),
   [dash.dependencies.Input('interval-id', 'n_intervals')])
def refresh_page(interval):
     return ' refreshed {} times '.format(interval)


# run the dashboard
if __name__ == '__main__':
    app.run_server()










