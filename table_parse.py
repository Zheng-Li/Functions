import re
import httplib
import urllib2
import socket
import HTMLParser
import random
import gspread
from selenium import webdriver
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

def update_spreadsheet(data) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')

	# sh = gc.open('Zheng Brass Rings Jobs to upload March 2015')
	# worksheet = sh.add_worksheet(title="bayer", rows="200", cols="20")
	# worksheet = sh.worksheet('bayer')

	sh = gc.open('Test')
	worksheet = sh.worksheet('Intel')
	

	# Header
	# cell_list = worksheet.range('A1:E1')
	# cell_values = ['Job Title', 'Job Url', 'Posted on', 'Country', 'State-City']
	# for i, val in enumerate(cell_values):  #gives us a tuple of an index and value
	#     cell_list[i].value = val    #use the index on cell_list and the val from cell_values
	# worksheet.update_cells(cell_list)

	# Data
	for x, row in enumerate(data) :
		num = x+2
		cell_list = worksheet.range('A'+str(num)+':D'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)

def parse_javascript(url, page) :
	# soup = BeautifulSoup(page) 
	# js  = soup.findAll("script")
	# for j in js :
	# 	ss = j.prettify()
	# 	print ss

	browser = webdriver.Firefox()
	browser.get(url)
	for x in range(1, page) :
		button = browser.find_element_by_id("jobPager").find_elements_by_tag_name("span")[3].find_element_by_tag_name("span").find_element_by_tag_name("a")
		print button.get_attribute("class")
		button.click()
	browser.implicitly_wait(5)
	table = browser.find_elements_by_tag_name("table")[2]

	# header = []
	# headers = table.find_element_by_tag_name("thead").find_element_by_tag_name("tr").find_elements_by_tag_name("th")
	# for h in headers :
	# 	tmp = h.text
	# 	header.append(tmp)
	# print head

	records = []
	jobs = table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
	for j in jobs:
		title = j.find_elements_by_tag_name("td")[1].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("a").text
		url = j.find_elements_by_tag_name("td")[1].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("a").get_attribute("href")
		location = j.find_elements_by_tag_name("td")[2].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("span").text
		posted = j.find_elements_by_tag_name("td")[3].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("span").text
		record = [title, url, location, posted]
		records.append(record)
		print record

	browser.quit()
	return records

if __name__ == '__main__':
	# url = 'https://career.bayer.com/en/career/job-search/?accessLevel=student&functional_area=&country=*&location=&company=&fulltext='
	url = 'https://intel.taleo.net/careersection/10000/jobsearch.ftl'
	
	page = url_parse(url)
	data = []
	for i in range (1, 11) :
		data += parse_javascript(url, i)
	# result = table_parse(page)
	update_spreadsheet(data)


