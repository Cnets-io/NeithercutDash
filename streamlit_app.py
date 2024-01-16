from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models import PointDrawTool, ColumnDataSource, CustomJS, Div, Row, MultiChoice
from bokeh.plotting import figure, show
from bokeh.io import show

import pandas as pd
import streamlit as st
from influxdb_client import InfluxDBClient, Point




# Instantiate an InfluxDB client configured for a bucket
#@st.cache_resource
def getDataFrame():
    client = InfluxDBClient(
    "http://141.148.21.97:8086",
    database="neithercut",
    token=st.secrets['INFLUXDB_KEY'],
    org='cnets')
    query_api = client.query_api()

    # Execute the query to retrieve all record batches in the stream
    # formatted as a PyArrow Table.

    table = query_api.query_data_frame('from(bucket:"neithercut") |> range(start: -30d)')
    client.close()

    # Convert the PyArrow Table to a pandas DataFrame.
    dataframe = table
    dataframe['local_time'] = dataframe['time'].dt.tz_localize('utc').dt.tz_convert('America/Detroit')
    dataframe['local_time'] = dataframe['local_time'].dt.tz_localize(None)
    dataframe['avg_temperature'] = (dataframe.object_air_temperature_value + dataframe.object_barometer_temperature_value + dataframe.object_co2_sensor_temperature_value) / 3
    return dataframe


dataframe = getDataFrame()
dfInside = dataframe[dataframe.object_device_id == 1541]
dfOutside = dataframe[dataframe.object_device_id == 1542]


st.write("# Neithercut 30-Day Data Window")

option = st.selectbox(
    'Please select data from the following drop-down list (defaults to temperature).',
    ('Barometric Pressure', 'Temperature ', 'Air Humidity', 'C02 Concentration'),
    index=1)


# prepare some data
xi = dfInside['local_time']
xo = dfOutside['local_time']
ylabel = 'Value'

if (option == 'Barometric Pressure'):
    yi = dfInside.object_barometric_pressure_value * 0.0002952998057228486
    yo = dfOutside.object_barometric_pressure_value * 0.0002952998057228486
    ylabel = 'Inches of mercury [inHG]'
elif (option == 'Temperature '):
    yi = dfInside.avg_temperature
    yo = dfOutside.avg_temperature
    ylabel = "3 sensor average [°C]"
elif (option == 'Air Humidity'):
    yi = dfInside.object_air_humidity_value
    yo = dfOutside.object_air_humidity_value
    ylabel = 'Relative [%]'
elif (option == 'C02 Concentration'):
    yi = dfInside.object_co2_concentration_lpf_value
    yo = dfOutside.object_co2_concentration_lpf_value
    ylabel = 'Low-pass filtered [ppm]'
else:
    yi = dfInside.avg_temperature
    yo = dfOutside.avg_temperature
    ylabel = "3 sensor average [°C]"


# create a new plot with a title and axis labels
p = figure(title=option, x_axis_label="Date and time", y_axis_label=ylabel, x_axis_type='datetime')

# add a line renderer with legend and line thickness
p.line(xo, yo, legend_label="Outside", line_width=2,line_color='gold')
#p.varea(xo, yo, alpha=0.2, fill_color='gold')

p.line(xi, yi, legend_label="Inside", line_width=2, line_color='maroon')
url = "http://cnets.group/media/cnets-logo.png"
d1 = Div(text = '<div style="position: absolute; left:-666px; top:444px"><img src=' + url + ' style="width:96px; height:96px; opacity: 0.3"></div>')

p1 = (Row(p,d1))

st.bokeh_chart(p1, use_container_width=True)
st.write('''<span style="font-size:0.9em; text-align: center;">Made by PS + :coffee: from [Cnets.group](https://cnets.group) for the [College of Science and Engineering](https://www.cmich.edu/cse) at [Central Michgian University](https://www.cmich.edu).<span>''', unsafe_allow_html=True)
