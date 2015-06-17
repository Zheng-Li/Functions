# -*- coding: utf-8 -*-
import re
import urllib2
import socket
import httplib
import csv
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
	json_key = json.load(open('zheng-36483ac6d4a3.json'))
	scope = ['https://spreadsheets.google.com/feeds']

	credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
	gc = gspread.authorize(credentials)
	ws = gc.open(spreadsheet).worksheet(worksheet)

	return ws


def update_spreadsheet(data, page, worksheet) :
	for x, row in enumerate(data) :
		num = x+2+page*100 # Skip header row
		cell_list = worksheet.range('A'+str(num)+':F'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		print 'Row No.' + str(num) + '....' + str(cell_list[0].value)
		worksheet.update_cells(cell_list)

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

def parse_job_search_page(browser, keyword, num_of_pages) :
	result = []

	# ------------ Add keyword to search ---------------
	# key_search = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '')))
	# key_search.clear()
	# key_search.send_keys(key)
	# key_search.send_keys(Keys.ENTER)
	# sleep(1)

	# ----------- Change number of result per page -------
	# display = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.NAME, '')))
	# Select(display).select_by_value('100')
	# sleep(1)

	# ------------ Parse all pages of search result ------------
	# button_moreJobs = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH,'')))
	# while len(browser.find_elements_by_xpath('')) > 0 :
	# 	button_moreJobs = browser.find_element_by_xpath('')
	# 	button_moreJobs.click()
	# 	button_moreJobs = None
	# 	sleep(1.7)
	# sleep(5)

	# ------------ Parse all pages of search result ------------
	for i in range(0, num_of_pages) :
		pager = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, '')))  
		if i != 0 :
			pager.click()
		sleep(3)

		table = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '')))
		jobs = table.find_elements_by_tag_name('tr')
		for job in jobs :
			title = 
			url = 
			location = 
			result.append([title, url] + location + [''])
			print title + '......' + url + '......Done'

	return result


def parse_job_location(location) :
	parsed_loc = []
	city = ''
	abbr = ''
	country = ''

	loc = re.split('', location)

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
	ws = login(spreadsheet_name, worksheet_name)
	update_spreadsheet(parsed_data, 0, ws)

	# -------- Parse job detail page (spreadsheet update included)-----------
	browser = webdriver.Firefox()
	parse_job_details(browser, ws)
	browser.quit()


	print("--- %s seconds ---" % (time.time() - start_time))






