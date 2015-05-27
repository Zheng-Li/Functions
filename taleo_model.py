# -*- coding: utf-8 -*-
import re
import urllib2
import socket
import httplib
import random
import gspread
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


def login(spreadsheet) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open(spreadsheet)
	return sh


def update_spreadsheet(data, spreadsheet, worksheet) :
	ss = login(spreadsheet)
	ws = ss.worksheet(worksheet)

	for x, row in enumerate(data) :
		num = x+2 # Skip header row
		cell_list = ws.range('A'+str(num)+':F'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		print 'Row No.' + str(x) + '....' + str(cell_list[0].value)
		ws.update_cells(cell_list)


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
	for i in range(0, num_of_pages) :
		pager = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, '')))  
		if i != 0 :
			pager.click()
		sleep(3)

		table = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '')))
		jobs = table.
		for job in jobs :
			title = 
			url = 
			location = 
			result.append([title, url] + location + [''])
			print title + '......' + url + '......Done'

	return result


def parse_job_location(location) :
	parsed_loc = []

	loc = re.split('', location)

	parsed_loc = [city, abbr, country]
	return parsed_loc # <City, Abbreviation, Country>


def parse_job_details(browser, spreadsheet, worksheet) :
	ss = login(spreadsheet)
	ws = ss.worksheet(worksheet)
	raw_data = ws.get_all_values()
	raw_data.pop(0) # Remove header line from spreadsheet

	for x, val in enumerate(raw_data) :
		url = val[1]
		browser.get(url)
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
				ws.update_acell('G'+str(x+2), snippet)
				print 'Line No.' + str(x+2) + '.......' + url
			else :
				print 'Line No.' + str(x+2) + '.......Job not found'
				
		else :
			print 'Line No.' + str(x+2) + '.......Skipped'


if __name__ == '__main__':
	start_time = time.time()

	url = ''
	spreadsheet = ''
	worksheet = ''
	num_of_pages = 0 # Number of pages in the search result
	keyword = '' # Keywords if certain jobs are needed.

	# ------ Search page url check --------
	if not check_url_status(url) :
		print 'Error URL!'

	# -------- Parse job search page -----------
	browser = webdriver.Firefox()
	browser.get(url)
	parsed_data = parse_job_search_page(browser, keyword, num_of_pages)
	update_spreadsheet(parsed_data, spreadsheet, worksheet)
	browser.quit()

	# -------- Parse job detail page (spreadsheet update included)-----------
	browser = webdriver.Firefox()
	parse_job_details(browser, spreadsheet, worksheet)
	browser.quit()


	print("--- %s seconds ---" % (time.time() - start_time))





