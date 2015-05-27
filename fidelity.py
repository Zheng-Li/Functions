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

def fidelity_parse_jobs(url, page, key) :
	browser = webdriver.Firefox()
	browser.get(url)

	# for i in range(1, page) :
	# 	pager = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, "jobPager")))
	# 	button = pager.find_elements_by_tag_name("span")[3].find_element_by_tag_name("span").find_element_by_tag_name("a")
	# 	button.click()

	# ------------ Add keyword to search ---------------
	key_search = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="KEYWORD"]')))
	key_search.send_keys(key)
	key_search.send_keys(Keys.ENTER)
	sleep(1)

	records = []
	WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "tr")))
	table = browser.find_element_by_id('jobs').find_element_by_tag_name("tbody")
	jobs = table.find_elements_by_tag_name("tr")
	for j in jobs:
		job_title = j.find_elements_by_tag_name("td")[1].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("a").text
		job_url = j.find_elements_by_tag_name("td")[1].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("a").get_attribute("href")
		job_location = j.find_elements_by_tag_name("td")[2].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("span").text
		job_posted = j.find_elements_by_jptag_name("td")[3].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("span").text
		record = [job_title, job_url] + fidelity_location(job_location) + [job_posted]
		records.append(record)
		print record
	
	browser.quit()
	return records

def fidelity_location(location) :
	if location == 'Multiple Locations' :
		return ['', '', '']
	elif location == 'United States' :
		return ['USA', '' , '']
	else : 
		loc = re.split('-', location)
		country = 'USA' if loc[0] == 'US' else loc[0]
		state = get_abbreviation(loc[1]) if len(loc) > 1 else ''
		city = loc[2] if len(loc) > 2 else ''
	return [city, state, country]

def fidelity_job_details(url) :
	job_sh = login('Test')
	sh = job_sh.worksheet('Fidelity_Intern')
	raw_data = sh.get_all_values()
	raw_data.pop(0)

	browser = webdriver.Firefox()
	for x, val in enumerate(raw_data) :
		url = val[1]
		if val[6] == '' :
			try :
				job_data = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "job")))
				job_data = job_data.get_attribute('innerHTML')
				# soup = BeautifulSoup(job_data)
				# trimed_data = soup.find_all('div', {'class' : 'contentlinepanel'})[:1]
				# result = ''.join(str(tag) for tag in trimed_data)

				result = job_data

				# # ------------ Test for Multiple locations ---------------
				# trimed_data = soup.find('span', {'id' : 'requisitionDescriptionInterface.ID1790.row1'})
				# result = intel_location(trimed_data.string)

				return result
			except StaleElementReferenceException:
				return
			except TimeoutException:
				return



			print str(x) + '.......' + url
			if snippet is not None :
				sh.update_acell('G'+str(x+2), snippet)
				print 'Line No.' + str(x+2) + '.......' + url
			else :
				print 'Line No.' + str(x+2) + '.......Job not found'
	browser.quit() 



	return details


def update_spreadsheet(data, sheet_name) :
	sheet = login('Test')
	worksheet = sheet.worksheet(sheet_name)

	for x, row in enumerate(data) :
		num = x+2
		cell_list = worksheet.range('A'+str(num)+':F'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		print 'Row No.' + str(x) + '....' + str(cell_list[0].value)
		worksheet.update_cells(cell_list)


if __name__ == '__main__':
	url = 'https://fidelity.taleo.net/careersection/10020/jobsearch.ftl'
	page = url_parse(url)

	result = []
	result += fidelity_parse_jobs(url, 1, 'intern')
	result += fidelity_parse_jobs(url, 1, 'college graduates')

	update_spreadsheet(result, 'Fidelity_Intern')



