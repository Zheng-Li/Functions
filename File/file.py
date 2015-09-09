# -*- coding: utf-8 -*-
import csv
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import time
from time import sleep
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def login(credentials_file, spreadsheet, worksheet) :
	json_key = json.load(open(credentials_file))
	scope = ['https://spreadsheets.google.com/feeds']

	credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
	gc = gspread.authorize(credentials)
	ws = gc.open(spreadsheet).worksheet(worksheet)

	return ws

def read_csv(csv_file_name, has_header) :
	data_list = []
	csv_reader = csv.reader(open(csv_file_name, 'rU'))
	for row in csv_reader :
		data_list.append(row)

	if has_header :
		del data_list[0]

	return data_list


def read_spreadsheet(credentials_file, spreadsheet_name, worksheet_name, has_header) :
	ws = login(credentials_file, spreadsheet_name, worksheet_name)
	data_list = ws.get_all_values()

	if has_header :
		del data_list[0]

	return data_list

def write_csv(csv_file_name, header_line, data_list) :
	writer = csv.writer(open(csv_file_name, 'w'))
	if header_line :
		writer.writerow(header_line)

	for row in data_list :
		writer.writerow(row)

def write_spreadsheet(credentials_file, spreadsheet_name, worksheet_name, header_line, data_list) :
	worksheet = login(credentials_file, spreadsheet_name, worksheet_name)

	# -------- Header (if exists)-----------
	if header_line : 
		length = len(header_line)
		header_cell_list = worksheet.range('A1:' + chr(ord('A') + length - 1) + '1')
		for i, val in enumerate(header_line):  #gives us a tuple of an index and value
			header_cell_list[i].value = val    #use the index on cell_list and the val from cell_values
		worksheet.update_cells(header_cell_list)


	# -------- Data -----------
	length = len(data_list[0])
	size = len(data_list)
	data_cell_list = worksheet.range('A2:'+ chr(ord('A') + length - 1) + str(size+1))
	for x, row in enumerate(data_list) :
		for y, val in enumerate(row) :
			data_cell_list[x*length + y].value = val
	worksheet.update_cells(data_cell_list)

if __name__ == '__main__':
	start_time = time.time()

	credentials_file = 'zheng-6cef143e8ce1.json'
	print ''

	print("--- %s seconds ---" % (time.time() - start_time))
	




