import re
import csv
import json
import urllib2
import string
from time import sleep
from location_reference import get_full_name
import random

URL = 'https://maps.googleapis.com/maps/api/geocode/json?address=' 
API_KEY = "AIzaSyAW3GX8hrAuoET8ESMA8rB8Y7AXqTHMH6I"
result = []

def read_file():
	in_file = csv.reader(open('location.csv', 'rU'))
	for row in in_file : 
		# tmp = [row['City'], row['State Full Name'] ,row['State'], row['Country']]
		result.append(row)

def write_file():
	out_file = csv.writer(open('result.csv', 'wb', buffering=0))
	for x in result :
		print (x)  
		out_file.writerow(x)

def send_request_by_record(record):
	address = record[1] + ',+' + record[2] + ',+' + record[3] + ',+' + record[4]
	address = address.replace(" ", "+")
	url = URL + address
	response = urllib2.urlopen(url)
	jsongeocode = response.read()
	geo = parse_json(jsongeocode)
	record[6] = geo[0]
	record[7] = geo[1]
	return record

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

if __name__ == '__main__':
	read_file()
	for item in result :
		item = send_request(item)
		print item
		# import_db(item)
		sleep(random.uniform(1.6, 3.6))
	write_file()

