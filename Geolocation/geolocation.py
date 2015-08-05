import re
import csv
import json
import urllib2
import string
from time import sleep
from geolocation_reference import get_full_name
from geolocation_reference import get_abbreviation
import random
import sys
import getopt
import gspread

URL = 'https://maps.googleapis.com/maps/api/geocode/json?address=' 
API_KEY = 'AIzaSyAW3GX8hrAuoET8ESMA8rB8Y7AXqTHMH6I'

# ----------- Location record(City, State, Country) --------------------
def send_request_by_record(record):
	address = record[0] + ',+' + record[1] + ',+' + record[2]
	address = address.replace(" ", "+")
	url = URL + address + '&key=' + API_KEY
	response = urllib2.urlopen(url)
	jsongeocode = response.read()
	geo = parse_json(jsongeocode)
	# Output data in <City, State, Country, latitude, longitude> order
	record.append(geo[0])
	record.append(geo[1])
	print record

# ------------ Location data(City, State, Country) ----------------
def send_request_by_location(city, state, country) :
	address = country
	state_full_name = ''
	if state and len(state) == 2:
		address = state + ',+' + address
		state_full_name = get_full_name(state)
	elif state and len(state) > 2:
		address = state + ',+' + address
		state_full_name = state
		state = get_abbreviation(state)
	if city :
		address = city + ',+' + address
	address = address.replace(' ', '+')
	url = URL + address + '&key=' + API_KEY
	response = urllib2.urlopen(url)
	jsongeocode = response.read()
	geo = parse_json(jsongeocode)
	return [city, state_full_name, state, country, geo[0], geo[1]]


# ---------- JSON result from Google Geocoding -------------
def parse_json(code) :
	response = json.loads(code)
	if response['status'] == 'OK' :
		geo = response['results'][0]['geometry']['location']
		return [geo['lat'], geo['lng']]
	else :   
		# print response['status']
		return ['0', '0']


if __name__ == "__main__":
	# main(sys.argv[1:])
	print ''


# ---------------------- Useful File ------------------------

SQL = '''
	SELECT ID, City, State, Abbreviation, Country, Latitude, Longitude
	INTO OUTFILE '/var/tmp/locations.csv'
	FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
	LINES TERMINATED BY '\n'
	FROM zd_new_location
	WHERE ID <> 149 AND (Latitude = 0 OR Longitude = 0)
	ORDER BY City;
	'''

# def main(argv):
# 	input_file = ''
# 	output_file = ''
# 	try:
# 		opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
# 	except getopt.GetoptError:
# 		print 'test.py -i <inputfile> -o <outputfile>'
#      	sys.exit(2)
#    	for opt, arg in opts:
#    		if opt == '-h':
#    			print 'test.py -i <inputfile> -o <outputfile>'
#    			sys.exit()
#    		elif opt in ("-i", "--ifile"):
#    			input_file = arg
#    		elif opt in ("-o", "--ofile"):
#    			output_file = arg
#    	print 'Input file is "', input_file
#    	print 'Output file is "', output_file

#    	data = read_file(input_file)
# 	for item in result :
# 		item = send_request_by_record(item)
# 		print item
# 		# sleep(random.uniform(1.6, 3.6))
# 	write_file(output_file, data)