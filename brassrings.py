import re
import csv
import gspread
import time
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from geolocation import send_request_by_location
from sql_upload import upload_location
from location_reference import get_abbrevation


AETNA=MySQLdb.escape_string('<p>For job details and to Apply: <a href="https://www.aetna.com/about-us/aetna-careers.html">Click Here</a></p><p>Click Apply for Jobs Online to navigate to Search Openings. Enter Req # or Job Title and Search.</p>')
AMWAY=MySQLdb.escape_string('<p>For job details and to Apply: <a href="http://jobs.brassring.com/EN/ASP/TG/cim_home.asp?sec=1&PartnerId=8647&SiteId=33&codes">Click Here</a></p><p>Click Search Career / Internship Opportunities.</p>')
FIDELITY=MySQLdb.escape_string('<p>For job details and to Apply: <a href="http://jobs.fidelity.com/apply-now/search-jobs.html">Click Here</a></p><p>Enter Job # or Job Title and Search.</p>')
ADOBE=MySQLdb.escape_string('<p>For job details and to Apply: <a href="http://adobe.taleo.net/careersection/adobe_global/jobsearch.ftl?lang=en&location=6801372523&jobfield=0">Click Here</a></p><p>Enter Job # or Job Title in Keywords and Search.</p>')
BAYER=MySQLdb.escape_string('<p>For job details and to Apply: <a href="http://career.bayer.us/en/job-search/?accessLevel=&functional_area=&country=US&location=&division=&fulltext=internship">Click Here</a></p><p>Click on Job Title</p>')
SCHWAB=MySQLdb.escape_string('<p>For job details and to Apply: <a href="http://www.aboutschwab.com/work-at-schwab">Click Here</a></p><p>Click Start you job search.</p>  <p>Enter Job Title in Keywords and Search.</p>')
GENERAL=MySQLdb.escape_string('<p>For job details and to Apply: <a href="http://www.gdcareers.com/gdchq_jobs/main.cfm?pg=search">Click Here</a></p><p>Enter Job ID # or Job Title and Search.</p>')
WEYERHAUSER=MySQLdb.escape_string('<p>For job details and to Apply: <a href="https://weyerhaeuser.taleo.net/careersection/10000/jobdetail.ftl">Click Here</a></p><p>Enter Job # or Job Title and Search.</p>')
INTEL=MySQLdb.escape_string('')

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

# Bayer AG ---------------------------
def data_parse_bayer(raw_data) :
	records = []
	bayer_url = 'http://career.bayer.us/en/job-search/?accessLevel=&functional_area=&country=US&location=&division=&fulltext=internship'
	raw_data.pop(0)
	raw_data.pop(0)
	for row in raw_data :
		record = [row[0], row[1], bayer_url, row[7], row[6], row[3],row[2]]
		records.append(record)
	return records

# Aetna -------------------------
def data_parse_aetna(raw_data) :
	records = []
	aetna_url = 'https://www.aetna.com/about-us/aetna-careers.html'
	raw_data.pop(0)
	for row in raw_data :
		tmp_list = [x.strip() for x in row[4].split(',')]
		for y in tmp_list :
			tmp = y.split('-')
			record = ['Aetna', row[2], aetna_url, tmp[1], tmp[0], 'USA', row[6], row[1]] # Posted on time with Req # 
			records.append(record)
	return records

# Intel -------------------------
def data_parse_intel(raw_data) :
	records = []
	intel_url = 'https://intel.taleo.net/careersection/10000/jobsearch.ftl'
	raw_data.pop(0)
	raw_data.pop(0)
	for row in raw_data :
		if row[2] == 'Multiple Locations' :
			record = ['Intel', row[1], intel_url, '', '', '', row[3]]
		elif row[2] == 'Israel--':
			record = ['Intel', row[1], intel_url, '', '', 'Israel', row[3]]
		else :
			loc = re.split('-|, ', row[2])
			country = loc[0]
			if len(loc) < 2 or 'USA' not in row[2]:
				state = ''
			else : 
				state = get_abbrevation(loc[1])
				if state is None :
					state = ''
			if len(loc) < 3 :
				city = ''
			else :
				city = loc[2]
			record = ['Intel', row[1], intel_url, city, state, country, row[3]]
			# print [city, state, country]
		records.append(record)
	return records

# Fidelity -------------------------
def data_parse_fidelity(raw_data) :
	records = []
	fidelity_url = 'http://jobs.fidelity.com/apply-now/search-jobs.html'
	raw_data.pop(0)
	for row in raw_data :
		if row[2] == 'Multiple Locations' :
			record = ['Fidelity', row[1], fidelity_url, '', '', 'USA', row[3]]
		else :
			loc = re.split('-', row[2])
			if loc[0] == 'US' :
				country = 'USA'
				state = loc[1]
			if len(loc) > 2 :
				city = loc[2]
			else :
				city = ''
			record = ['Fidelity', row[1], fidelity_url, city, state, country, row[3]]
		records.append(record)
	return records

# Amway ------------------------------
def data_parse_amway(raw_data) :
	records = []
	amway_url = 'https://jobs.brassring.com/EN/ASP/TG/cim_home.asp?sec=1&PartnerId=8647&SiteId=33&codes'
	raw_data.pop(0)
	for row in raw_data :
		loc = re.split(', ', row[3])
		record = ['Amway', row[2], amway_url, loc[1], loc[0], 'USA', '']
		records.append(record)
	return records

def keyword_find(text, keywords) :
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

def sql_output(data, company) :
	# company = company + '<b>Job #: ' + data[7] + '</b>' # Only for job with Req # or Job #
	f = open('Result/brassrings.sql', 'a')
	data[0] = MySQLdb.escape_string(data[0].strip())
	data[1] = MySQLdb.escape_string(data[1].strip())
	data[2] = MySQLdb.escape_string(data[2].strip())
	data[3] = MySQLdb.escape_string(data[3].strip())
	data[4] = MySQLdb.escape_string(data[4].strip())
	data[5] = MySQLdb.escape_string(data[5].strip())
	data[6] = MySQLdb.escape_string(data[6].strip())
	data[7] = MySQLdb.escape_string(data[7].strip())
	# data[8] = MySQLdb.escape_string(data[8].strip())
	if data[6] == '' :
		date = 'CURDATE()'
	else :
		date = '\''+ data[6] + '\''
	sql = '''INSERT INTO zd_new_job(Title, Snippet ,Url, Url_status, Created_on, Org_id, Loc_id, tags) SELECT \'{0[1]}\', \'{1}\' ,\'{0[2]}\',200, {2}, org.ID, loc.ID, \'{0[7]}\' FROM zd_new_organization AS org, zd_new_location AS loc WHERE org.Name = \'{0[0]}\' AND loc.City = \'{0[3]}\' AND loc.Abbreviation = \'{0[4]}\' AND loc.Country = \'{0[5]}\' ON DUPLICATE KEY UPDATE tags = \'{0[7]}\';'''.format(data, company,date)
	f.write(sql + '\n')

def parse_location(records) :
	location = []
	for rec in records :
		location.append([rec[3].strip(), rec[4].strip(), rec[5].strip()])
	location_set = set(map(tuple,location))  #need to convert the inner lists to tuples so they are hashable
	location = map(list,location_set) #Now convert tuples back into lists (maybe unnecessary?)
	for count, x in enumerate(location) :
		print str(count) + '------'
		result = send_request_by_location(x[0], x[1], x[2])
		upload_location(result)
	return location

def parse_job(records, company) :
	raw_key = csv_input('keywords.csv')
	keywords = []
	for key in raw_key :
		keywords.append(key[0].lower())
	print 'Keys....Done'
	for count, rec in enumerate(records) :
		tags = ','.join(keyword_find(rec[1].lower(), keywords)) # Job Title Only
		rec.append(tags)	
		if rec is not None:
			sql_output(rec, company)
			print str(count) + '---' + rec[1] + '...Done'

if __name__ == '__main__':
	start_time = time.time()
	sheet = login('Zheng Brass Rings Jobs to upload March 2015')

	# Raw data from different sheets ----------------------------
	# raw_data = sheet_input(sheet, 'Bayer AG')
	# raw_data = sheet_input(sheet, 'Aetna Inc.')
	# raw_data3 = sheet_input(sheet, 'Intel Corporation')
	# raw_data4 = sheet_input(sheet, 'Fidelity')
	# raw_data5 = sheet_input(sheet, 'Amway')
	
	# records = data_parse_bayer(raw_data)
	# records = data_parse_aetna(raw_data)
	# records += data_parse_intel(raw_data3)
	# records += data_parse_fidelity(raw_data4)
	# records += data_parse_amway(raw_data5)

	# location = parse_location(records)

	# Parsing data with different company ------------------------
	# parse_job(records, BAYER)
	# parse_job(records, AETNA)
	# parse_job(records, INTEL)
	# parse_job(records, FIDELITY)
	# parse_job(records, AMWAY)


	print("--- %s seconds ---" % (time.time() - start_time))