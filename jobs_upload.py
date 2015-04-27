# -*- coding: utf-8 -*-
import requests
import gspread
import time
import urllib2
import re
import MySQLdb
# from bs4 import BeautifulSoup
from geolocation import send_request_by_location
from sql_upload import upload_location
from keyword_search import keyword_search
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def url_check(url) :
	try:
	    r = requests.head(url)
	    return r.status_code
	except requests.ConnectionError:
	    return "Unknown Error"

def get_locations(sh) :
	locations = []
	start_sheet = 0 
	end_sheet = 6
	for i in range(start_sheet, end_sheet) :
		sheet = sh.get_worksheet(i)
		raw_data = sheet.get_all_values()
		raw_data.pop(0)
		for item in raw_data :
			loc = [item[3].strip(), item[4].strip(), item[5].strip()]
			if loc not in locations :
				locations.append(loc)

	result = []
	for item in locations :
		tmp = send_request_by_location(item[0], item[1], item[2])
		result.append(tmp)
		upload_location(tmp)
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

def taleo_sql_upload(spreadsheet_name, worksheet_name) :
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
		if row[7] == 'Job Not Found' :
			continue
		job_sql = '''INSERT INTO zd_new_job(Title, Url, Url_status, Created_on, Expired_on, Org_id, Loc_id, tags, Snippet) SELECT \'{0[0]}\', \'{0[1]}\', 200, CURDATE(), \'{0[5]}\', org1.ID, loc1.ID, \'{0[7]}\', \'{0[6]}\' FROM zd_new_organization AS org1, zd_new_location AS loc1 WHERE org1.Name = \'{1}\' AND loc1.City = \'{0[4]}\' AND loc1.Abbreviation = \'{0[3]}\' AND loc1.Country = \'{0[2]}\' ON DUPLICATE KEY UPDATE Snippet = \'{0[6]}\';'''.format(row, worksheet_name)
		f.write(job_sql + '\n')

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


def tag_parse(spreadsheet_name) :
	sh_list = spreadsheet_name.worksheets()
	keyword_dict = get_keyword_dict()
	# for x in range(0,1) :
			# sh = job_sh.worksheet('GE Captial')
	for sh in sh_list :
		raw_data = sh.get_all_values()
		raw_data.pop(0)
		for x, val in enumerate(raw_data) :
			url = sh.acell('C'+str(x+2)).value
			snippet = sh.acell('I'+str(x+2)).value
			if snippet == '' or not check_job_valid(url, snippet) :
				tags = ['Job Not Found'] 
			else :
				tags = keyword_search(snippet, keyword_dict)
			sh.update_acell('J'+str(x+2), ','.join(tags))
			print 'No.' + str(x) + ', ' + url + '.......Done' 

def sql_parse(spreadsheet_name, worksheet_name, taleo) :
	if taleo :
		taleo_sql_upload(spreadsheet_name, worksheet_name)
	else :
		normal_sql_upload(spreadsheet_name, worksheet_name)


if __name__ == '__main__':
	start_time = time.time()

	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	job_sh = gc.open('Copy of Project 9a')

	# -------------- Step 1: Location parse ------------------
	location_parse(job_sh)
	# -------------- Step 2: Url parse ----------------
	url_parse(job_sh)
	# -------------- Step 3: Snippet parse -----------------
	snippet_parse(job_sh, '') # Pass worksheet name
	# -------------- Step 4: Tag parse ---------------
	tag_parse(job_sh)
	# -------------- Step 5: SQL parse -------------------
	sql_parse(job_sh, '', True)
	sql_parse(job_sh, '', False)

	print("--- %s seconds ---" % (time.time() - start_time))