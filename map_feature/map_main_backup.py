from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.palettes import PRGn, RdYlGn
from bokeh.io import output_notebook



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

output_file("test.html")

# Import dataset
database = pd.read_pickle('sgwuhandata.pkl')

"""Format dataset to DataFrame"""
# Define dataset in arrays; data is key
dataset = database['data']
# Convert dataset into DataFrame format
df = pd.DataFrame(dataset)

"""Set html output"""
output_file("tile.html")


"""Function to convert lat/long to mercator coordinates for plotting on p"""
def x_coord(x, y):
    lat = x
    lon = y
    
    r_major = 6378137.000
    x = r_major * np.radians(lon)
    scale = x/lon
    y = 180.0/np.pi * np.log(np.tan(np.pi/4.0 + 
        lat * (np.pi/180.0)/2.0)) * scale
    return (x, y)

"""Prepping DataFrame file for mercators coordinates"""
# Define lat/lon coord as tuple (lat,long)
df['coordinates'] = list(zip(df['lat'], df['lng']))

# Obtain list of mercator coordinates via x_coord(x, y)
mercators = [x_coord(x, y) for x, y in df['coordinates']]

# Create mercator column in DataFrame
df['mercator'] = mercators

# Split mercator column into mercator_x and mercator_y
df[['mercator_x', 'mercator_y']] = df['mercator'].apply(pd.Series)


"""Prepping the Plot"""
# Choose palette
palette = PRGn[11]

# Set up bokeh source for plotting in relation to DataFrame
source = ColumnDataSource(df)

# Set up tooltips for user hovers over a data point
tooltips = [("Case No:", "@caseNo"), ("Linked Case", "@relatedCaseNo"), 
            ("Date", "@confirmDate")]


"""Creating Map figure"""
# Choosing tile
tile_provider = get_provider(CARTODBPOSITRON)

# Creating Figure
# range bounds supplied in web mercator coordinates
p = figure(title = 'Singapore Covid-19', width = 900, height = 550, 
           x_range = (11529747, 11585747), y_range = (148544, 148644),
           x_axis_type = "mercator", y_axis_type = "mercator", 
           x_axis_label = "Longtitude", y_axis_label = "Latitude", 
           tooltips = tooltips)

#Add map tile
p.add_tile(tile_provider)

"""Plotting Time"""
# Plot the points
p.circle (x = "mercator_x", y = "mercator_y", source = source, 
          size = 10, fill_alpha = 0.7)
# p.circle(x="lng", y="lat", size=5, fill_color="blue", fill_alpha=0.8, 
#          source=source)

show(p)

