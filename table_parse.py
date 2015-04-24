import re
import httplib
import urllib2
import socket
import HTMLParser
import random
import gspread
import csv
import time
from location_reference import get_abbrevation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from BeautifulSoup import BeautifulSoup
from time import sleep
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

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
	except socket.error, v:
		print 'Socket error!'
	except (IOError, httplib.HTTPException):
		print 'Unknown error!'

def csv_output(data_list, csv_file) :
	csv_writer = csv.writer(open(csv_file, 'ab'))
	for row in data_list :
		csv_writer.writerow(row)

def table_parse(page) :
	data = []

	soup = BeautifulSoup(page)
	table = soup.findChildren('table')[0]

	heads = table.findChildren(['th'])
	rows = table.findChildren(['tr'])

	rows.pop(0) # Pop first row when it is the head

	for row in rows :
		tmp = [] # organized data record
		cells = row.findChildren('td')
		# cells.pop(0) # Pop first cell when there is special flag/symbol/space
		for cell in cells :
			if cell.string is not None :
				value = cell.string
				value = value.replace('\\n\\t', '')
				value = value.replace('\\n', '')
				value = value.strip()
				tmp.append(value)
			else :
				value = cell.findChildren('a')[0].string
				value = value.replace('\\n\\t', '')
				value = value.replace('\\n', '')
				value = value.strip()
				tmp.append(value)
				url = cell.find('a').get('href')
				tmp.append(url)
		data.append(tmp)
	return data

def update_spreadsheet(data, sheet_name, loc) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')

	# sh = gc.open('Zheng Brass Rings Jobs to upload March 2015')
	# worksheet = sh.add_worksheet(title="bayer", rows="200", cols="20")
	# worksheet = sh.worksheet('bayer')

	sh = gc.open('Test')
	worksheet = sh.worksheet(sheet_name)

	for x, row in enumerate(data) :
		num = x + 2 + 25*(loc-1)
		cell_list = worksheet.range('A'+str(num)+':F'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)

# ------------- Intel ----------------
# def parse_javascript(url, page) :
# 		browser = webdriver.Firefox()
# 		browser.get(url)

# 		for i in range(1, page) :
# 			pager = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "jobPager")))
# 			button = pager.find_elements_by_tag_name("span")[3].find_element_by_tag_name("span").find_element_by_tag_name("a")
# 			button.click()

# 		records = []
# 		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "searchresults")))
# 		table = browser.find_elements_by_tag_name("table")[2].find_element_by_tag_name("tbody")
# 		jobs = table.find_elements_by_tag_name("tr")
# 		for j in jobs:
# 			job_title = j.find_elements_by_tag_name("td")[1].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("a").text
# 			job_url = j.find_elements_by_tag_name("td")[1].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("a").get_attribute("href")
# 			job_location = j.find_elements_by_tag_name("td")[2].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("span").text
# 			job_posted = j.find_elements_by_tag_name("td")[3].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("span").text
# 			record = [job_title, job_url] + intel_location(job_location) +  [job_posted]
# 			records.append(record)
# 			print record

# 		update_spreadsheet(records, 'Intel', page)
# 		csv_output(records, 'Result/intel.csv')
# 		browser.quit()

def intel_location(location) :
	if location == 'Multiple Locations' :
		return ['','','']
	elif location == 'Israel--':
		return ['Israel','','']
	else :
		loc = re.split('-|, ', location)
		country = loc[0]
		if len(loc) < 2 or 'USA' not in location:
			state = ''
		else : 
			state = get_abbrevation(loc[1])
			if state is None :
				state = ''
		if len(loc) < 3 :
			city = ''
		else :
			city = loc[2]
		return [country, state, city]


# ---------------- Fidelity ------------------
def parse_javascript(url, page) :
		browser = webdriver.Firefox()
		browser.get(url)

		for i in range(1, page) :
			pager = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, "jobPager")))
			button = pager.find_elements_by_tag_name("span")[3].find_element_by_tag_name("span").find_element_by_tag_name("a")
			button.click()

		records = []
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "tr")))
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

		update_spreadsheet(records, 'Fidelity', page)
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


if __name__ == '__main__':
	start_time = time.time()

	# url = 'https://career.bayer.com/en/career/job-search/?accessLevel=student&functional_area=&country=*&location=&company=&fulltext='
	# result = table_parse(page)

	# url = 'https://intel.taleo.net/careersection/10000/jobsearch.ftl'
	url = 'https://fidelity.taleo.net/careersection/10020/jobsearch.ftl'
	page = url_parse(url)

	# ------------- Taleo Site Table parse ---------------
	# parse_javascript(url, 10) # Certain page
	# for i in range(9, 10) :
	# 	parse_javascript(url, i)

	print("--- %s seconds ---" % (time.time() - start_time))
	


