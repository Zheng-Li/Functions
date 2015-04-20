import requests
import gspread
import time
import urllib2
import re
from BeautifulSoup import BeautifulSoup
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

if __name__ == '__main__':
	start_time = time.time()

	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	job_sh = gc.open('Zheng: Jobs for Upload: April 17_2015_Project7')
	# worksheet = job_sh.worksheet('Accor')
	# worksheet = job_sh.worksheet('Acne Studios')
	# worksheet = job_sh.worksheet('Acxiom')
	# worksheet = job_sh.worksheet('Airbnb, Inc.')
	# worksheet = job_sh.worksheet('American Rivers')
	# worksheet = job_sh.worksheet('Associated Bank')
	# worksheet = job_sh.worksheet('Amnesty International')
	# worksheet = job_sh.worksheet('Baxter International Inc.')
	# worksheet = job_sh.worksheet('Orbital ATK Inc.')

	sh_list = job_sh.worksheets()
	keyword_lib = get_keyword_lib()
	# print keyword_lib
	for sh in sh_list :
		raw_data = sh.get_all_values()
		raw_data.pop(0)
		for x, val in enumerate(raw_data) :
			title = sh.acell('B'+str(x+2)).value
			url = sh.acell('C'+str(x+2)).value
			# status = url_check(url)
			snippet = sh.acell('I'+str(x+2)).value
			if not check_job_valid(url):
				tags = 'Job Not Found' 
			else :
				text = title + snippet 
				tags = keyword_search(title, keyword_lib)
			print 'No.' + str(x) + ' ,' +  url + '.......' + ','.join(tags)
			# sh.update_acell('H'+str(x+2), status)
			sh.update_acell('J'+str(x+2), ','.join(tags))


	# for x in range(2, 38) :
	# 	url = worksheet.acell('C'+str(x)).value
	# 	status = url_check(url)
	# 	snippet = get_job_snippet(url)
	# 	tags = keyword_seach(snippet, snippet)
	# 	print 'No.' + str(x) + ' ,' +  url + '.......' + str(status) 
	# 	worksheet.update_acell('H'+str(x), status)
	# 	worksheet.update_acell('I'+str(x), snippet)
	# 	worksheet.update_acell('J'+str(x), tags)

	# result = get_locations(job_sh)
	# worksheet = job_sh.worksheet("Locations")
	# for x, item in enumerate(result) :
	# 	cell_list = worksheet.range('A'+str(x+1)+':F'+str(x+1))
	# 	for i, val in enumerate(item) :
	# 		cell_list[i].value = val
	# 	worksheet.update_cells(cell_list)


	print("--- %s seconds ---" % (time.time() - start_time))