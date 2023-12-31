# HW Requirements: M5StickC Plus + ENVIII Unit
# SW Requirements: Micropython
#
# For each 60 seconds:
#   Shows on LCD of the M5StickC Plus
#     T: current_Temperature
#     P: current_Pressure
#     H: current_humidity
#     current_hour (from rtc)
#     current_minute (from rtc)
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
#Per emprar UNITS
import unit
import ntptime
import network


#help(m5stack.lcd)
#There are 2 different RTC class
#help(m5stack.rtc)
#help(machine.rtc)
#help(ntptime.client.rtc)
#help(speaker)
#help(axp) Bateria + power
#help(imu) accelerometer
#help(unit) Unitats: SensorIII, PIR, BUZZER, etc

_FONT_SMALL=m5stack.lcd.FONT_DejaVu24
#_FONT_SMALL=m5stack.lcd.FONT_Small
_FONT_MEDIUM=m5stack.lcd.FONT_DejaVu40
#_FONT_MEDIUM=m5stack.lcd.FONT_Arial12
_FONT_BIG=m5stack.lcd.FONT_DejaVu56
#_FONT_BIG=m5stack.lcd.FONT_Arial16
#_FONT=m5stack.lcd.FONT_Default
_X_BEGIN=5
_Y_BEGIN=5
_BRIGHTNESS=80
_NTP_POOL='es.pool.ntp.org'
_TIMEZONE=1
_SSID="My_SSID"
_PASSWD="My_WiFi_password"

_sync_color = m5stack.lcd.GREEN #GREEN=NTP synchronized. RED=not Syncrhonized
_connected = False

# Function to connect to the AP
def do_connect(ssid, password):
    global _sync_color
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        msg = 'connecting to SSID {}'.format(_SSID)
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
    return wlan.isconnected()


# Function to set the RTC from NTP
def set_rtc_from_ntp():
    try:
        #Get and update the RTC time from NTP server
        ntp_client = ntptime.client(host=_NTP_POOL, timezone=(_TIMEZONE))
        m5stack.rtc.setTime(ntp_client.year(),ntp_client.month(),ntp_client.day(),ntp_client.hour(),ntp_client.minute(),ntp_client.second())
        print(m5stack.rtc.now())
        #Next sentences are not needed
        #update the time
        #ntp_client.updateTime()
        return True
    except OSError:
        return False


# Return the measured Temperature, Presure and Humidity
def read_TPH():
    env3_0 = unit.get(unit.ENV3, unit.PORTA)
    return env3_0.temperature, env3_0.pressure, env3_0.humidity


# Setup LCD properties
def setup_lcd():
    m5stack.lcd.clear()
    axp.setLcdBrightness(_BRIGHTNESS) # Save some power
    m5stack.lcd.setRotation(m5stack.lcd.PORTRAIT)  # Adjust rotation if needed
    #m5stack.lcd.font(font [,rotate, transparent, fixedwidth, dist, width, outline, color])
    #m5stack.lcd.font(font=m5stack.lcd.FONT_Ubuntu, rotate=90, width=100, transparent=True, color=m5stack.lcd.GREEN)
    m5stack.lcd.font(font=_FONT_MEDIUM)
    m5stack.lcd.setCursor(_X_BEGIN, _Y_BEGIN)


def setup():
    global _connected
    setup_lcd()
    _connected = do_connect(_SSID,_PASSWD)

    
# Display the measured Temperature, Presure and Humidity
# At the bottom
def display_TPH_old(x:int, y:int):
    m5stack.lcd.font(_FONT_MEDIUM)
    x_offset, y_offset=m5stack.lcd.fontSize()
    m5stack.lcd.setCursor(x, y)
    t,p,h = read_TPH()
    
    m5stack.lcd.setTextColor(m5stack.lcd.RED, m5stack.lcd.BLACK)
    text_T = "T {:.1f}".format(t)
    m5stack.lcd.textClear(x,y,text=text_T)
    m5stack.lcd.println(text_T)

    #Do not want to show the pressure
    #m5stack.lcd.setTextColor(m5stack.lcd.YELLOW, m5stack.lcd.BLACK)
    #text_P = "P: {:.1f}".format(p)
    #m5stack.lcd.println(text_P)
    
    m5stack.lcd.setTextColor(m5stack.lcd.ORANGE, m5stack.lcd.BLACK)
    text_H = "H {:.1f}".format(h)
    m5stack.lcd.println(text_H)
    

# Display the measured Temperature, Presure and Humidity
# At the bottom
def display_TPH():
    m5stack.lcd.font(_FONT_MEDIUM)
    x_offset, y_offset=m5stack.lcd.fontSize()
    t,p,h = read_TPH()
    
    m5stack.lcd.setTextColor(m5stack.lcd.RED, m5stack.lcd.BLACK)
    text_T = "T {:.1f}".format(t)
    #m5stack.lcd.textClear(x,y,text=text_T)
    m5stack.lcd.println(text_T)

    #Do not want to show the pressure
    #m5stack.lcd.setTextColor(m5stack.lcd.YELLOW, m5stack.lcd.BLACK)
    #text_P = "P: {:.1f}".format(p)
    #m5stack.lcd.textClear(x,y,text=text_P)
    #m5stack.lcd.println(text_P)
    
    m5stack.lcd.setTextColor(m5stack.lcd.ORANGE, m5stack.lcd.BLACK)
    text_H = "H {:.1f}".format(h)
    #m5stack.lcd.textClear(x,y,text=text_H)
    m5stack.lcd.println(text_H)
    
    

# Display the measured Temperature, Presure and Humidity
# At the bottom
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
    


# Display Temperature, Pressure and humidity
# Current Hour and Minute if it is NTP syncrhonized
def display_info():
    display_TPH()
    x_offset, y_offset=m5stack.lcd.fontSize()    
    if _connected:
        #Jump the 3 Lines of TPH (y_offset*3)
        ##display_time(x=x_offset, y=y_offset*2+_Y_BEGIN)
        # m5stack.lcd.text_y() gives the next line
        display_time()
        m5stack.lcd.font(_FONT_SMALL)
        m5stack.lcd.setCursor(0, m5stack.lcd.BOTTOM)
        m5stack.lcd.setTextColor(_sync_color, m5stack.lcd.BLACK)
        m5stack.lcd.println("WiFi OK",x=m5stack.lcd.CENTER)
    else:
        m5stack.lcd.font(_FONT_BIG)
        #x_offset, y_offset=m5stack.lcd.fontSize()
        m5stack.lcd.setCursor(0, m5stack.lcd.text_y()+10)
        m5stack.lcd.setTextColor(_sync_color, m5stack.lcd.BLACK)
        m5stack.lcd.println("NO WiFi",y=m5stack.lcd.BOTTOM)

setup()
while True:
    setup_lcd()
    display_info()
    time.sleep(60)
