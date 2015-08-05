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

def parse_job_search_page(browser, keyword, num_of_pages) :
	result = []
	base_url = ''

	# ------------ Parse all pages of search result ------------
	table = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="jvform"]/div/div[2]/div')))
	jobs = table.find_elements_by_tag_name('li')
	for job in jobs :
		title = job.find_element_by_tag_name('a').text

		url_block = job.find_element_by_tag_name('a').get_attribute('onclick')
		re_url = re.compile("\\'[a-z0-9A-Z]+\\'")
		serial_url = re_url.search(url_block).group(0)
		url = base_url + serial_url.replace('\'', '')

		print title + '......' + url + '......Done'
		location = parse_job_location()
		result.append([title, url] + location)

	return result 


def parse_job_location(location) :
	parsed_loc = []
	city = ''
	abbr = ''
	country = ''

	loc = re.split('', location) 

	if country.lower() == 'us':
		country = 'USA'
	elif country.lower() == 'united states' :
		country = 'USA'
	elif country.lower() == 'united kingdom' :
		country = 'UK'
	elif country.lower() == 'united arab emirates' :
		country = 'UAE'
	elif country.lower() == 'great britain' :
		country = 'UK'

	parsed_loc = [city, abbr, country]
	print parsed_loc
	return parsed_loc # <City, Abbreviation, Country>


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

	# -------- Upload result to spreadsheet -----------
	header_line = ['Job Title', 'Job Url', 'City', 'State',	'Country', 'Snippet', 'Tags']
	write_spreadsheet(spreadsheet_name, worksheet_name, header_line, parsed_data)


	print("--- %s seconds ---" % (time.time() - start_time))


