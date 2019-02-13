rrdtool create weather.rrd --step 300 \
DS:temperature:GAUGE:1200:-40:50 \
DS:humidity:GAUGE:1200:0:100 \
DS:wind_speed:GAUGE:1200:0:30 \
DS:wind_gust:GAUGE:1200:0:30 \
DS:wind_direction:GAUGE:1200:0:359 \
DS:rainfall:DCOUNTER:0:10 \
RRA:AVERAGE:0.5:1:105120 \
RRA:MIN:0.5:12:87600 \
RRA:MAX:0.5:12:87600 \
RRA:AVERAGE:0.5:12:87600