# -*- coding: utf-8 -*-
import requests
import gspread
import time
import urllib2
import re
import MySQLdb
from bs4 import BeautifulSoup
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
	for i in range(0, 16) :
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
	# -------- Check by URL ------------
	# header = {'User-Agent': 'Mozilla/5.0'}
	# request = urllib2.Request(url,headers=header)
	# page = urllib2.urlopen(request).read()

	# ----------- Check by Text ---------------
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

	# for x in range(1, 235) :
	# 	row = worksheet.row_values(x)
	# 	key = row.pop(0)
	# 	values = filter(None, row)

	return  keywords_dict

def sql_upload(sheet_name) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	job_sh = gc.open(sheet_name)

	for x in range(0, 16) :
		sheet = job_sh.get_worksheet(x)
		data = sheet.get_all_values()
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
			row[8] = MySQLdb.escape_string(row[8].strip())
			row[9] = MySQLdb.escape_string(row[9].strip())
			if row[9] == 'Job Not Found' :
				continue
			# job_sql = '''INSERT INTO zd_new_job(Title, Url, Url_status, Created_on, Expired_on, Org_id, Loc_id, tags, Snippet) SELECT \'{0[1]}\', \'{0[2]}\', 200, CURDATE(), \'{0[6]}\', org1.ID, loc1.ID, \'{0[9]}\', \'{0[8]}\' FROM zd_new_organization AS org1, zd_new_location AS loc1 WHERE org1.Name = \'{0[0]}\' AND loc1.City = \'{0[3]}\' AND loc1.Abbreviation = \'{0[4]}\' AND loc1.Country = \'{0[5]}\' AND NOT EXISTS (SELECT 1 FROM zd_new_job as job WHERE Title = \'{0[1]}\' AND job.Org_id = org1.ID AND job.Loc_id = loc1.ID AND job.Url = \'{0[2]}\');'''.format(row)
			job_sql = '''INSERT INTO zd_new_job(Title, Url, Url_status, Created_on, Expired_on, Org_id, Loc_id, tags, Snippet) SELECT \'{0[1]}\', \'{0[2]}\', 200, CURDATE(), \'{0[6]}\', org1.ID, loc1.ID, \'{0[9]}\', \'{0[8]}\' FROM zd_new_organization AS org1, zd_new_location AS loc1 WHERE org1.Name = \'{0[0]}\' AND loc1.City = \'{0[3]}\' AND loc1.Abbreviation = \'{0[4]}\' AND loc1.Country = \'{0[5]}\' ON DUPLICATE KEY UPDATE Snippet = \'{0[8]}\';'''.format(row)
			print job_sql

if __name__ == '__main__':
	start_time = time.time()

	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	job_sh = gc.open('Project 8 Copy')


	# -------------- Location update ------------------
	# result = get_locations(job_sh)
	# worksheet = job_sh.worksheet("Locations")
	# for x, item in enumerate(result) :
	# 	cell_list = worksheet.range('A'+str(x+1)+':F'+str(x+1))
	# 	for i, val in enumerate(item) :
	# 		cell_list[i].value = val
	# 	worksheet.update_cells(cell_list)


	# -------------- Snippet update -----------------
	# sh = job_sh.worksheet('CGI')
	# header = {'User-Agent': 'Mozilla/5.0'}
	# raw_data = sh.get_all_values()
	# raw_data.pop(0)
	# for x, val in enumerate(raw_data) :
	# # for x in range(26, 85) :
	# 	url = sh.acell('C'+str(x+2)).value
	# 	url_status = sh.acell('H'+str(x+2)).value
	# 	if url_status == '200' :
	# 		request = urllib2.Request(url, headers=header)
	# 		soup = BeautifulSoup(urllib2.urlopen(request).read())
	# 		snippet = soup.find('span', {'class' : 'ProfileInputLabel'})
	# 		if snippet is not None :
	# 			for tag in snippet.find_all('a'):
	# 			    tag.replaceWith('')
	# 			for tag in snippet.find_all('script'):
	# 			    tag.replaceWith('')
	# 			print str(x) + '.......Done' 
	# 			sh.update_acell('I'+str(x+2), snippet)


	# ------------- Url update ----------------
	# sh_list = job_sh.worksheets()
	# for sh in sh_list :
	# 	raw_data = sh.get_all_values()
	# 	raw_data.pop(0)
	# 	for x, val in enumerate(raw_data) :
	# 		url = sh.acell('C'+str(x+2)).value
	# 		status = url_check(url)
	# 		sh.update_acell('H'+str(x+2), status)
	# 		print 'No.' + str(x) + ', ' + title + '.......Done' 


	# -------------- Tag update ---------------
	# sh_list = job_sh.worksheets()
	# keyword_dict = get_keyword_dict()
	# for x in range(0,1) :
	# 	sh = job_sh.worksheet('CGI')
	# # for sh in sh_list :
	# 	raw_data = sh.get_all_values()
	# 	raw_data.pop(0)
	# 	for x, val in enumerate(raw_data) :
	# 		url = sh.acell('C'+str(x+2)).value
	# 		snippet = sh.acell('I'+str(x+2)).value
	# 		if snippet == '' or not check_job_valid(url, snippet) :
	# 			tags = ['Job Not Found'] 
	# 		else :
	# 			tags = keyword_search(snippet, keyword_dict)
	# 		sh.update_acell('J'+str(x+2), ','.join(tags))
	# 		print 'No.' + str(x) + ', ' + url + '.......Done' 

	# --------------- SQL update -------------------
	sql_upload('Project 8 Copy')

	print("--- %s seconds ---" % (time.time() - start_time))