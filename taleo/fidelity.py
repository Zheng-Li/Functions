# -*- coding: utf-8 -*-
import re
import urllib2
import socket
import httplib
import random
import gspread
from time import sleep
# from Geolocation.geolocation_reference import get_abbrevation
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
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

def fidelity_parse_jobs(url, page) :
	browser = webdriver.Firefox()
	browser.get(url)

	for i in range(1, page) :
		pager = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, "jobPager")))
		button = pager.find_elements_by_tag_name("span")[3].find_element_by_tag_name("span").find_element_by_tag_name("a")
		button.click()

	records = []
	WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "tr")))
	table = browser.find_element_by_id('jobs').find_element_by_tag_name("tbody")
	jobs = table.find_elements_by_tag_name("tr")
	for j in jobs:
		job_title = j.find_elements_by_tag_name("td")[1].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("a").text
		job_url = j.find_elements_by_tag_name("td")[1].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("a").get_attribute("href")
		job_location = j.find_elements_by_tag_name("td")[2].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("span").text
		job_posted = j.find_elements_by_tag_name("td")[3].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("span").text
		record = [job_title, job_url] + fidelity_location(job_location) + [job_posted]
		records.append(record)
		print record

	# update_spreadsheet(records, 'Intel', page)
	csv_output(records, 'Result/fidelity.csv')
	browser.quit()

def fidelity_location(location) :
	if location == 'Multiple Locations' :
		return ['', '', '']
	elif location == 'United States' :
		return ['USA', '' , '']
	else : 
		loc = re.split('-', location)
		country = 'USA' if loc[0] == 'US' else loc[0]
		state = get_abbrevation(loc[1]) if len(loc) > 1 else ''
		city = loc[2] if len(loc) > 2 else ''
	return [country, state, city]

def update_spreadsheet(data, sheet_name, loc) :
	sheet = login('Test')
	worksheet = sheet.worksheet(sheet_name)

	for x, row in enumerate(data) :
		num = x + 2 + 25*(loc-1)
		cell_list = worksheet.range('A'+str(num)+':F'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)

if __name__ == '__main__':
	url = 'https://fidelity.taleo.net/careersection/10020/jobsearch.ftl'
	page = url_parse(url)

	# print sys.path
	# get_abbrevation('New York')

	# Get certain page 
	# fidelity_parse_javascript(url, 2)

	# Get whole range of pages
	# for i in range(0, 10) :
	# 	fidelity_parse_javascript(url, i)

