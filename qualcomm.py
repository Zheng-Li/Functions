# -*- coding: utf-8 -*-
import re
import urllib2
import socket
import httplib
import random
import gspread
from time import sleep
from Geolocation.geolocation_reference import get_abbreviation
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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

def parse_job_search_page(browser, url, keyword) :
	if not check_url_status(url) :
		return

	result = []
	browser.get(url) 

	# ------------ Add keyword to search ---------------
	key_search = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-term"]')))
	key_search.send_keys(keyword)
	key_search.send_keys(Keys.ENTER)
	sleep(1)

	result = []
	WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="gridResult"]/table/thead')))
	table = browser.find_element_by_xpath('//*[@id="gridResult"]/table/tbody')
	rows = table.find_elements_by_tag_name('tr')
	jobs = [rows[i] for i in (2, 6, 10, 14, 18, 22, 26, 30, 34)]
	if len(rows) > 39: 
		jobs += row[38]
	for job in jobs :
		title = job.find_element_by_tag_name('a').text
		url = job.find_element_by_tag_name('a').get_attribute('href')
		print title


	return ''


def parse_job_location(location) :
	loc = re.split('', location)

	return location # <City, Abbreviation, Country>


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
				# soup = BeautifulSoup(snippet)
				# trimed_data = soup.find_all('div', {'class' : 'contentlinepanel'})[:1]
				# result = ''.join(str(tag) for tag in trimed_data)

				# # ------------ Test for Multiple locations ---------------
				# trimed_data = soup.find('span', {'id' : 'requisitionDescriptionInterface.ID1790.row1'})
				# result = intel_location(trimed_data.string)

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

	url = 'https://jobs.qualcomm.com/public/search.xhtml'
	spreadsheet = 'Test'
	worksheet = 'Qualcomm'
	keyword1 = 'Intern' # Keywords if certain jobs are needed.
	keyword2 = 'Analyst'

	# -------- Parse job search page -----------
	browser = webdriver.Firefox()
	parsed_data = []
	parsed_data += parse_job_search_page(browser, url, keyword1)
	parsed_data += parse_job_search_page(browser, url, keyword2)
	update_spreadsheet(parsed_data, spreadsheet, worksheet)
	# browser.quit()

	# -------- Parse job detail page (spreadsheet update included)-----------
	# browser = webdriver.Firefox()
	# parse_job_details(browser, spreadsheet, worksheet)
	# browser.quit()







