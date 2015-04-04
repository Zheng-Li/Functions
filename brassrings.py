import re
import csv
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import gspread
from geolocation import send_request_by_location
from upload import upload_location
import time

AETNA='<p>For job details and to Apply: <a href="https://www.aetna.com/about-us/aetna-careers.html">Click Here</a></p><p>Click Apply for Jobs Online to navigate to Search Openings. Enter Req # or Job Title and Search.</p>'
AMWAY='<p>For job details and to Apply: <a href="http://jobs.brassring.com/EN/ASP/TG/cim_home.asp?sec=1&PartnerId=8647&SiteId=33&codes">Click Here</a></p><p>Click Search Career / Internship Opportunities.</p>'
FIDELITY='<p>For job details and to Apply: <a href="http://jobs.fidelity.com/apply-now/search-jobs.html">Click Here</a></p><p>Enter Job # or Job Title and Search.</p>'
ADOBE='<p>For job details and to Apply: <a href="http://adobe.taleo.net/careersection/adobe_global/jobsearch.ftl?lang=en&location=6801372523&jobfield=0">Click Here</a></p><p>Enter Job # or Job Title in Keywords and Search.</p>'
BAYER='<p>For job details and to Apply: <a href="http://career.bayer.us/en/job-search/?accessLevel=&functional_area=&country=US&location=&division=&fulltext=internship">Click Here</a></p><p>Click on Job Title</p>'
SCHWAB='<p>For job details and to Apply: <a href="http://www.aboutschwab.com/work-at-schwab">Click Here</a></p><p>Click Start you job search.</p>  <p>Enter Job Title in Keywords and Search.</p>'
GENERAL='<p>For job details and to Apply: <a href="http://www.gdcareers.com/gdchq_jobs/main.cfm?pg=search">Click Here</a></p><p>Enter Job ID # or Job Title and Search.</p>'
WEYERHAUSER='<p>For job details and to Apply: <a href="https://weyerhaeuser.taleo.net/careersection/10000/jobdetail.ftl">Click Here</a></p><p>Enter Job # or Job Title and Search.</p>'

def login(sheet_name) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open(sheet_name)
	return  sh    

def sheet_input(spreadsheet, sheetname) :
	worksheet = spreadsheet.worksheet(sheetname)
	data_list = worksheet.get_all_values()
	# data_list.pop(0)

	# Insert organization name
	for data in data_list :
		if not data[0] :
			data[0] = sheetname
	# csv_output(data_list, 'Backup/'+sheetname+'_backup.csv')
	return data_list

def data_parse(raw_data) :
	records = []
	url = 'http://career.bayer.us/en/job-search/?accessLevel=&functional_area=&country=US&location=&division=&fulltext=internship'
	raw_data.pop(0)
	raw_data.pop(0)
	for row in raw_data :
		record = [row[0], row[1], url, row[7], row[6], row[3],row[2]]
		records.append(record)
	return records

def keyword_find(text) :
	keyword_tag = []

	for ky in keywords :
		ky = ky.strip()
		reg = '\\b' + ky + '\\b'
		re.search(reg, text)  
		if re.search(reg, text) is not None :
			keyword_tag.append(ky)
	return keyword_tag

def csv_input(csv_file) :
	data_list = []
	csv_reader = csv.reader(open(csv_file, 'rU'))
	for row in csv_reader :
		data_list.append(row)
	return data_list

def sql_output(data) :
	f = open('brassrings.sql', 'a')
	for item in data:
  		f.write("%s " % item)
	f.write('\n')

if __name__ == '__main__':
	start_time = time.time()
	sheet = login('Zheng Brass Rings Jobs to upload March 2015')
	raw_data = sheet_input(sheet, 'Bayer AG')
	records = data_parse(raw_data)
	location = []
	keywords = [] 

	# for rec in records :
	# 	location.append([rec[3].strip(), rec[4].strip(), rec[5].strip()])
	# location_set = set(map(tuple,location))  #need to convert the inner lists to tuples so they are hashable
	# location = map(list,location_set) #Now convert tuples back into lists (maybe unnecessary?)
	# for count, x in enumerate(location) :
	# 	print str(count) + '------'
	# 	result = send_request_by_location(x[0], x[1], x[2])
	# 	print result
	# 	upload_location(result)
	# 	# print result

	raw_key = csv_input('keys.csv')
	for key in raw_key :
		keywords.append(key[0].lower())
	print 'Keys....Done'
	for count, rec in enumerate(records) :
		rec.append(keyword_find(rec[1]))	
		if rec is not None:
			sql_output(rec)
			print str(count) + '---' + rec[1] + '...Done'

	print("--- %s seconds ---" % (time.time() - start_time))