import re
import gspread
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def update_spreadsheet(sheet_name, location_list) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open(sheet_name)
	# worksheet = sh.add_worksheet(title="Location", rows="200", cols="10")
	worksheet = sh.worksheet('Locations')

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

def upload_location(sheet_name) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open(sheet_name)
	worksheet = sh.worksheet('Locations')

	# <City, State, Abbreviation, Country, Latitude, Longitude>
	data_list = worksheet.get_all_values()
	data_list.pop(0) # Remove header row

	for data in data_list :
		f = open('Result/locations.sql', 'a')
		data[0] = MySQLdb.escape_string(data[0].strip())
		data[1] = MySQLdb.escape_string(data[1].strip())
		data[2] = MySQLdb.escape_string(data[2].strip())
		data[3] = MySQLdb.escape_string(data[3].strip())
		sql = '''INSERT INTO zd_new_location(City, State, Abbreviation, Country, Latitude, Longitude) VALUES (\'{0[0]}\', \'{0[1]}\', \'{0[2]}\', \'{0[3]}\', {1}, {2}) ON DUPLICATE KEY UPDATE State = VALUES(State), Latitude = VALUES(Latitude), Longitude = VALUES(Longitude);'''.format(data, float(data[4]), float(data[5]))
		f.write(sql + '\n')

if __name__ == '__main__':
	upload_location('Test')




