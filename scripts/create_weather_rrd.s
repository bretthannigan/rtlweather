#!/bin/bash
# One sample per 5 minutes (900 s).
# Store 105,120 samples (1 year) of data.
# Compute min, average, max over last 12 samples (1 hour)
# Store 87,600 samples of these data (10 years).
rrdtool create weather.rrd --step 900 \
DS:temperature:GAUGE:1200:-40:50 \
DS:humidity:GAUGE:1200:0:100 \
DS:wind_speed:GAUGE:1200:0:30 \
DS:wind_gust:GAUGE:1200:0:30 \
DS:rainfall:DCOUNTER:1200:0:100 \
RRA:AVERAGE:0.5:1:105120 \
RRA:MIN:0.5:12:87600 \
RRA:MAX:0.5:12:387600 \
RRA:AVERAGE:0.5:12:87600