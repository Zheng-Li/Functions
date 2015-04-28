# -*- coding: utf-8 -*-
import re
import httplib
import urllib2
import HTMLParser
import csv
import socket
import random
import gspread
from geolocation import send_request_by_location
from sql_upload import upload_location
from sql_upload import upload_job
from sql_upload import update_job
import time
from time import sleep
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

WARNING_SIGN = ['illegal', 'apologize', 'sorry','no longer available', 'not found', 'inconvenience', 'no longer posted', 'no longer accepting', 'no vacancy', 'vacancy closed']
URL_SIGN = ['jobvite','icims','taleo', 'jobs.brassring.com']

def login(sheet_name) :
	gs = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gs.open(sheet_name)
	return  sh

def csv_input(csv_file) :
	data_list = []
	csv_reader = csv.reader(open(csv_file, 'rU'))
	for row in csv_reader :
		data_list.append(row)
	return data_list

def csv_output(data_list, csv_file) :
	csv_writer = csv.writer(open(csv_file, 'ab'))
	for row in data_list :
		csv_writer.writerow(row)

def sheet_input(spreadsheet, sheetname) :
	worksheet = spreadsheet.worksheet(sheetname)
	data_list = worksheet.get_all_values()
	data_list.pop(0) # Remove header row 

	# Insert organization name
	for data in data_list :
		if not data[0] :
			data[0] = sheetname
	# csv_output(data_list, 'Backup/'+sheetname+'_backup.csv')
	return data_list

def special_url_check(url) :
	if 'ch.tbe.taleo.net' in url :
		# Oracle taleo site is able to parse
		return False
	for sign in URL_SIGN :
		if sign in url :
			csv_output([[url, sign]], 'Result/'+sign+'.csv')
			return True
	return False 

def keyword_search(site_page, keyword_dict) :
	keyword_tag = []
	
	# Remove HTML tags from page
	re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I)
	re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I | re.M)
	re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)
	re_br=re.compile('<br\s*?/?>')
	re_h=re.compile('</?\w+[^>]*>')
	re_comment=re.compile('<!--[^>]*-->')
	re_special=re.compile('[\xc2]', re.I) # Special character '\xc2'
	s=re_cdata.sub('',site_page)
	s=re_script.sub('',s)
	s=re_style.sub('',s)
	s=re_br.sub('\n',s)
	s=re_h.sub('',s)
	s=re_comment.sub('',s)
	s=re_special.sub(' ',s)
	s=s.lower()
	# print s

	# Find site with WARNING_SIGN
	for sign in WARNING_SIGN :
		if re.search(sign, s) is not None :
			return ['Job Not Found']

	for ky in keyword_dict.keys() :
		ky = ky.strip()
		reg = '\\b' + ky + '\\b'
		result = re.search(reg, s)  
		if result is not None :
			keyword_tag.append(ky)
			keyword_tag += keyword_dict[ky]

	tags = list(set(keyword_tag))
	# tag_set = set(map(tuple,keyword_tag))  #need to convert the inner lists to tuples so they are hashable
	# tags = map(list,tag_set) #Now convert tuples back into lists (maybe unnecessary?)
	return tags

def url_parse(rec, url_col) :
	url = rec[url_col]
	result = []

	# URL header
	if not (url.startswith('http://') or url.startswith('https://')) :
		url = 'http://' + url

	# Rearrage data from spreadsheet
	if url_col == 3 :
		result.append(rec[0]) # Organization name
		result.append(rec[4])
		result.append(url)
		result.append(rec[5])
		result.append(rec[6])
		result.append(rec[7])
		result.append(rec[8])
	elif url_col == 4 :
		result.append(rec[0]) # Organization name
		result.append(rec[5])
		result.append(url)
		result.append(rec[6])
		result.append(rec[7])
		result.append(rec[8])
		result.append(rec[9])
	else :
		result = rec

	if not special_url_check(url) :
		try :
			page = urllib2.urlopen(url, timeout = 10)
			if page.getcode()>300 and page.getcode()!=304:
				result.append(page.getcode())
				csv_output([result], 'Result/Error.csv')
				return result
			tags = ','.join(keyword_search(result[1]+page.read())) # Job Title + Web page
			result.append(tags)
			if 'Warning' in tags :
				csv_output([result], 'Result/Warning.csv')
				return result
			upload_job(result)
			update_job(result)
			csv_output([result], 'Result/Checked.csv')
			sleep(random.uniform(0.1 ,0.3))
		except urllib2.URLError, e:
			result.append('Page error!')
			csv_output([result], 'Result/Error.csv')
		except socket.error, v:
			result.append('Socket error!')
			csv_output([result], 'Result/Error.csv')
		except (IOError, httplib.HTTPException):
			result.append('Unknown error!')  
			csv_output([result], 'Result/Error.csv')
		return result
	else :
		# print 'Special cite'
		return

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

if __name__ == '__main__':
	start_time = time.time()
	keywords = get_keyword_dict()
	records = []
	location = []

	text = ''''''
	print keyword_search(text, keywords)


	# ------------------ Normal sheet input --------------------------
	# sheets = login('Template Standard for New Jobs Upload March 2015')
	# records = sheet_input(sheets, 'Sheet1')
	# records += sheet_input(sheets, 'Sheet2')
	# records += sheet_input(sheets, 'Sheet3')
	# print 'Download....Done'

	# --------------------- Normal location input -----------------------
	# for rec in records :
	# 	location.append([rec[3].strip(), rec[4].strip(), rec[5].strip()])
	# location_set = set(map(tuple,location))  #need to convert the inner lists to tuples so they are hashable
	# location = map(list,location_set) #Now convert tuples back into lists (maybe unnecessary?)
	# for count, x in enumerate(location) :
	# 	# print str(count) + '------'
	# 	result = send_request_by_location(x[0], x[1], x[2])
	# 	upload_location(result)
	# 	# print result

	# ----------- NOT IN USE -------------
	# raw_key = csv_input('keywords.csv')
	# for key in raw_key :
	# 	keywords.append(key[0].lower())
	# print 'Keys....Done'
	# for count, rec in enumerate(records) :
	# 	r = url_parse(rec, 2)		
	# 	if r is not None:
	# 		print str(count) + '---' + r[1] + '...Done'

	# Test url input
	# urls.append('')

	# Double check error
	# recs = csv_input('recheck.csv')
	# for count, rec in enumerate(recs) :
	# 	re_rec = url_parse(rec, 2)
	# 	if re_rec is not None :
	# 		print str(count) + '---' + re_rec[1] + '...Done'

	print("--- %s seconds ---" % (time.time() - start_time))







# --------------------------------- No longer in use -----------------------------
# def url_save(rec):
# 	output_file = 'result.csv'
# 	url_writer = csv.writer(open(output_file, 'ab'))
# 	url_writer.writerow([rec['url'], rec['tag'], rec['error']])

# def url_setup_sheet(sheet) :
# 	worksheet = sheet.worksheet('Copy of CR')
# 	url_list = worksheet.col_values(4)
# 	return url_list

# def keyword_setup_by_keyboard () :
# 	keyword_input = raw_input('What is your keyword setup?\n').split();
# 	keywords = [key.lower() for key in keyword_input]
# 	return keywords

# def url_setup_csv(url_file) :
# 	f = url_file
# 	url_reader = csv.DictReader(open(f, 'rb'))
# 	for row in url_reader :
# 		if url_check(row) :
# 			print 'Skipped ' + row['Organization']
# 		else :
# 			urls.append([row['Organization'], row['internship_url']])