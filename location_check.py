# -*- coding: utf-8 -*-
import re
import csv
import json
import gspread
import time
from File.file import *
from oauth2client.client import SignedJwtAssertionCredentials
from Geolocation.geolocation_reference import get_abbreviation
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

def country_check(country) :
	correction = {
	# --------- US --------------
		'US'			:	'USA',
		'U.S.'			:	'USA',
		'United States'	:	'USA',
	# --------- UK --------------
		'United Kingdom':	'UK',
		'U.K.'			:	'UK',
		'GB'			:	'UK',
		'GBR'			:	'UK',
		'Great Britain'	:	'UK',
		'England'		:	'UK',
		'Scotland'		:	'UK',
		'Wales'			:	'UK',
	# --------- UAE -------------
		'United Arab Emirates'	:	'UAE',
		'U.A.E.'		:	'UAE',
	# --------- Other Countries -------------
		'CHN'			:	'China',
		'AUS'			:	'Australia',
		'BRA'			:	'Brazil',
		'CAN'			:	'Canada',
		'DEU'			:	'Germany',
		'IND'			:	'India',
		'ISR'			:	'Israel',
		'ITA'			:	'Italy',
		'JPN'			:	'Japan',
		'MEX'			:	'Mexico',
		'SGP'			:	'Singapore',
		'NZL'			:	'New Zealand',
		'TWN'			:	'Taiwan',
		'ZAF'			:	'South Africa',
		'KOR'			:	'South Korea',
		'HKG'			:	'Hong Kong',
		'MYS'			:	'Malaysia',
	} 

	if country in correction :
		return correction[country]
	else :
		return country


if __name__ == '__main__':
	start_time = time.time()

	credentials_file = 'zheng-6cef143e8ce1.json'
	spreadsheet_name = ''
	worksheet_name = ''
	country_col = 5

	worksheet = login(spreadsheet_name, worksheet_name)
	countries = worksheet.col_values(country_col)
	del countries[0]

	for num, country in enumerate(countries) :
		print country_check(country)

	print("--- %s seconds ---" % (time.time() - start_time))



