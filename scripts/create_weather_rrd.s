#!/bin/bash
# Create rrd database for weather measurement
# One average value for each quarter hour (900 s) of 2 * 8 + 5 sensors 
# Average 1: 960 samples == 10 days
# Average/Min/Max 2: 1 sample per day for 3600 days 
rrdtool create weather.rrd --step 900 \
DS:temps1:GAUGE:1200:-40:50 \
DS:temps2:GAUGE:1200:-40:50 \
DS:temps3:GAUGE:1200:-40:50 \
DS:temps4:GAUGE:1200:-40:50 \
DS:temps5:GAUGE:1200:-40:50 \
DS:temps6:GAUGE:1200:-40:50 \
DS:temps7:GAUGE:1200:-40:50 \
DS:temps8:GAUGE:1200:-40:50 \
DS:hums1:GAUGE:1200:0:100 \
DS:hums2:GAUGE:1200:0:100 \
DS:hums3:GAUGE:1200:0:100 \
DS:hums4:GAUGE:1200:0:100 \
DS:hums5:GAUGE:1200:0:100 \
DS:hums6:GAUGE:1200:0:100 \
DS:hums7:GAUGE:1200:0:100 \
DS:hums8:GAUGE:1200:0:100 \
DS:temps9:GAUGE:1200:-40:50 \
DS:hums9:GAUGE:1200:0:100 \
DS:winds9:GAUGE:1200:0:200 \
DS:rains9:DERIVE:1200:0:0.027 \
DS:israins9:GAUGE:1200:0:1 \
RRA:AVERAGE:0.5:1:960 \
RRA:MIN:0.5:96:3600 \
RRA:MAX:0.5:96:3600 \
RRA:AVERAGE:0.5:96:3600
