# -*- coding: utf-8 -*-
import re
import urllib2
import socket
import httplib
import random
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import time
from time import sleep
from Geolocation.geolocation_reference import get_abbreviation
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from keyword_remove import check_if_exists
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

def parse_job_details(browser, worksheet) :
	raw_data = worksheet.get_all_values()
	raw_data.pop(0) # Remove header line from spreadsheet

	for x, val in enumerate(raw_data) :
		url = val[1]
		if val[2] == 'Multiple Locations' :
			browser.get(url)
			try :
				location = browser.find_element_by_xpath('//*[@id="requisitionDescriptionInterface.ID1808.row1"]').text
				if '-' not in location :
					city = ''
					abbr = ''
				else :
					city = re.split('-', location)[2]
					abbr = get_abbreviation(re.split('-', location)[1])
				# ------------- Trim for necessary part ----------------
				# soup = BeautifulSoup(snippet)
				# trimed_data = soup.find_all('div', {'class' : 'contentlinepanel'})[:1]
				# result = ''.join(str(tag) for tag in trimed_data)

			except StaleElementReferenceException:
				print 'Selenium Error!'
				return
			except TimeoutException:
				print 'Timeout Error!'
				return
				
			if city is not None :
				worksheet.update_acell('C'+str(x+2), city)
				worksheet.update_acell('D'+str(x+2), abbr)
				print 'Line No.' + str(x+2) + '.......' + url
			else :
				print 'Line No.' + str(x+2) + '.......Job not found'
				
		else :
			print 'Line No.' + str(x+2) + '.......Skipped'


if __name__ == '__main__':
	start_time = time.time()

	spreadsheet_name_1 = 'Organization Parsing New Companies from Carol_May2015'
	worksheet_name_1 = 'Honeywell International'
	ws_1 = login(spreadsheet_name_1, worksheet_name_1)

	# -------- Parse job detail page (spreadsheet update included)-----------
	# browser = webdriver.Firefox()
	# parse_job_details(browser, ws)
	# browser.quit()


	raw_data = ws_1.get_all_values()
	del raw_data[0]
	for i, row in enumerate(raw_data) :
		title = row[2].strip()
		if check_if_exists(title) :
			ws_1.update_acell('J' + str(num), 'Experienced')
			print 'Row...' + str(num) + '...Experienced'
		else :

	print("--- %s seconds ---" % (time.time() - start_time))






