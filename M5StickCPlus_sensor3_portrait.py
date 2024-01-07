# HW Requirements: M5StickC Plus + ENVIII Unit
# SW Requirements: Micropython
#
# ON START (SETUP):
# Tries to connect to the WiFi and get the current
# time from a NTP.
#   If the connection to WiFi and NTP is ok, show the current time
#      and "Wifi ok" at the bottom.
#   else does not show the current time and show "No WiFi" in red.
# Finally shows the measured Temperature and Humidity at the top.
#
# IN THE MAIN LOOP:
# For each 60 seconds:
#   The first 50 seconcds shows in the LCD of the M5StickC Plus:
#     T: current_Temperature
#     P: current_Pressure
#     H: current_humidity
#     current_hour (from rtc)
#     current_minute (from rtc)
#   in the remaining 10 seconds shows
#   the max and min measured Temperature and Humidity from the
#   last boot.
#
# All the measured data is lost when the system is restarted.
#
# More info:
#    https://github.com/m5stack/M5Stack_MicroPython
#    d
#    https://community.m5stack.com/topic/41/lesson-1-1-lcd-graphics
#    https://shop.m5stack.com/products/env-iii-unit-with-temperature-humidity-air-pressure-sensor-sht30-qmp6988

import m5stack
import time
import machine
import imu
import unit # For the M5Stack UNITs
import ntptime
import network
# secrets.py has the sensitive and not shared data
# Must have SSID_NAME and SSID_PASSWORD variables
import secrets 


# help(m5stack.lcd)
# There are 2 different RTC class
# help(m5stack.rtc)
# help(machine.rtc)
# help(ntptime.client.rtc)
# help(speaker)
# help(axp) Bateria + power
# help(imu) accelerometer
# help(unit) Unitats: SensorIII, PIR, BUZZER, etc

_FONT_SMALL=m5stack.lcd.FONT_DejaVu24
# _FONT_SMALL=m5stack.lcd.FONT_Small
_FONT_MEDIUM=m5stack.lcd.FONT_DejaVu40
# _FONT_MEDIUM=m5stack.lcd.FONT_Arial12
_FONT_BIG=m5stack.lcd.FONT_DejaVu56
# _FONT_BIG=m5stack.lcd.FONT_Arial16
# _FONT=m5stack.lcd.FONT_Default
_X_BEGIN=5
_Y_BEGIN=5
_BRIGHTNESS=60
_NTP_POOL='es.pool.ntp.org'
_TIMEZONE=1 # Europe/Madrid
_SSID=secrets.SSID_NAME
_PASSWD=secrets.SSID_PASSWD

_sync_color = m5stack.lcd.GREEN # GREEN=NTP synchronized. RED=not Syncrhonized
_connected = False

# Where to save the max and min Temperature, Humidity, ... of the last 24h
_data={"t":{"max":{"hour":99, "value":-99}, "min":{"hour":99, "value":99}},
       "h":{"max":{"hour":99, "value":-99}, "min":{"hour":99, "value":99}}
      }
# Init the ENVIII Sensor
env3_0 = unit.get(unit.ENV3, unit.PORTA)


# The initialization must do on power on.
def setup():
    global _connected
    setup_lcd()
    do_connect(_SSID,_PASSWD)
    if _connected:
        set_rtc_from_ntp(_NTP_POOL, _TIMEZONE)
    # Do not need more the network. Disable to save power.   
    # wlan.active(False)


# Function to connect to the AP
def do_connect(ssid, password):
    global _sync_color
    global _connected
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        msg = 'connecting to SSID {}'.format(ssid)
        print(msg)
        wlan.connect(ssid, password)
        timeout = 10  # 10 tries
        while (not wlan.isconnected()) and (timeout>0):
            time.sleep(1)
            timeout -= 1
            msg += '.'
            print(msg)
    if wlan.isconnected():
        _sync_color = m5stack.lcd.GREEN
        print('network config:', wlan.ifconfig())
    else:
        _sync_color = m5stack.lcd.RED
        print("NOT connected!")
    _connected = wlan.isconnected()


# Function to set the RTC from NTP
def set_rtc_from_ntp(ntp_server, timezone):
    try:
        # Get and update the RTC time from NTP server
        ntp_client = ntptime.client(host=ntp_server, timezone=timezone)
        m5stack.rtc.setTime(ntp_client.year(),ntp_client.month(),ntp_client.day(),ntp_client.hour(),ntp_client.minute(),ntp_client.second())
        print(m5stack.rtc.now())
        # Next sentences are not needed
        # update the time
        # ntp_client.updateTime()
        return True
    except OSError:
        return False


# Setup LCD properties
def setup_lcd():
    m5stack.lcd.clear()
    axp.setLcdBrightness(_BRIGHTNESS) # Save some power
    m5stack.lcd.setRotation(m5stack.lcd.PORTRAIT)  # Adjust rotation if needed
    # m5stack.lcd.font(font [,rotate, transparent, fixedwidth, dist, width, outline, color])
    # m5stack.lcd.font(font=m5stack.lcd.FONT_Ubuntu, rotate=90, width=100, transparent=True, color=m5stack.lcd.GREEN)
    m5stack.lcd.font(font=_FONT_MEDIUM)
    m5stack.lcd.setCursor(_X_BEGIN, _Y_BEGIN)


# Return the measured Temperature, Presure and Humidity
def read_TPH():
    return env3_0.temperature, env3_0.pressure, env3_0.humidity


# Udate the min and max registered values
def update_data(t,p,h):
    global _data
    if _data["t"]["max"]["value"]<t:
        _data["t"]["max"]["value"]=t
        _data["t"]["max"]["hour"]=m5stack.rtc.now()[3]
    if _data["t"]["min"]["value"]>t:
        _data["t"]["min"]["value"]=t
        _data["t"]["min"]["hour"]=m5stack.rtc.now()[3]
    if _data["h"]["max"]["value"]<h:
        _data["h"]["max"]["value"]=h
        _data["h"]["max"]["hour"]=m5stack.rtc.now()[3]
    if _data["h"]["min"]["value"]>h:
        _data["h"]["min"]["value"]=h
        _data["h"]["min"]["hour"]=m5stack.rtc.now()[3]

    
# Display the measured Temperature and Humidity
def display_TPH():
    m5stack.lcd.font(_FONT_MEDIUM)
    x_offset, y_offset=m5stack.lcd.fontSize()
    t,p,h = read_TPH()
    update_data(t=t,p=p,h=h)
    m5stack.lcd.setTextColor(m5stack.lcd.RED, m5stack.lcd.BLACK)
    text_T = "T {:.1f}".format(t)
    # m5stack.lcd.textClear(x,y,text=text_T)
    m5stack.lcd.println(text_T)

    # Do not want to show the pressure
    # m5stack.lcd.setTextColor(m5stack.lcd.YELLOW, m5stack.lcd.BLACK)
    # text_P = "P: {:.1f}".format(p)
    # m5stack.lcd.textClear(x,y,text=text_P)
    # m5stack.lcd.println(text_P)
    
    m5stack.lcd.setTextColor(m5stack.lcd.ORANGE, m5stack.lcd.BLACK)
    text_H = "H {:.1f}".format(h)
    # m5stack.lcd.textClear(x,y,text=text_H)
    m5stack.lcd.println(text_H)
      

# Display the current time from the internal RTC
def display_time():
    m5stack.lcd.font(_FONT_BIG)
    year, month, day, hour, minute, seconds = m5stack.rtc.now()

    m5stack.lcd.setTextColor(_sync_color, m5stack.lcd.BLACK)
    m5stack.lcd.setCursor(m5stack.lcd.CENTER,m5stack.lcd.text_y())
    text_hour = "{:02d}".format(hour)
    m5stack.lcd.println(text_hour)

    m5stack.lcd.setTextColor(m5stack.lcd.YELLOW, m5stack.lcd.BLACK)
    text_minute = "{:02d}".format(minute)
    m5stack.lcd.setCursor(m5stack.lcd.CENTER,m5stack.lcd.text_y())
    m5stack.lcd.println(text_minute)
    

# Display the main info:
# - current Temperature and humidity
# - the time from the RTC. 
def display_info():
    display_TPH()
    x_offset, y_offset=m5stack.lcd.fontSize()    
    if _connected:
        display_time()
        m5stack.lcd.font(_FONT_SMALL)
        m5stack.lcd.setCursor(0, m5stack.lcd.BOTTOM)
        m5stack.lcd.setTextColor(_sync_color, m5stack.lcd.BLACK)
        m5stack.lcd.println("WiFi OK",x=m5stack.lcd.CENTER)
    else:
        m5stack.lcd.font(_FONT_BIG)
        m5stack.lcd.setCursor(0, m5stack.lcd.text_y()+10)
        m5stack.lcd.setTextColor(_sync_color, m5stack.lcd.BLACK)
        m5stack.lcd.println("NO WiFi",y=m5stack.lcd.BOTTOM)


# Display the max and min measured Temperature and humidity
# sice the last boot.
def display_data():
    setup_lcd()
    m5stack.lcd.font(_FONT_SMALL)
    m5stack.lcd.setTextColor(m5stack.lcd.RED, m5stack.lcd.BLACK)
    max_t =  _data["t"]["max"]["value"]
    hour =  _data["t"]["max"]["hour"]
    text_T = "T {:.1f} {:02d}".format(max_t,hour)
    m5stack.lcd.println(text_T)
    m5stack.lcd.println("")
    
    m5stack.lcd.setTextColor(m5stack.lcd.GREEN, m5stack.lcd.BLACK)
    min_t =  _data["t"]["min"]["value"]
    hour =  _data["t"]["min"]["hour"]
    text_T = "T {:.1f} {:02d}".format(min_t,hour)
    m5stack.lcd.println(text_T)
    m5stack.lcd.println("")    

    m5stack.lcd.setTextColor(m5stack.lcd.WHITE, m5stack.lcd.BLACK)
    text_V = "BAT {:.1f} v".format(axp.getBatVoltage())
    m5stack.lcd.println(text_V)
    m5stack.lcd.println("")
    
    m5stack.lcd.setTextColor(m5stack.lcd.ORANGE, m5stack.lcd.BLACK)
    max_h =  _data["h"]["max"]["value"]
    hour =  _data["h"]["max"]["hour"]
    text_H = "H {:.1f} {:02d}".format(max_h,hour)
    m5stack.lcd.println(text_H)
    m5stack.lcd.println("")
    
    m5stack.lcd.setTextColor(m5stack.lcd.GREEN, m5stack.lcd.BLACK)
    min_h =  _data["h"]["min"]["value"]
    hour =  _data["h"]["min"]["hour"]
    text_H = "H {:.1f} {:02d}".format(min_h,hour)
    m5stack.lcd.println(text_H)


setup()
# Alternate display current data
# and max/min values
while True:
    setup_lcd() # Prepare the LCD and try to connect to WiFi and synchronize from NTP.
    display_info() # Show current Temperature, Humidity and time.
    machine.lightsleep(50 * 1000) # light sleep for 50 seconds
    display_data() # Display max and min values since last boot.
    machine.lightsleep(10 * 1000) # light sleep for 10 seconds

