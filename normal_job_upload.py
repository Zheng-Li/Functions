# -*- coding: utf-8 -*-
import requests
import gspread
import time
import urllib2
import json
import re
import MySQLdb
# from bs4 import BeautifulSoup
from oauth2client.client import SignedJwtAssertionCredentials
from Geolocation.geolocation import send_request_by_location
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from sql_upload import upload_location
from keyword_search import keyword_search
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def login(spreadsheet, worksheet) :
	json_key = json.load(open('zheng-6cef143e8ce1.json'))
	scope = ['https://spreadsheets.google.com/feeds']

	credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
	gc = gspread.authorize(credentials)
	ws = gc.open(spreadsheet).worksheet(worksheet)

	return ws

def url_check(url) :
	try:
	    r = requests.head(url)
	    return r.status_code
	except requests.ConnectionError:
	    return "Unknown Error"

def get_locations(sh, worksheet) :
	locations = []
	# start_sheet = 0 
	# end_sheet = 6
	# for i in range(start_sheet, end_sheet) :
		# sheet = sh.get_worksheet(i)
	sheet = sh.worksheet(worksheet)
	for i in range(0, 1) :	
		raw_data = sheet.get_all_values()
		raw_data.pop(0)
		for item in raw_data :
			loc = [item[2].strip(), item[3].strip(), item[4].strip()]
			if loc not in locations :
				locations.append(loc)

	result = []
	for item in locations :
		tmp = send_request_by_location(item[0], item[1], item[2])
		result.append(tmp)
		print tmp
		upload_location(tmp)
		print tmp
	return result

def check_job_valid(url, text) :
	# -------- Check URL ------------
	header = {'User-Agent': 'Mozilla/5.0'}
	request = requests.get(url,headers=header)
	status = request.status_code
	if status != 200:
		print status_code
		return False

	# ----------- Check Text ---------------
	page = text 
	re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I)
	re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I | re.M)
	re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)
	re_br=re.compile('<br\s*?/?>')
	re_h=re.compile('</?\w+[^>]*>')
	re_comment=re.compile('<!--[^>]*-->')
	s=re_cdata.sub('',page)
	s=re_script.sub('',s)
	s=re_style.sub('',s)
	s=re_br.sub('\n',s)
	s=re_h.sub('',s)
	s=re_comment.sub('',s)
	s=s.lower()
	# print s

	# Find site with WARNING_SIGN
	WARNING_SIGN = ['illegal', 'apologize', 'sorry','no longer available', 'not found', 'inconvenience', 'no longer posted', 'no longer accepting', 'no vacancy', 'vacancy closed']
	for sign in WARNING_SIGN :
		if re.search(sign, s) is not None :
			return False 

	return True

def get_keyword_dict() :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	key_sh = gc.open('Test Project')
	worksheet = key_sh.worksheet('Keywords Python Parsing Job Tags April22')

	keywords_dict = {}

	raw = worksheet.get_all_values()
	for row in raw :
		key = row.pop(0).lower()
		values = filter(None, row)
		keywords_dict[key] = [x.lower() for x in values]

	return  keywords_dict

def normal_sql_upload(spreadsheet_name, worksheet_name) :
	f = open('Result/'+ worksheet_name + '.sql', 'a')
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	job_sh = gc.open(spreadsheet_name)

	worksheet = job_sh.worksheet(worksheet_name)
	data = worksheet.get_all_values()
	data.pop(0)
	for row in data :
		row[0] = MySQLdb.escape_string(row[0].strip())
		row[1] = MySQLdb.escape_string(row[1].strip())
		row[2] = MySQLdb.escape_string(row[2].strip())
		row[3] = MySQLdb.escape_string(row[3].strip())
		row[4] = MySQLdb.escape_string(row[4].strip())
		row[5] = MySQLdb.escape_string(row[5].strip())
		row[6] = MySQLdb.escape_string(row[6].strip())
		row[7] = MySQLdb.escape_string(row[7].strip())
		row[8] = MySQLdb.escape_string(row[7].strip())
		row[9] = MySQLdb.escape_string(row[7].strip())
		if row[9] == 'Job Not Found' :
			continue
		job_sql = '''INSERT INTO zd_new_job(Title, Url, Url_status, Created_on, Expired_on, Org_id, Loc_id, tags, Snippet) SELECT \'{0[1]}\', \'{0[2]}\', 200, CURDATE(), \'{0[6]}\', org1.ID, loc1.ID, \'{0[9]}\', \'{0[8]}\' FROM zd_new_organization AS org1, zd_new_location AS loc1 WHERE org1.Name = \'{0[0]}\' AND loc1.City = \'{0[3]}\' AND loc1.Abbreviation = \'{0[4]}\' AND loc1.Country = \'{0[5]}\' ON DUPLICATE KEY UPDATE Snippet = \'{0[8]}\';'''.format(row)
		f.write(job_sql + '\n')

def parse_job_details(browser, url) :
	browser.get(url)
	try :
		if 'brassring' in url :
			snippet = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ProgressBar"]/table/tbody/tr[2]/td/table[4]')))
			snippet = '<table width="92%" border="0" cellpadding="3" cellspacing="0" align="center" role="presentation">' + \
						snippet.get_attribute('innerHTML') + \
						'</table>'
		elif 'appone' in url :
			snippet = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="JobDescription"]')))
			snippet = '<table width="100%" cellpadding="3" id="JobDescription">' + \
						snippet.get_attribute('innerHTML') + \
						'</table>'
		else :
			snippet = ''
		
		re_img = re.compile('<img.*?>')
		snippet = re_img.sub('', snippet)
		print snippet
		return snippet 
	except StaleElementReferenceException:
		print 'Selenium Error!'
		return
	except TimeoutException:
		print 'Timeout Error!'
		return


def taleo_sql_upload(worksheet, company) :
	f = open('Result/'+ company + '.sql', 'a')
	data = worksheet.get_all_values()
	data.pop(0)
	browser = webdriver.Firefox()
	for row in data :
		row[0] = MySQLdb.escape_string(row[0].strip())
		row[1] = MySQLdb.escape_string(row[1].strip())
		row[2] = MySQLdb.escape_string(row[2].strip())
		row[3] = MySQLdb.escape_string(row[3].strip())
		row[4] = MySQLdb.escape_string(row[4].strip())

		# Job snippet from worksheet
		# row[5] = MySQLdb.escape_string(row[5].strip()) 
		# Job snippet from live site
		snippet = parse_job_details(browser, row[1].strip())
		if snippet :
			row[5] = MySQLdb.escape_string(snippet)
		else :
			continue

		row[6] = MySQLdb.escape_string(row[6].strip())
		if row[6] == 'Experienced' or row[6] == '':
			continue
		job_sql = '''INSERT INTO zd_new_job(Title, Url, Url_status, Created_on, Org_id, Loc_id, tags, Snippet) SELECT \'{0[0]}\', \'{0[1]}\', 200, CURDATE(), org1.ID, loc1.ID, \'{0[6]}\', \'{0[5]}\' FROM zd_new_organization AS org1, zd_new_location AS loc1 WHERE org1.Name = \'{1}\' AND loc1.City = \'{0[2]}\' AND loc1.Abbreviation = \'{0[3]}\' AND loc1.Country = \'{0[4]}\' ON DUPLICATE KEY UPDATE Snippet = \'{0[5]}\', tags = \'{0[6]}\';'''.format(row, company)
		print job_sql
		f.write(job_sql + '\n')

	browser.quit()
	f.close()

def location_parse(spreadsheet_name) :
	result = get_locations(spreadsheet_name)
	worksheet = spreadsheet_name.worksheet("Locations")
	for x, item in enumerate(result) :
		cell_list = worksheet.range('A'+str(x+1)+':F'+str(x+1))
		for i, val in enumerate(item) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)

def url_parse(spreadsheet_name) :
	sh_list = spreadsheet_name.worksheets()
	for sh in sh_list :
		raw_data = sh.get_all_values()
		raw_data.pop(0)
		for x, val in enumerate(raw_data) :
			title = sh.acell('B'+str(x+2)).value
			url = sh.acell('C'+str(x+2)).value
			status = url_check(url)
			sh.update_acell('H'+str(x+2), status)
			print 'No.' + str(x) + ', ' + title + '.......' + str(status) 

def snippet_parse(spreadsheet_name, worksheet_name) :
	tag = ''
	attribute = ''
	value = ''
	sh = spreadsheet_name.worksheet(worksheet_name)
	header = {'User-Agent': 'Mozilla/5.0'}
	raw_data = sh.get_all_values()
	raw_data.pop(0)
	for x, val in enumerate(raw_data) :
	# for x in range(26, 85) :
		url = sh.acell('C'+str(x+2)).value
		url_status = sh.acell('H'+str(x+2)).value
		if url_status == '200' :
			request = urllib2.Request(url, headers=header)
			soup = BeautifulSoup(urllib2.urlopen(request).read())
			snippet = soup.find(tag, {attrbute : value})
			if snippet is not None :
				for tag in snippet.find_all('a'):
				    tag.replaceWith('')
				for tag in snippet.find_all('script'):
				    tag.replaceWith('')
				print str(x) + '.......Done' 
				sh.update_acell('I'+str(x+2), snippet)


def tag_parse(spreadsheet, worksheet_name) :
	sh_list = spreadsheet.worksheets()
	keyword_dict = get_keyword_dict()
	for x in range(0,1) :
		sh = job_sh.worksheet(worksheet_name)
	# for sh in sh_list :
		raw_data = sh.get_all_values()
		raw_data.pop(0)
		for x, val in enumerate(raw_data) :
			# url = val[2]
			# snippet = val[8]
			# if snippet == '' or not check_job_valid(url, snippet) :
			# 	tags = ['Job Not Found'] 
			# else :
			# 	tags = keyword_search(snippet, keyword_dict)
			# sh.update_acell('J'+str(x+2), ','.join(tags))
			# print 'No.' + str(x) + ', ' + url + '.......Done' 

			snippet = val[6]
			# tags = val[7]
			if snippet == '' :
				tags = ['Job Not Found']
			else :
				tags = keyword_search(snippet, keyword_dict)
			sh.update_acell('H'+str(x+2), ','.join(tags))
			print 'No.' + str(x+2) + ' Line: ' + '........Done'

			# Double check tag parsing 
			# if tags != '' :
			# 	continue
			# else :
			# 	tags = keyword_search(snippet, keyword_dict)
			# 	print 'No.' + str(x+2) + ' Line: ' + ','.join(tags)
			


def sql_parse(spreadsheet_name, worksheet_name, company, taleo) :
	if taleo :
		taleo_sql_upload(spreadsheet_name, worksheet_name, company)
	else :
		normal_sql_upload(spreadsheet_name, worksheet_name, company)


if __name__ == '__main__':
	start_time = time.time()
	spreadsheet_name = 'Organization Parsing New Companies from Carol_May2015'
	worksheet_name = 'Copy of Test'

	# -------------- Step 1: Location parse ------------------
	# location_parse(job_sh)
	# get_locations(job_sh, 'BASF Corporation')

	# -------------- Step 2: Url parse ----------------
	# url_parse(job_sh)

	# -------------- Step 3: Snippet parse -----------------
	# snippet_parse(job_sh, 'Associated Bank (Associated Banc-Corp)') # Pass worksheet Name

	# -------------- Step 4: Tag parse ---------------
	# tag_parse(job_sh, 'Adobe_global')

	# -------------- Step 5: SQL parse -------------------
	# sql_parse('Test', 'BASF Corporation', 'BASF Corporation' ,True)
	# sql_parse(job_sh, '', False)
	
	worksheet = login(spreadsheet_name, worksheet_name)
	taleo_sql_upload(worksheet, 'FedEx Corporation (FedEx)')

	print("--- %s seconds ---" % (time.time() - start_time))