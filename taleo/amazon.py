# -*- coding: utf-8 -*-
import re
import urllib2
import socket
import httplib
import json
import gspread
# from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
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
		num = x + 2 + 30*(loc-1)
		cell_list = worksheet.range('A'+str(num)+':E'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)


def parse_job_data(browser, p) :
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


if __name__ == '__main__':
	url = 'http://www.amazon.jobs/results?searchStrings[]=intern'
	# url = 'http://www.amazon.jobs/results?searchStrings[]=leadership'
	# url = 'http://www.amazon.jobs/results?searchStrings[]=MBA'

	browser = webdriver.Firefox()
	browser.get(url)

	# -------------- Jump to page 28 -------------------
	# for x in range (0, 27) :
	# 	button = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.LINK_TEXT, 'Next')))
	# 	button.click()

	results = []

	for p in range (1, 4) :
		if p != 1 :
			button = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.LINK_TEXT, 'Next')))
			button.click()
		results += parse_job_data(browser, p)

	browser.get('http://www.amazon.jobs/results?searchStrings[]=MBA')
	results += parse_job_data(browser, 1)

	result_set = set(map(tuple,results))  #need to convert the inner lists to tuples so they are hashable
	result = map(list,result_set) #Now convert tuples back into lists (maybe unnecessary?)
	update_spreadsheet(result, 'Amazon', 1)

	browser.quit()




# -----------------------------------
# header = {'User-Agent': 'Mozilla/5.0'}
# request = urllib2.Request(url, headers=header)
# soup = BeautifulSoup(urllib2.urlopen(request).read())
# raw_data = soup.find('script', {'data-ap' : 'jobs'}).text
# json_dict = json.loads(raw_data)

# print json.dumps(json_dict, indent=4, sort_keys=True)