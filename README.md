## M5StickCPlus_sensor3_portrait.py

This is a micropython script for M5StickC Plus to measure and show the current 
Temperature and Humidity.
If the device is connected to WiFi, synchronizes its RTC with NTP and also
shows the current time.
Saves the max and min values of Temperature and Humidity since the last boot and
show this in the last 10 seconds of every minute.

## HW Requirements:
- M5StickC Plus
- M5 ENVIII Unit

## SW Requirements
- Micropython
- A "secrets.py" file with the values for your WiFi connection (SSID and Password)
  - SSID_NAME="Put_here_your_SSID"
  - SSID_PASSWD="Put_here_your_WiFi_passkey"

## How it works

**ON START (SETUP):**
Tries to connect to the WiFi and get the current
time from a NTP.
Shows the current measured Temperature and Humidity at the top.
If the connection to WiFi and NTP is ok, show the current time
and "Wifi ok" at the bottom.
else does not show the current time and show "No WiFi" in red.

**IN THE MAIN LOOP:**
For each 60 seconds:
   The first 50 seconcds shows in the LCD of the M5StickC Plus:
     T: current_Temperature
     P: current_Pressure
     H: current_humidity
     current_hour (from rtc)
     current_minute (from rtc)
   in the remaining 10 seconds shows
   the max and min measured Temperature and Humidity from the
   last boot.

 All the measured data is lost when the system is restarted.

## More info:
- https://github.com/m5stack/M5Stack_MicroPython
- https://community.m5stack.com/topic/41/lesson-1-1-lcd-graphics
- https://shop.m5stack.com/products/env-iii-unit-with-temperature-humidity-air-pressure-sensor-sht30-qmp6988
