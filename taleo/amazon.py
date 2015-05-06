# -*- coding: utf-8 -*-
import re
import urllib2
import socket
import httplib
import json
import gspread
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def login(sheet_name) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open(sheet_name)
	return sh


def update_spreadsheet(data, sheet_name, loc) :
	sheet = login('Test')
	worksheet = sheet.worksheet(sheet_name)

	for x, row in enumerate(data) :
		num = x + 2 + 30*(loc-1) # 30 records per page
		cell_list = worksheet.range('A'+str(num)+':E'+str(num)) # Post time not included
		for i, val in enumerate(row) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)


def amazon_parse_jobs(browser, p) :
	sleep(1.7)
	all_jobs = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
	jobs = all_jobs.find_elements_by_tag_name('tr')
	results = []
	for job in jobs :
		j = job.find_elements_by_tag_name('td')
		job_title = j[1].text
		job_url = j[1].find_element_by_tag_name('a').get_attribute('href')
		job_location = adobe_location(j[3].text)
		print job_title + '......' + ','.join(job_location)
		job_rec = [job_title, job_url] + job_location 
		results.append(job_rec)
	# update_spreadsheet(results, 'Amazon', p)
	return results

def adobe_location(loc) :
	tmp = re.split(', ', loc)
	country = tmp[0]
	if len(tmp) == 1 :
		state = ''
		city = ''
	if len(tmp) == 2 :
		state = ''
		if 'Virtual' in tmp[1] :
			city = ''
		else :
			city = tmp[1]
	if len(tmp) == 3 :
		if 'Virtual' in tmp[2] :
			city = ''
		else :
			city = tmp[2]
		if country == 'US' :
			state = tmp[1]
		else :
			state = ''
	return [city, state, country]

def amazon_new_jobs() :

	intern_url = 'http://www.amazon.jobs/results?searchStrings[]=intern'
	leadership_url = 'http://www.amazon.jobs/results?searchStrings[]=leadership'
	mba_url = 'http://www.amazon.jobs/results?searchStrings[]=MBA'

	browser = webdriver.Firefox()
	browser.get(intern_url)

	# -------------- Jump to page 28 -------------------
	# for x in range (0, 27) :
	# 	button = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.LINK_TEXT, 'Next')))
	# 	button.click()

	results = []

	# 3 Pages in Intern
	for p in range (1, 4) :
		if p != 1 :
			button = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.LINK_TEXT, 'Next')))
			button.click()
		results += amazon_parse_jobs(browser, p)

	# First page in MBA
	browser.get(mba_url)
	results += amazon_parse_jobs(browser, 1)

	# First page in Leadership
	browser.get('http://www.amazon.jobs/results?searchStrings[]=leadership')
	results += amazon_parse_jobs(browser, 1)

	result_set = set(map(tuple,results))  #need to convert the inner lists to tuples so they are hashable
	result = map(list,result_set) #Now convert tuples back into lists (maybe unnecessary?)
	update_spreadsheet(result, 'Amazon', 1)

	browser.quit()



def amazon_parse_job_details(url) :
	header = {'User-Agent': 'Mozilla/5.0'}
	request = urllib2.Request(url, headers=header)
	soup = BeautifulSoup(urllib2.urlopen(request).read())
	raw_data = soup.find('div', {'class' : 'row collapse'})
	raw_data['class'] = 'job-details'

	return raw_data


if __name__ == '__main__':

	# amazon_new_jobs()

	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open('Test')
	job_sh = sh.worksheet('Amazon')
	raw_data = job_sh.get_all_values()
	raw_data.pop(0)

	for x, val in enumerate(raw_data) :
		url = val[1]
		# if val[6] == '' :
		if True :
			snippet = amazon_parse_job_details(url)
			print str(x) + '.......' + url
			if snippet is not None :
				for tag in snippet.find_all('a'):
				    tag.replaceWith('')
				for tag in snippet.find_all('script'):
				    tag.replaceWith('')
				job_sh.update_acell('G'+str(x+2), snippet)
				print 'Line No.' + str(x+2) + '.......' + url
			else :
				print 'Line No.' + str(x+2) + '.......Job not found'



# BeautifulSoup parsing strategy -----------------------------------
# header = {'User-Agent': 'Mozilla/5.0'}
# request = urllib2.Request(url, headers=header)
# soup = BeautifulSoup(urllib2.urlopen(request).read())
# raw_data = soup.find('script', {'data-ap' : 'jobs'}).text
# json_dict = json.loads(raw_data)

# print json.dumps(json_dict, indent=4, sort_keys=True)