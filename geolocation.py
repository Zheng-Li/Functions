import re
import csv
import json
import urllib2
import string
from time import sleep
from location_reference import get_full_name
import random
import sys
import getopt
import gspread

URL = 'https://maps.googleapis.com/maps/api/geocode/json?address=' 
API_KEY = "AIzaSyAW3GX8hrAuoET8ESMA8rB8Y7AXqTHMH6I"

def read_file(file_name):
	f = csv.reader(open(file_name, 'rU'))
	raw_data = []
	for row in f : 		
		# Input data in <City, State, Country> order
		raw_data.append([row[0], row[1], row[2]])
	return raw_data

def write_file(file_name, data):
	f = csv.writer(open(file_name, 'wb', buffering=0))
	for x in data :
		f.writerow(x)

def send_request_by_record(record):
	# Input data in <City, State, Country> order
	address = record[0] + ',+' + record[1] + ',+' + record[2]
	address = address.replace(" ", "+")
	url = URL + address + '&key=' + API_KEY
	print url
	response = urllib2.urlopen(url)
	jsongeocode = response.read()
	geo = parse_json(jsongeocode)
	# Output data in <City, State, Country, latitude, longitude> order
	record.append(geo[0])
	record.append(geo[1])
	print record

def send_request_by_location(city, state, country) :
	address = country
	state_full_name = ''
	if state and len(state) == 2:
		address = state + ',+' + address
		state_full_name = get_full_name(state)
	elif state and len(state) > 2:
		address = state + ',+' + address
		state_full_name = state
		state = ''
	if city :
		address = city + ',+' + address
	address = address.replace(' ', '+')
	url = URL + address + '&key=' + API_KEY
	response = urllib2.urlopen(url)
	jsongeocode = response.read()
	geo = parse_json(jsongeocode)
	return [city, state_full_name, state, country, geo[0], geo[1]]


def parse_json(code) :
	response = json.loads(code)
	if response['status'] == 'OK' :
		geo = response['results'][0]['geometry']['location']
		return [geo['lat'], geo['lng']]
	else :   
		print response['status']
		return ['0', '0']

def update_spreadsheet() :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open('Test Project')

	worksheet = sh.worksheet('States Short_Canada_Australia')

	for i in range(4, 17) :
		# state = worksheet.acell('B' + str(i)).value
		# country = 'Canada'
		# x = ['', state, country]
		# send_request_by_record(x)
		# worksheet.update_acell('C' + str(i), x[3])
		# worksheet.update_acell('D' + str(i), x[4])
		data = ['', worksheet.acell('A'+str(i)).value, worksheet.acell('B'+str(i)).value, 'Canada', worksheet.acell('C'+str(i)).value, worksheet.acell('D'+str(i)).value]
		sql = '''INSERT INTO zd_new_location(City, State, Abbreviation, Country, Latitude, Longitude) VALUES (\'{0[0]}\', \'{0[1]}\', \'{0[2]}\', \'{0[3]}\', {1}, {2}) ON DUPLICATE KEY UPDATE State = VALUES(State), Latitude = VALUES(Latitude), Longitude = VALUES(Longitude);'''.format(data, float(data[4]), float(data[5]))
		print sql

	for j in range(20, 30) :
		# state = worksheet.acell('B' + str(j)).value
		# country = 'Australia'
		# y = ['', state, country]
		# send_request_by_record(y)
		# worksheet.update_acell('C' + str(j), y[3])
		# worksheet.update_acell('D' + str(j), y[4])
		data = ['', worksheet.acell('A'+str(j)).value, worksheet.acell('B'+str(j)).value, 'Australia', worksheet.acell('C'+str(j)).value, worksheet.acell('D'+str(j)).value]
		sql = '''INSERT INTO zd_new_location(City, State, Abbreviation, Country, Latitude, Longitude) VALUES (\'{0[0]}\', \'{0[1]}\', \'{0[2]}\', \'{0[3]}\', {1}, {2}) ON DUPLICATE KEY UPDATE State = VALUES(State), Latitude = VALUES(Latitude), Longitude = VALUES(Longitude);'''.format(data, float(data[4]), float(data[5]))
		print sql

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

if __name__ == "__main__":
   # main(sys.argv[1:])
   update_spreadsheet()

