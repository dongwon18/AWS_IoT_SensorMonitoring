# import library for DHT22 sensor
import Adafruit_DHT

# define sensor type and GPIO pin
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4 # GPIO4
POS = "TH01"

# get data from sensor
t, h = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
# if reading value failed
if(h == None or t == None):
    print("Reading failed")
else:
    print("{}C {}%".format(h, t))
