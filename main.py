from bokeh.embed import file_html
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.tile_providers import get_provider, CARTODBPOSITRON
from flask import Flask, render_template, request, redirect, jsonify, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import os
import numpy as np
import pandas_bokeh
from bokeh.models import *

app = Flask(__name__)
UPLOAD_FOLDER = os.path.abspath('static/document/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
fn = ''


@app.route('/')
@app.route('/home')
def home():
    # Check if there is a dataset in the specified file:
    try:
        df = pd.read_excel(os.path.join(UPLOAD_FOLDER, 'Covid-19_SG.xlsx'))

        graph_size = (1890, 300)

        # Plots the graph using 2 columns for the y-axis, therefore, there will be 2 lines on the line graph
        graph1 = interactive_graph(df, 'line', 'Date', ['Daily Confirmed ', 'Daily Discharged'], 'Date',
                                   'No. of Confirmed Cases',
                                   'Comparison between Daily Confirmed & Daily Discharged COVID-19 Cases in Singapore',
                                   graph_size, 1)

        graph2 = interactive_graph(df, 'line', 'Date', 'Daily Local transmission', 'Date', 'No. of Confirmed Cases',
                                   'Daily Count of Locally Transmitted COVID-19 Cases in Singapore', graph_size, 1)

        graph3 = local_transmission_bar(df, graph_size)

        map = interactive_map()

        return render_template('home.html', title='Home', graph1=graph1, graph2=graph2, graph3=graph3, map=map)
    except FileNotFoundError:
        return render_template('home.html', title='Home')


# Upload feature:
@app.route('/upload', methods=["GET", "POST"])
def upload():
    global fn
    # When the document is uploaded, it will return a POST method.
    # We read the dataset file using Pandas.

    if request.method == 'POST':
        if 'datafile' in request.files:
            file = request.files['datafile']
            fn = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
        else:
            if fn == '':
                pass
            else:
                df = pd.read_excel(os.path.join(UPLOAD_FOLDER, fn))
                html = df.to_html(escape=False)

                # obtain column names and length
                columns = df.columns.values.tolist()
                columns.remove('Date') # remove 'date' as the x-axis will always be a date.
                columns.insert(0, '') # insert blank column as selector
                colLen = len(columns)

                # obtain user-selected column
                ycol = request.form.getlist("pickY1")

                # remove all blank columns in user-selected values
                ycol = [elem for elem in ycol if elem != '']

                # at the first upload, user-selected column will always be empty list
                # use default column in this scenario
                if len(ycol) == 0:
                    ycol = ylabel = columns[1]

                # once user-selected column has values inside, display the string as a list
                else:

                    # check for duplicates in selected values
                    # if there are duplicates, remake ycol as a list without duplicate values
                    if len(ycol) != len(set(ycol)):
                        ycol = list(set(ycol))

                    # we're using set() to remove duplicates.
                    # Note: set() only works if values are hashable, which it should be anyways.
                    ylabel = ', '.join([str(elem) for elem in set(ycol)])

                graph = interactive_plot(df, ycol, ylabel)
                return render_template('upload.html', title='Output Results', content=html,
                                       columns=columns, len=colLen, graph=graph, ycol=ylabel)

    return render_template('upload.html', columns=None, len=None, title='Upload Files')


@app.route('/export', methods=['GET', 'POST'])
def export():
    df = pd.read_excel(os.path.join(UPLOAD_FOLDER, 'Covid-19_SG.xlsx'))
    html = df.to_html(escape=False)
    if request.method == 'POST':
        if request.form.get("export_file"):
            df = pd.read_excel(os.path.join(UPLOAD_FOLDER, 'Covid-19_SG.xlsx'))
            html = df.to_html(escape=False)
            writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            return render_template('export.html', title='Export Files', content=html)
    return render_template('export.html', title='Export Files', content=html)


# Upload.html's graph that will update according to user-selected column
def interactive_plot(frame, ycol, ylabel):

    return frame.plot_bokeh.line(
        x='Date', y=ycol,
        xlabel='Date', ylabel=ylabel, show_figure=False, return_html=True,
        figsize=(1650, 500), toolbar_location=None)


# Function to plot the interactive graph on the landing page using different hard-coded values
def interactive_graph(frame, graphtype, xvariable, yvariable, xtext, ytext, title, size, trange):
    # Put 1 to trange to use the rangetool
    if trange == 1:
        return frame.plot_bokeh(
            kind=graphtype, x=xvariable, y=yvariable, xlabel=xtext, ylabel=ytext, show_figure=False, return_html=True,
            toolbar_location=None, title=title, rangetool=True, figsize=size, zooming=False)
    else:
        return frame.plot_bokeh(
            kind=graphtype, x=xvariable, y=yvariable, xlabel=xtext, ylabel=ytext, show_figure=False, return_html=True,
            toolbar_location=None, title=title, figsize=size, zooming=False)


def local_transmission_bar(frame, size):
    # Sum all local cases based on the month
    total = frame.resample('M', on='Date')['Daily Local transmission'].sum().tolist()

    # Make a new frame that only contains the months and no. of cases per month.
    new_frame = pd.DataFrame(
        {'Month': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September']})
    new_frame['Daily Local Transmission'] = total

    # Use the interactive graph function to create the bar chart.
    return interactive_graph(new_frame, 'bar', 'Month', 'Daily Local Transmission', 'Month', 'No. of Cases',
                             'Locally Transmitted COVID-19 Cases in Singapore per month', size, 0)


def interactive_map():
    # Import the dataset from the specified file
    locationDS = pd.read_pickle('static/document/sgwuhandata.pkl')
    # Convert the dataset into an iterable
    dataset = locationDS['data']
    # Convert the iterable into a Dataframe
    df = pd.DataFrame(dataset)

    # Define lat/long coordinates as tuples
    df['coordinates'] = list(zip(df['lat'], df['lng']))

    # Obtain list of mercator coordinates via x_coord(x, y) function
    mercator = [x_coord(x, y) for x, y in df['coordinates']]

    # Create mercator column in Dataframe
    df['mercator'] = mercator

    # Split the mercator column into mercator_x and mercator_y
    df[['mercator_x', 'mercator_y']] = df['mercator'].apply(pd.Series)

    # Set up bokeh source for plotting in relation to the Dataframe
    source = ColumnDataSource(df)

    # Set up the tooltips that will appear when the user hovers over each plot point
    tooltips = [
        ('Case No:', '@caseNo'),
        ('Linked Case', '@relatedCaseNo'),
        ('Date', '@confirmDate')
    ]

    # Choose the tile
    tile_provider = get_provider(CARTODBPOSITRON)

    # Create the figure
    # The range bounds are supplied in the web mercator coordinates
    plot = figure(title='Map of COVID-19 Cases in Singapore', x_range=(11529747, 11585747),
                  y_range=(148544, 148644), x_axis_type='mercator', y_axis_type='mercator',
                  x_axis_label='Longitude', y_axis_label='Latitude', tooltips=tooltips, width=1890,
                  toolbar_location=None)

    # Add the map tile
    plot.add_tile(tile_provider)

    # Plot the points
    plot.circle(x='mercator_x', y='mercator_y', source=source, size=10, fill_alpha=0.7)

    plot.toolbar.active_scroll = plot.select_one(WheelZoomTool)

    # Return the map as an html string
    return file_html(plot, CDN)


# Function to convert lat/long to mercator coordinates for plotting
def x_coord(x, y):
    lat = x
    lon = y

    r_major = 6378137.000
    x = r_major * np.radians(lon)
    scale = x / lon
    y = 180.0 / np.pi * np.log(np.tan(np.pi / 4.0 +
                                      lat * (np.pi / 180.0) / 2.0)) * scale
    return x, y