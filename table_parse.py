import re
import httplib
import urllib2
import socket
import HTMLParser
import random
import gspread
from BeautifulSoup import BeautifulSoup
from time import sleep
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

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
	except socket.error, v:
		print 'Socket error!'
	except (IOError, httplib.HTTPException):
		print 'Unknown error!'

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
		data.append(tmp)
	return data

def update_spreadsheet(data) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open('Zheng Brass Rings Jobs to upload March 2015')

	# worksheet = sh.add_worksheet(title="bayer", rows="200", cols="20")
	worksheet = sh.worksheet('bayer')

	# Header
	cell_list = worksheet.range('A1:E1')
	cell_values = ['Job Title', 'Job Url', 'Posted on', 'Country', 'State-City']
	for i, val in enumerate(cell_values):  #gives us a tuple of an index and value
	    cell_list[i].value = val    #use the index on cell_list and the val from cell_values
	worksheet.update_cells(cell_list)

	# Data
	for x, row in enumerate(data) :
		num = x+2
		cell_list = worksheet.range('A'+str(num)+':F'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)

if __name__ == '__main__':
	# url = 'https://career.bayer.com/en/career/job-search/?accessLevel=student&functional_area=&country=*&location=&company=&fulltext='
	url = 'https://intel.taleo.net/careersection/10000/jobsearch.ftl'
	
	page = url_parse(url)
	print page
	# result = table_parse(page)
	# update_spreadsheet(result)
