#!/usr/local/bin/rrdcgi
<html>
<head>
<title>Anmore, BC Weather Station Data</title>
</head>
<body>
<h1>Weather Station</h1>
<h2>About the Station</h2>
<hr>
<h2>Weather Data</h2>

<script type="text/javascript">
	params = new URLSearchParams(location.search);
	if(params.has("RRD_SPAN") == false) {
		window.location.href="test.cgi?RRD_SPAN=-1d";
		window.loaction.reload();
	}
</script>

<form name=dateRange>
	Time scale:<br>
	<input name=RRD_SPAN type=radio value="-1d" id="day"> Day
    <input name=RRD_SPAN type=radio value="-1w" id="week"> Week
    <input name=RRD_SPAN type=radio value="-1m" id="month"> Month
    <input name=RRD_SPAN type=radio value="-1y" id="year"> Year
    <input name=RRD_SPAN type=radio value="20200101" id="all"> All
    <input type=submit>
</form>

<script type="text/javascript">
	if(params.get("RRD_SPAN") == "-1d") {
		document.forms["dateRange"]["day"].checked=true;
	}
	if(params.get("RRD_SPAN") == "-1w") {
		document.forms["dateRange"]["week"].checked=true;
	}
	if(params.get("RRD_SPAN") == "-1m") {
		document.forms["dateRange"]["month"].checked=true;
	}
	if(params.get("RRD_SPAN") == "-1y") {
		document.forms["dateRange"]["year"].checked=true;
	}
	if(params.get("RRD_SPAN") == "20200101") {
		document.forms["dateRange"]["all"].checked=true;
	}
</script>

<p>

<RRD::GOODFOR -300>

<RRD::GRAPH ../temperature.png 
			--imginfo '<img src=../%s width=%lu height=%lu>' 
			--width 600 
			--start <RRD::CV RRD_SPAN> 
			--end now 
			--title "Temperature & Humidity" 
			--right-axis 1:0
			DEF:temperature=./weather.rrd:temperature_C:AVERAGE 
			DEF:humidity=./weather.rrd:humidity:AVERAGE
			LINE1:temperature#ffa000:"Temperature (C)"
			LINE1:humidity#00aa00:"Humidity (%)">
<br><br>
<RRD::GRAPH ../wind.png 
			--imginfo '<img src=../%s width=%lu height=%lu>' 
			--width 600 
			--start <RRD::CV RRD_SPAN> 
			--end now 
			--title Wind 
			DEF:speed=./weather.rrd:wind_speed:AVERAGE 
			DEF:gust=./weather.rrd:wind_gust:LAST 
			DEF:direction=./weather.rrd:wind_direction:AVERAGE
			LINE1:speed#ffa000:"Wind speed (m/s)" 
			LINE1:gust#00aa00:"Gust speed (m/s)"
			LINE1:direction#00aaff:"Direction">
<br><br>
<RRD::GRAPH ../rainfall.png 
			--imginfo '<img src=../%s width=%lu height=%lu>' 
			--width 600 
			--start <RRD::CV RRD_SPAN> 
			--end now 
			--title Rainfall 
			DEF:rainfall=./weather.rrd:rain_total:LAST 
			LINE1:rainfall#ffa000:"Rainfall (mm)">

</p>
<hr>
Last measurement: <RRD::TIME::LAST weather.rrd "%Y-%m-%d %H:%M:%S">
</body>
</html>
