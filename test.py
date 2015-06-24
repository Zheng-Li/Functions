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

def load_remove_keywords () :
	spreadsheet_name = 'Test Project'
	worksheet_name = 'Keywords_Jobs to Remove'
	ws = login(spreadsheet_name, worksheet_name)

	keyword_dict = ws.col_values(1)

	return keyword_dict

def check_if_exists (title, keyword_dict) :
	if any (keyword.strip().lower() in title.lower() for keyword in keyword_dict) :
		return True
	else :
		return False

def load_tag_keywords_1 () :
	spreadsheet_name = 'Test Project'
	worksheet_name = 'Keywords Page 1 Job Tags June 6'
	ws = login(spreadsheet_name, worksheet_name)

	keyword_dict = {}

	raw_data = ws.get_all_values()
	for row in raw_data :
		key = row.pop(0).strip().lower()
		values = filter(None, row)
		keyword_dict[key] = [x.lower() for x in values]

	return  keyword_dict

def load_tag_keywords_2 () :
	spreadsheet_name = 'Test Project'
	worksheet_name = 'Keywords Page 2 Job Tags June 6'
	ws = login(spreadsheet_name, worksheet_name)

	keyword_dict = {}

	raw_data = ws.get_all_values()
	for row in raw_data :
		key = row.pop(0).strip().lower()
		values = filter(None, row)
		keyword_dict[key] = [x.lower() for x in values]

	return  keyword_dict

def add_tags (title, keyword_dict) :
	tag_list = []
	for ky in keyword_dict.keys() :
		if ky.strip().lower() in title.lower() :
			tag_list.append(ky)
			tag_list += keyword_dict[ky]

	tags = list(set(tag_list))
	return tags

if __name__ == '__main__':
	start_time = time.time()

	spreadsheet_name = 'Organization Parsing New Companies from Carol_May2015'
	worksheet_name = 'Test'
	ws = login(spreadsheet_name, worksheet_name)


	# ---------- Remove jobs -----------
	raw_data = ws.get_all_values()
	del raw_data[0]
	remove_keyword_dict = load_remove_keywords()
	keyword_dict_1 = load_tag_keywords_1()
	keyword_dict_2 = load_tag_keywords_2()
	for i, row in enumerate(raw_data) :
		title = row[0].strip()
		if not check_if_exists(title, remove_keyword_dict) :
			tags = add_tags(title, keyword_dict_1) + add_tags(title, keyword_dict_2)
			tags_list = list(set(tags))
			print title + '...' + ','.join(tags_list)
			ws.update_acell('H' + str(i+2), ','.join(tags_list))
		# else :
		# 	ws.update_acell('J' + str(i+2), 'Experienced')
		# 	print 'Row...' + str(i+2) + '...Experienced'

	# -------- Parse job detail page (spreadsheet update included)-----------
	# browser = webdriver.Firefox()
	# parse_job_details(browser, ws)
	# browser.quit()

	print("--- %s seconds ---" % (time.time() - start_time))






