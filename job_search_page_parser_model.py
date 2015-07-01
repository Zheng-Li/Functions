# -*- coding: utf-8 -*-
import re
import urllib2
import socket
import httplib
import csv
import json
import gspread
import time
from File.file import *
from oauth2client.client import SignedJwtAssertionCredentials
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

def check_url_status(url) :
	try :
		page = urllib2.urlopen(url, timeout = 10)
		if page.getcode()>300 and page.getcode()!=304:
			print 'Error:' + page.getcode()
			return False
		return True
	except urllib2.URLError, e:
		print 'Page error!'
		return False
	except socket.error, v:
		print 'Socket error!'
		return False
	except (IOError, httplib.HTTPException):
		print 'Unknown error!'
		return False

def load_remove_keywords () :
	spreadsheet_name = 'Test Project'
	worksheet_name = 'Keywords_Jobs to Remove'
	ws = login(spreadsheet_name, worksheet_name)

	keyword_dict = ws.col_values(1)
	del keyword_dict[0]

	return keyword_dict

def check_if_exists (title, keyword_dict) :
	if any (keyword.lower() in title.lower() for keyword in keyword_dict) :
		return True
	else :
		return False

def load_tag_keywords () :
	spreadsheet_name = 'Test Project'

	worksheet_name_1 = 'Keywords Page 1 Job Tags June 6'
	ws_1 = login(spreadsheet_name, worksheet_name_1)
	keyword_dict_1 = {}

	raw_data_1 = ws_1.get_all_values()
	for row in raw_data_1 :
		key = row.pop(0).lower().strip()
		values = filter(None, row)
		keyword_dict_1[key] = [x.lower() for x in values]

	worksheet_name_2 = 'Keywords Page 2 Job Tags June 6'
	ws_2 = login(spreadsheet_name, worksheet_name_2)
	keyword_dict_2 = {}

	raw_data_2 = ws_2.get_all_values()
	for row in raw_data_2 :
		key = row.pop(0).lower().strip()
		values = filter(None, row)
		keyword_dict_2[key] = [x.lower() for x in values]

	return  keyword_dict_1, keyword_dict_2

def tag_job (title, keyword_dict) :
	tag_list = []
	title = re.escape(title.strip().lower())
	for ky in keyword_dict.keys() :
		ky = re.escape(ky)
		reg = '\\b' + ky + '[,.]?\\b'
		result = re.search(reg, title)  
		if result is not None :
			tag_list.append(ky)
			tag_list += keyword_dict[ky]

	tags = list(set(tag_list))
	return tags

def parse_job_search_page(browser, keyword, num_of_pages) :
	result = []

	remove_keyword_dict = load_remove_keywords()
	tag_keyword_dict_1, tag_keyword_dict_2 = load_tag_keywords()

	# ------------ Add keyword to search ---------------
	# key_search = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '')))
	# key_search.clear()
	# key_search.send_keys(key)
	# key_search.send_keys(Keys.ENTER)
	# browser.implicitly_wait(2)

	# ----------- Change number of result per page -------
	# display = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.NAME, '')))
	# Select(display).select_by_value('100')
	# browser.implicitly_wait(2)

	# ------------ Parse all pages of search result ------------
	# button_moreJobs = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH,'')))
	# while len(browser.find_elements_by_xpath('')) > 0 :
	# 	button_moreJobs = browser.find_element_by_xpath('')
	# 	button_moreJobs.click()
	# 	button_moreJobs = None
	# 	browser.implicitly_wait(1.7)
	# browser.implicitly_wait(2)

	# ------------ Switch to inner iframe if exists ----------
	# browser.switch_to.frame(browser.find_element_by_tag_name('iframe'))

	
	try : 
		# ------------ Parse all pages of search result ------------
		for i in range(0, num_of_pages) :
			pager = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, '')))  
			if i != 0 :
				pager.click()
			browser.implicitly_wait(3)

			table = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '')))
			jobs = table.find_elements_by_tag_name('tr')
			for job in jobs :
				title = job.find_element_by_tag_name('a').text
				url = job.find_element_by_tag_name('a').get_attribute('href')
				print title + '......' + url + '......Done'
				location = parse_job_location()
				if check_if_exists(title, remove_keyword_dict) :
					tags_list = 'Experienced'
				else :
					tags = tag_job(title, tag_keyword_dict_1)
					if tags != '' :
						tags += tag_job(title, tag_keyword_dict_2)
						tags_list = ','.join(list(set(tags)))
				result.append([title, url] + location + ['', tags_list])
		return result 
	except :
		return result


def parse_job_location(location) :
	parsed_loc = []
	city = ''
	abbr = ''
	country = ''

	loc = re.split('', location)

	if 'US' in country :
		country = 'USA'
	elif 'United States' in country :
		country = 'USA'
	elif 'United Kingdom' in country :
		country = 'UK'
	elif 'United Arab Emirates' in country :
		country = 'UAE'
	elif 'Great Britain' in country :
		country = 'UK'

	parsed_loc = [city, abbr, country]
	print parsed_loc
	return parsed_loc # <City, Abbreviation, Country>


def parse_job_details(browser, worksheet) :
	raw_data = worksheet.get_all_values()
	raw_data.pop(0) # Remove header line from spreadsheet

	for x, val in enumerate(raw_data) :
		url = val[1]
		if val[6] == '' :
			browser.get(url)
			try :
				snippet = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "job")))
				snippet = snippet.get_attribute('innerHTML')

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
				
			if snippet is not None :
				worksheet.update_acell('G'+str(x+2), snippet)
				print 'Line No.' + str(x+2) + '.......' + url
			else :
				print 'Line No.' + str(x+2) + '.......Job not found'
				
		else :
			print 'Line No.' + str(x+2) + '.......Skipped'


if __name__ == '__main__':
	start_time = time.time()

	url = ''
	spreadsheet_name = ''
	worksheet_name = ''
	local_sheet_name = ''
	num_of_pages = 0 # Number of pages in the search result
	keyword = '' # Keywords if certain jobs are needed.
	

	# ------ Search page url check --------
	if not check_url_status(url) :
		print 'Error URL!'

	# -------- Parse job search page -----------
	browser = webdriver.Firefox()
	browser.get(url)
	parsed_data = parse_job_search_page(browser, keyword, num_of_pages)
	browser.quit()

	# -------- Download to local csv file --------
	writer = csv.writer(open('Result/'+local_sheet_name, 'w'))
	for item in parsed_data :
		writer.writerow(item)

	# -------- Upload result to spreadsheet
	header_line = ['Job Title', 'Job Url', 'City', 'State',	'Country', 'Snippet', 'Tags']
	write_spreadsheet(spreadsheet_name, worksheet_name, header_line, parsed_data)

	# -------- Parse job detail page (spreadsheet update included)-----------
	browser = webdriver.Firefox()
	parse_job_details(browser, ws)
	browser.quit()


	print("--- %s seconds ---" % (time.time() - start_time))






