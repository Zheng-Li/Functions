# -*- coding: utf-8 -*-
import re
import httplib
import urllib2
import socket
import HTMLParser
import random
import gspread
import csv
import time
# from Geolocation.geolocation import *
# from sql_upload import upload_location
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from time import sleep
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def login(spreadsheet) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open(spreadsheet)
	return sh

# ----------- Regular site table parse -----------------
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

		if tmp[3] == 'United States' :
			country = 'USA'
		else :
			country = tmp[3]
		data.append([tmp[0], tmp[1]] + location_parse(tmp[4]) + [country, tmp[2]])
	return data

def location_parse(raw) :
	loc = re.split('-', raw) 
	l = []
	if len(loc) == 1 :
		l = [loc[0], '']
	else :
		l = [loc[1], loc[0]]	
	return l




def csv_output(data_list, csv_file) :
	csv_writer = csv.writer(open(csv_file, 'ab'))
	for row in data_list :
		csv_writer.writerow(row)

# ------------- Taleo sheet update --------------
def update_spreadsheet(data, sheet_name, loc) :
	sheet = login('Test')
	worksheet = sheet.worksheet(sheet_name)

	for x, row in enumerate(data) :
		num = x + 2 + 25*(loc-1)
		cell_list = worksheet.range('A'+str(num)+':F'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)



# ------------- Selenium Wait ----------------- unfinished
# def click_through_to_new_page(link_loc):
#     link = browser.find_element_by_class_name(link_loc).find_elements_by_tag_name("a")[-1]
#     link.click()

#     def link_has_gone_stale():
#         try:
#             # poll the link with an arbitrary call
#             link.find_elements_by_id('what?') 
#             return False
#         except StaleElementReferenceException:
#             return True

#     wait_for(link_has_gone_stale)

# def wait_for(condition_function):
#     start_time = time.time()
#     while time.time() < start_time + 10:
#         if condition_function():
#             return True
#         else:
#             time.sleep(0.1)
#     raise Exception(
#         'Timeout waiting for {}'.format(condition_function.__name__)
#     )


# ----------- Taleo detail page --------------
def parse_job_detail(browser, url) :

	browser.get(url)
	try :
		job_data = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'editablesection')))
		job_data = job_data.get_attribute('innerHTML')
		soup = BeautifulSoup(job_data)
		trimed_data =  soup.find_all('div', {'class' : 'contentlinepanel'})[:3]
		result = ''.join(str(tag) for tag in trimed_data)

		# result = job_data

		# # ------------ Test for Multiple locations ---------------
		# trimed_data = soup.find('span', {'id' : 'requisitionDescriptionInterface.ID1790.row1'})
		# result = intel_location(trimed_data.string)

		return result
	except StaleElementReferenceException:
		return
	except TimeoutException:
		return


def intel_location(location) :
	if location == 'Multiple Locations' :
		return ['','','']
	elif location == 'Israel--':
		return ['','','Israel']
	else :
		loc = re.split('-|, ', location)
		if loc[0] == 'United Arab Emirates' :
			country = 'UAE'
		elif loc[0] == 'Russian Federation' :
			country = 'Russia'
		elif loc[0] == 'United Kingdom' :
			country = 'UK'
		elif loc[0] == 'Viet Nam' :
			country = 'Vietnam'
		else :
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
		return [city, state, country]



# ----------- Taleo location sheet --------------
def update_location_from_sheet(spreadsheet, start, end) :
	worksheet = spreadsheet.worksheet('Locations')
	locations = []
	for i in range(start, end+1) :
		sheet = spreadsheet.get_worksheet(i)
		raw_data = sheet.get_all_values()
		raw_data.pop(0)
		for item in raw_data :
			loc = [item[4].strip(), item[3].strip(), item[2].strip()]
			locations.append(loc)
	location_set = set(map(tuple,locations))  #need to convert the inner lists to tuples so they are hashable
	locations = map(list,location_set) #Now convert tuples back into lists (maybe unnecessary?)

	result = []
	for item in locations :
		tmp = send_request_by_location(item[0], item[1], item[2])
		result.append(tmp)
		print tmp

	for x, row in enumerate(result) :
		num = x+1
		cell_list = worksheet.range('A'+str(num)+':F'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)
	

# def update_location_sheet() :
# 	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
# 	sh = gc.open('Test')

# 	worksheet = sh.worksheet('Location')
# 	raw_data = worksheet.get_all_values()

# 	worksheet = sh.worksheet('Location')
# 	for i in range(138, 209) :
# 		city = worksheet.acell('A' + str(i)).value
# 		abbr = worksheet.acell('C' + str(i)).value
# 		country = worksheet.acell('D' + str(i)).value
		
# 		tmp = send_request_by_location(city, abbr, country)
# 		worksheet.update_acell('B' + str(i), tmp[1])
# 		worksheet.update_acell('E' + str(i), tmp[4])
# 		worksheet.update_acell('F' + str(i), tmp[5])
# 		sql = '''INSERT INTO zd_new_location(City, State, Abbreviation, Country, Latitude, Longitude) VALUES (\'{0[0]}\', \'{0[1]}\', \'{0[2]}\', \'{0[3]}\', {1}, {2}) ON DUPLICATE KEY UPDATE State = VALUES(State), Latitude = VALUES(Latitude), Longitude = VALUES(Longitude);'''.format(tmp, float(tmp[4]), float(tmp[5]))
# 		print sql


if __name__ == '__main__':
	start_time = time.time()

	# ----------- Regular Site ------------
	# url = 'https://career.bayer.com/en/career/job-search/?accessLevel=student&functional_area=&country=*&location=&company=&fulltext='
	# page = url_parse(url)
	# result = table_parse(page)
	# update_spreadsheet(result, 'Bayer AG', 1)

	# ------------- Taleo Job Details ---------------
	job_sh = login('Test')
	sh = job_sh.worksheet('Fidelity_Intern')
	raw_data = sh.get_all_values()
	raw_data.pop(0)

	browser = webdriver.Firefox()
	for x, val in enumerate(raw_data) :
		url = val[1]
		if val[6] == '' :
			snippet = parse_job_detail(browser, url)
			# print str(x) + '.......' + url
			if snippet is not None :
				sh.update_acell('G'+str(x+2), snippet)
				print 'Line No.' + str(x+2) + '.......' + url
			else :
				print 'Line No.' + str(x+2) + '.......Job not found'
	browser.quit() 

	# ------------------ Test for Multilocation -----------------
	# job_sh = login('Test')
	# sh = job_sh.worksheet('Intel_Intern')
	# raw_data = sh.get_all_values()
	# raw_data.pop(0)

	# browser = webdriver.Firefox()
	# for x, val in enumerate(raw_data) :
	# 	url = val[1]
	# 	if val[4] == '' :
	# 		loc = parse_job_detail(browser, url)
	# 		sh.update_acell('C'+str(x+2), loc[0])
	# 		sh.update_acell('D'+str(x+2), loc[1])
	# 		sh.update_acell('E'+str(x+2), loc[2])
	# 		print 'Line No.' + str(x+2) + ','.join(loc)

	# browser.quit() 



	# -------------- Taleo Location -------------
	# spreadsheet = login('Test')
	# update_location_from_sheet(spreadsheet, 0, 1)
	# worksheet = spreadsheet.worksheet('Locations')
	# data = worksheet.get_all_values()
	# for x, val in enumerate(data) :
	# 	upload_location(val)

	print("--- %s seconds ---" % (time.time() - start_time))
	


