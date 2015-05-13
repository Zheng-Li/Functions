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

def parse_job_search_page(browser, keyword, page) :

	# ------------ Add keyword to search ---------------
	key_search = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-term"]')))
	key_search.clear()
	key_search.send_keys(keyword)
	key_search.send_keys(Keys.ENTER)
	sleep(1)

	for x in range(1, page) :
		WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="c1"]/section/div[2]/div[2]/div[2]/div[5]/div[1]/ul/li[6]/a'))).click()

	urls = []
	WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="gridResult"]/table/thead')))
	table = browser.find_element_by_xpath('//*[@id="gridResult"]/table/tbody')
	job_links = table.find_elements_by_tag_name('a')
	for link in job_links :
		url = link.get_attribute('href')
		if url not in urls :
			urls.append(url)

	return urls


def parse_job_location() :
	ss = login(spreadsheet)
	ws = ss.worksheet(worksheet)
	raw_data = ws.get_all_values()
	raw_data.pop(0) # Remove header line from spreadsheet

	for x, val in enumerate(raw_data) :
		location = val[2]
		city = re.split(' - ', location)[1].strip()
		state = re.split(' - ', location)[0].strip()
		if state == get_abbreviation(state) :
			country = state
			state = ''
		else :
			state = get_abbreviation(state)
			country = 'USA'

		ws.update_acell('C'+str(x+2), city)
		ws.update_acell('D'+str(x+2), state)
		ws.update_acell('E'+str(x+2), country)



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
				title = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="jobDetailsForm:jobTitle"]'))).text
				location = browser.find_element_by_xpath('//*[@id="jobDetailsForm"]/table[2]/tbody/tr[1]/td/table/tbody/tr[6]/td[3]').text
				snippet = browser.find_element_by_xpath('//*[@id="jobDetailsForm"]/table[2]/tbody/tr[1]/td/table').get_attribute('innerHTML')

			except StaleElementReferenceException:
				print 'Selenium Error!'
				return
			except TimeoutException:
				print 'Timeout Error!'
				return
				
			if title is not None :
				ws.update_acell('A'+str(x+2), title)
				ws.update_acell('C'+str(x+2), location)
				print 'Line No.' + str(x+2) + '.......' + url
			else :
				print 'Line No.' + str(x+2) + '.......Job not found'
				
		else :
			print 'Line No.' + str(x+2) + '.......Skipped'


if __name__ == '__main__':

	url = 'https://jobs.qualcomm.com/public/search.xhtml'
	if not check_url_status(url) :
		print 'Error URL!'

	spreadsheet = 'Test'
	worksheet = 'Qualcomm'
	keyword1 = 'Intern' # Keywords if certain jobs are needed.
	keyword2 = 'Analyst'

	# -------- Parse job search page -----------
	# browser = webdriver.Firefox()
	# browser.get(url) 
	# parsed_data = []
	# parsed_data += parse_job_search_page(browser, keyword1, 1)
	# parsed_data += parse_job_search_page(browser, keyword2, 1)
	# parsed_data += parse_job_search_page(browser, keyword2, 2)
	# parsed_data += parse_job_search_page(browser, keyword2, 3)
	# parsed_data += parse_job_search_page(browser, keyword2, 4)
	# browser.quit()

	# ss = login(spreadsheet)
	# ws = ss.worksheet(worksheet)
	# for i, url in enumerate(parsed_data) :
	# 	ws.update_acell('B'+str(i+2), url)

	# -------- Parse job detail page (spreadsheet update included)-----------
	browser = webdriver.Firefox()
	parse_job_details(browser, spreadsheet, worksheet)
	browser.quit()

	# -------- Parse job locations -----------
	parse_job_location()







