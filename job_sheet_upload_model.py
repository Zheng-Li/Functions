# -*- coding: utf-8 -*-
import requests
import gspread
import time
import socket
import httplib 
import urllib2
import json
import re
import MySQLdb
from bs4 import BeautifulSoup
from oauth2client.client import SignedJwtAssertionCredentials
from Geolocation.geolocation import send_request_by_location
from SQL.sql_translate import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from time import sleep
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def login(credentials_file, spreadsheet, worksheet) :
	json_key = json.load(open(credentials_file))
	scope = ['https://spreadsheets.google.com/feeds']

	credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
	gc = gspread.authorize(credentials)
	ws = gc.open(spreadsheet).worksheet(worksheet)

	return ws

def check_url_status(url) :
	try :
		page = urllib2.urlopen(url, timeout = 10)
		if page.getcode()>300 and page.getcode()!=304:
			print 'Error:' + page.getcode()
			return False
		print 'Correct Response Code: ' + page.getcode()
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


def download_location_list(worksheet) :
	data_list = worksheet.get_all_values()
	del data_list[0] # Spreadsheet Header

	location_list = []
	for row in data_list :
		# ---------- Location format <City, Abbr, Country> -------------
		loc = [row[2].strip(), row[3].strip(), row[4].strip()]
		location_list.append(loc)
	location_set = set(map(tuple,location_list))  #need to convert the inner lists to tuples so they are hashable
	locations = map(list,location_set) #Now convert tuples back into lists (maybe unnecessary?)

	result = []
	for item in locations :
		tmp = send_request_by_location(item[0], item[1], item[2])
		result.append(tmp)
		print tmp
	return result


def parse_job_details(browser, url, target) :
	browser.get(url)
	try :
		snippet = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, target))).get_attribute('innerHTML')
		return snippet
	except StaleElementReferenceException:
		print 'Selenium Error!'
		return
	except TimeoutException:
		print 'Timeout Error!'
		return


def upload_jobs(worksheet, company, target) :
	f = open('Result/'+ company + '.sql', 'a')
	browser = webdriver.Firefox()

	data = worksheet.get_all_values()
	data.pop(0)
	
	for row in data :
		row[0] = MySQLdb.escape_string(row[0].strip())
		row[1] = MySQLdb.escape_string(row[1].strip())
		row[2] = MySQLdb.escape_string(row[2].strip())
		row[3] = MySQLdb.escape_string(row[3].strip())
		row[4] = MySQLdb.escape_string(row[4].strip())
		row[6] = MySQLdb.escape_string(row[6].strip())

		# check_url_status(row[1].strip())
		snippet = parse_job_details(browser, row[1].strip(), target)

		if snippet :

			re_img = re.compile('<img\\b[^>]*>.*?>')
			snippet = re_img.sub('', snippet)

			re_href = re.compile('<a\\b[^>]*>.*?<\\/a>')
			snippet = re_href.sub('', snippet)

			re_input = re.compile('<input\\b[^>]*>.*?>')
			snippet = re_input.sub('', snippet)

			re_iframe = re.compile('<iframe\\b[^>]*>.*?<\\/a>')
			snippet = re_iframe.sub('', snippet)

			row[5] = MySQLdb.escape_string(snippet)
		else :
			continue

		if row[6] == 'Experienced' or row[6] == '':
			continue

		job_sql = '''INSERT INTO zd_new_job(Title, Url, Url_status, Created_on, Org_id, Loc_id, Snippet, tags) SELECT \'{0[0]}\', \'{0[1]}\', 200, CURDATE(), org1.ID, loc1.ID, \'{0[5]}\', \'{0[6]}\' FROM zd_new_organization AS org1, zd_new_location AS loc1 WHERE org1.Name = \'{1}\' AND loc1.City = \'{0[2]}\' AND loc1.Abbreviation = \'{0[3]}\' AND loc1.Country = \'{0[4]}\' ON DUPLICATE KEY UPDATE Snippet = \'{0[5]}\', tags = \'{0[6]}\';'''.format(row, company)
		print job_sql
		f.write(job_sql + '\n')

	browser.quit()
	f.close()


if __name__ == '__main__':
	start_time = time.time()

	spreadsheet_name = ''
	worksheet_name = ''
	credentials_file = 'zheng-6cef143e8ce1.json'
	worksheet = login(credentials_file, spreadsheet_name, worksheet_name)

	# -------------- Step 1: Location parse (with SQL) <City, State, Abbr, Country, Latitude, Longitude> ------------------
	loc_list = download_location_list(worksheet)
	for loc in loc_list :
		upload_location(loc)

	# -------------- Step 2: Snippet parse (with SQL) -----------------
	company_name = worksheet_name
	target_path = ''  
	upload_jobs(worksheet, company_name, target_path)


	print("--- %s seconds ---" % (time.time() - start_time))



