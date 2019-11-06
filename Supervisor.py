
#####
# This is a custom 'getting started' script, made with care for theodore.xavier221@gmail.com.
# If you have any questions, please email us! support@initialstate.com
#####

from __future__ import division
from subprocess import PIPE, Popen
# Import the ISStreamer module
from ISStreamer.Streamer import Streamer
# Import time for delays
import time
# Import light and weather sensors
from envirophat import light
from envirophat import weather

# Defined Access Keys
ACCESS_KEY  = "ist_vg7IMJ1kf0T-YjoSjdZG-1Do8VA3tj6i"
BUCKET_KEY  = "python_example"
BUCKET_NAME = "FireDash"

SAMPLE_RATE = 10

# Streamer constructor, this will create a bucket called Python Stream Example
# you'll be able to see this name in your list of logs on initialstate.com
# your access_key is a secret and is specific to you, don't share it!

# returns cpu temperature 
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")]) 

def calculate_risk(temp_value, pressure_value, light_value):	

	light_risk = 0
	temp_risk = 0

	if light_value < 2000 and light_value > 0:
		light_risk = 1

	if light_value > 2200 and light_value < 4000:
		light_risk = 2

	if light_value > 5000 and light_value < 6000:
		light_risk = 3

	if light_value > 6000:
		light_risk = 4


	if temp_value < 30 and temp_value > 0:
		temp_risk = 1

	if temp_value < 60 and temp_value > 32:
		temp_risk = 2

	if temp_value < 100 and temp_value > 62:
		temp_risk = 3

	if temp_value > 100:
		temp_risk = 4

	fire_risk = (temp_risk + light_risk) / 2
	return round(fire_risk)

def main():

	streamer = Streamer(bucket_name="FireDash", bucket_key="python_example", access_key="ist_vg7IMJ1kf0T-YjoSjdZG-1Do8VA3tj6i")
	
	#Sending Startup Values to dashboard
	streamer.log("Status", "Online")
	streamer.log("Temperature", 0)
	streamer.log("Pressure", 0)
	streamer.log("Light", 0)
	streamer.log("FireLevel", 1)
	streamer.log("FireDetected", "Low")

	count = 0
	temp_sum = 0
	pressure_sum = 0
	light_sum = 0

	risk_rating = { 
		1: "Low", 
		2: "Moderate", 
		3: "High",
		4: "Critical", 
	}

	print("Stream Started")

	while True:
		print("Streaming")
		time.sleep(0.1) 

		count = count + 1

		#temperature sensor affected by surrounding residual heat
		#subtracting raw value from cpu temperature to get accurate results
		cpu_temp = get_cpu_temperature()
		raw_temp = weather.temperature()
		temp_fixed = raw_temp - ((cpu_temp-raw_temp)/1.3)

		#temperature, light and pressure as totaled for smoothing
		temp_sum = temp_sum + temp_fixed
		light_sum = light_sum + light.light()
		pressure_sum = pressure_sum + weather.pressure(unit = 'hPa') 

		#once allocated samples are taken, the value is averaged to get a more accurate reading
		if count == SAMPLE_RATE:
			
			temp_value = temp_sum/SAMPLE_RATE
			pressure_value = pressure_sum/SAMPLE_RATE
			light_value = light_sum/SAMPLE_RATE

			#smoothed data is sent to dash board for processing
			streamer.log("Temperature", round(temp_value,2))
			streamer.log("Pressure", round(pressure_value,2))
			streamer.log("Light", round(light_value,2))



			#calculates the risk of a fire present based on recieved data
			risk_level = calculate_risk(temp_value, pressure_value, light_value)
			streamer.log("FireLevel", risk_level)
			streamer.log("FireDetected", risk_rating.get(risk_level))

			streamer.flush()
			count = 0
			temp_sum = 0
			light_sum = 0
			pressure_sum = 0

	streamer.close()


#might need this depending on what version python is running on pi
#if __name__ == __main__:
main()