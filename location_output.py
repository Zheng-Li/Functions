import re
import gspread
import MySQLdb
from Geolocation.geolocation import *
from oauth2client.client import SignedJwtAssertionCredentials
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def login(spreadsheet, worksheet) :
	print 'Loading Worksheet ...'

	json_key = json.load(open('zheng-6cef143e8ce1.json'))
	scope = ['https://spreadsheets.google.com/feeds']

	credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
	gc = gspread.authorize(credentials)
	ws = gc.open(spreadsheet).worksheet(worksheet)

	print 'Worksheet download .... Completed!'
	return ws


def download_location_list(worksheet) :
	data_list = worksheet.get_all_values()
	del data_list[0]

	location_list = []
	for row in data_list :
		loc = [row[2].strip(), row[3].strip(), row[4].strip()]
		print loc
		location_list.append(loc)
	location_set = set(map(tuple,location_list))  #need to convert the inner lists to tuples so they are hashable
	locations = map(list,location_set) #Now convert tuples back into lists (maybe unnecessary?)

	result = []
	for item in locations :
		tmp = send_request_by_location(item[0], item[1], item[2])
		result.append(tmp)
		print tmp
	return result


def update_spreadsheet(worksheet, location_list) :
	# Header
	cell_list = worksheet.range('A1:F1')
	cell_values = ['City', 'State', 'Abbrevation', 'Country', 'Latitude', 'Longitude']
	for i, val in enumerate(cell_values):  #gives us a tuple of an index and value
	    cell_list[i].value = val    #use the index on cell_list and the val from cell_values
	worksheet.update_cells(cell_list)

	# Data
	for x, rec in enumerate(location_list) :
		num = x+2
		cell_list = worksheet.range('A'+str(num)+':F'+str(num))
		for i, val in enumerate(rec) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)

def upload_location(worksheet) :
	# <City, State, Abbreviation, Country, Latitude, Longitude>
	data_list = worksheet.get_all_values()
	data_list.pop(0) # Remove header row

	for data in data_list :
		f = open('Result/locations.sql', 'a')
		data[0] = MySQLdb.escape_string(data[0].strip())
		data[1] = MySQLdb.escape_string(data[1].strip())
		data[2] = MySQLdb.escape_string(data[2].strip())
		data[3] = MySQLdb.escape_string(data[3].strip())
		# sql = '''INSERT INTO zd_new_location(City, State, Abbreviation, Country, Latitude, Longitude) VALUES (\'{0[0]}\', \'{0[1]}\', \'{0[2]}\', \'{0[3]}\', {1}, {2}) ON DUPLICATE KEY UPDATE State = VALUES(State), Latitude = VALUES(Latitude), Longitude = VALUES(Longitude);'''.format(data, float(data[4]), float(data[5]))
		sql = '''UPDATE zd_new_location SET State = \'{0[1]}\', Latitude = \'{1}\', Longitude = \'{2}\' WHERE City = \'{0[0]}\' and Abbreviation = \'{0[2]}\' and  Country = \'{0[3]}\'; '''.format(data, float(data[4]), float(data[5]))
		print sql
		f.write(sql + '\n')

if __name__ == '__main__':
	spreadsheet_name = 'Organization Parsing Project 04'

	# --------- Download Locastions from Job Search Result --------------
	# location_worksheet_name = 'loc'
	# loc_worksheet = login(spreadsheet_name, location_worksheet_name)
	# location_list = download_location_list(loc_worksheet)

	# # -------- Download to local csv file --------
	# writer = csv.writer(open('Result/Locations.csv', 'w'))
	# for item in location_list :
	# 	writer.writerow(item)

	# --------- Send Query to Google Geocoding API --------------
	result_worksheet_name = 'loc_result'
	result_worksheet = login(spreadsheet_name, result_worksheet_name)
	# update_spreadsheet(result_worksheet, location_list)


	# --------- Translate Locations into SQL --------------
	upload_location(result_worksheet)




