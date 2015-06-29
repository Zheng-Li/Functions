# -*- coding: utf-8 -*-
import csv
import time
from time import sleep
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def login(spreadsheet, worksheet) :
	json_key = json.load(open('zheng-6cef143e8ce1.json'))
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


def read_spreadsheet(spreadsheet_name, worksheet_name, has_header) :
	ws = login(spreadsheet_name, worksheet_name)
	data_list = ws.get_all_values()

	if has_header :
		del data_list[0]

	return data_list

def write_csv(csv_file_name, header_line, data_list) :





