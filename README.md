# rtlweather
A set of Python scripts and a simple database to post weather station measurements to the web. Weather station is located [here](https://tools.wmflabs.org/geohack/geohack.php?params=49_18_31.9_N_122_50_52.6_W).
Data are collected using a SDR dongle on the LPD433 band and the webpage is hosted on a Raspberry Pi.

## Dependencies
* Python 3
* [rtl_433](https://github.com/merbanan/rtl_433) - Decoder for many 433 MHz devices and more.
* [rrdtool](https://oss.oetiker.ch/rrdtool/) - Lightweight round-robin database.
