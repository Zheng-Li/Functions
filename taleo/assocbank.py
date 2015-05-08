# -*- coding: utf-8 -*-
import re
import urllib2
import socket
import httplib
import random
import gspread
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def login(spreadsheet) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open(spreadsheet)
	return sh

def url_parse(url) :
	try :
		page = urllib2.urlopen(url, timeout = 10)
		if page.getcode()>300 and page.getcode()!=304:
			print 'Error:' + page.getcode()
		page_data = page.read()
		sleep(random.uniform(0.1 ,0.3))
		return page_data
	except urllib2.URLError, e:
		print 'Page error!'
		return 
	except socket.error, v:
		print 'Socket error!'
		return 
	except (IOError, httplib.HTTPException):
		print 'Unknown error!'
		return


def assocbank_parse_javascript(browser, url, page) :
	browser.get(url)
	
	display = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.NAME, 'dropListSize')))
	Select(display).select_by_value('100')

	sleep(1)
	for i in range(1, page) :
		pager = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.NAME, "rlPager")))
		button = pager.find_elements_by_tag_name("a")[-1]
		button.click()
		sleep(1)

	job_url_base = 'https://assocbank.taleo.net/careersection/prof/jobdetail.ftl?job='
	records = []

	try :
		sleep(1)
		table = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'contentlist')))
		jobs = table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[::2]
		records = []
		for j in jobs:
			job = j.find_elements_by_class_name('contentlinepanel')
			job_title = job[0].find_element_by_tag_name('a').text
			job_location = job[1].find_element_by_tag_name('span').text
			job_url = job_url_base + job[0].find_elements_by_tag_name('span')[-1].text
			for item in assocbank_location(job_location) :
				record = [job_title, job_url] + item
				records.append(record)
			print job_title + '---' + job_url + '......Done'
		return records
	except StaleElementReferenceException:
		print 'Selenium wait founction error'
		return
	except TimeoutException:
		print 'Time out for page load'
		return


def assocbank_location(location) :
	result = []
	loc = re.split(',', location)
	for l in loc :
		sl = re.split('-', l)
		country = 'USA'
		if len(sl)>1 :
			state = sl[0].strip()
			city = sl[1].strip()
			result.append([city, state, country])
	return result

if __name__ == '__main__':
	url = 'https://assocbank.taleo.net/careersection/prof/jobsearch.ftl?lang=en'
	page = url_parse(url)

	result = []

	browser = webdriver.Firefox()
	# assocbank_parse_javascript(browser, url, 3)
	for i in range(1, 4) :
		result += assocbank_parse_javascript(browser, url, i)
	browser.quit()

	sheet = login('Test')
	worksheet = sheet.worksheet('Associated Bank (Associated Banc-Corp)')

	for x, row in enumerate(result) :
		# row_num = x+2+(page-1)*150 # In case of multiple location
		row_num = x+2
		cell_list = worksheet.range('A'+str(row_num)+':E'+str(row_num))
		for y, val in enumerate(row) :
			cell_list[y].value = val
		worksheet.update_cells(cell_list)
		print 'Row No.' + str(row_num) + ': '
		print row
