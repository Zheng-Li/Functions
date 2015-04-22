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
	    return "failed to connect"

def get_locations(sh) :
	locations = []
	for i in range(0, 9) :
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

def check_job_valid(url) :
	header = {'User-Agent': 'Mozilla/5.0'}
	request = urllib2.Request(url,headers=header)
	page = urllib2.urlopen(request).read()

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

def get_keyword_lib() :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	key_sh = gc.open('Keywords for Python Parsing for Job Tags')
	sh_list = key_sh.worksheets()
	raw_keys = []
	keywords = []
	result = []
	for s in sh_list : 
		raw_keys += s.get_all_values()

	for key in raw_keys :
		if key[0] not in keywords :
			keywords.append(key[0])

	for k in keywords :
		result.append(k.lower())
	return result

def sql_upload() :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	job_sh = gc.open('Zheng: Jobs for Upload: April 17_2015_Project7')

	for x in range(0, 9) :
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
	job_sh = gc.open('Zheng: Jobs for Upload: April 17_2015_Project7')

	# sh_list = job_sh.worksheets()
	# keyword_lib = get_keyword_lib()
	# # print keyword_lib
	# for sh in sh_list :
	# 	raw_data = sh.get_all_values()
	# 	raw_data.pop(0)
	# 	for x, val in enumerate(raw_data) :
	# 		title = sh.acell('B'+str(x+2)).value
	# 		url = sh.acell('C'+str(x+2)).value
	# 		# status = url_check(url)
	# 		snippet = sh.acell('I'+str(x+2)).value
	# 		if not check_job_valid(url):
	# 			tags = ['Job Not Found'] 
	# 		else :
	# 			text = title + snippet 
	# 			tags = keyword_search(text, keyword_lib)
	# 		print 'No.' + str(x) + ' ,' +  url + '.......' + ','.join(tags)
	# 		# sh.update_acell('H'+str(x+2), status)
	# 		sh.update_acell('J'+str(x+2), ','.join(tags))

	sql_upload()
	# sh = job_sh.worksheet('Orbital ATK Inc.')

	# header = {'User-Agent': 'Mozilla/5.0'}
	# raw_data = sh.get_all_values()
	# raw_data.pop(0)
	# for x, val in enumerate(raw_data) :
	# 	url = sh.acell('C'+str(x+2)).value
	# 	request = urllib2.Request(url, headers=header)
	# 	soup = BeautifulSoup(urllib2.urlopen(request).read())
	# 	snippet = soup.find('span', {'itemprop' : 'description'})
	# 	if snippet is not None :
	# 	# [a.extract() for a in snippet('a')]
	# 	# [s.extract() for s in snippet('script')]
	# 		for tag in snippet.find_all('a'):
	# 		    tag.replaceWith('')
	# 		for tag in snippet.find_all('script'):
	# 		    tag.replaceWith('')
	# 		print str(x) + '.......' + snippet.text
	# 		sh.update_acell('I'+str(x+2), snippet)



	# -------------- Location check ------------------
	# result = get_locations(job_sh)
	# worksheet = job_sh.worksheet("Locations")
	# for x, item in enumerate(result) :
	# 	cell_list = worksheet.range('A'+str(x+1)+':F'+str(x+1))
	# 	for i, val in enumerate(item) :
	# 		cell_list[i].value = val
	# 	worksheet.update_cells(cell_list)

	# ------------- Keyword check -----------------
	# keyword_lib = get_keyword_lib()
	# snippet = ''''''
	# tags = keyword_search(snippet, keyword_lib)
	# print ','.join(tags)	


	print("--- %s seconds ---" % (time.time() - start_time))