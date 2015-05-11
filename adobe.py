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


def adobe_parse_jobs(browser, page) :

	# job_url_base = 'https://adobe.taleo.net/careersection/2/jobdetail.ftl?job='
	job_url_base = 'https://adobe.taleo.net/careersection/adobe_global/jobdetail.ftl?job='

	records = []
	try :
		sleep(2)
		table = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'contentlist')))
		jobs = table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")[::2]
		for j in jobs:
			job = j.find_elements_by_class_name('contentlinepanel')
			job_title = job[0].find_element_by_tag_name('a').text
			job_posted = job[2].find_elements_by_tag_name('span')[2].text
			job_url = job_url_base + job[2].find_elements_by_tag_name('span')[-1].text
			job_location = job[1].text

			loc = re.split(', ', job_location)
			for l in loc :
				ll = re.split('-', l)
				city = ll[2]
				country = ll[1]
				record = [job_title, job_url, city, '', country, job_posted]
				records.append(record)
				print 'Page ' + str(page) + '....' + job_title
		return records
	except StaleElementReferenceException:
		print 'Selenium wait founction error'
		return
	except TimeoutException:
		print 'Time out for page load'
		return


# ------------- Adobe sheet update --------------
def update_spreadsheet(data, sheet_name) :
	sheet = login('Test')
	worksheet = sheet.worksheet(sheet_name)

	for x, row in enumerate(data) :
		num = x + 2
		cell_list = worksheet.range('A'+str(num)+':F'+str(num)) # Created_on time included
		for i, val in enumerate(row) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)
		print 'Row No.' + str(x) + '...' + cell_list[0].value


if __name__ == '__main__':
	# url = 'https://adobe.taleo.net/careersection/2/jobsearch.ftl'
	url = 'https://adobe.taleo.net/careersection/adobe_global/jobsearch.ftl'
	result = []

	browser = webdriver.Firefox()
	browser.get(url)
	display = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.NAME, 'dropListSize')))
	Select(display).select_by_value('100')
	sleep(1)

	for i in range(1, 4) :
		if i != 1:
			pager = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "pagerpanel")))
			button = pager.find_elements_by_tag_name("a")[-1]
			button.click()
			sleep(1)
		result += adobe_parse_jobs(browser, i)

	browser.quit()
	update_spreadsheet(result, 'Adobe_global')

