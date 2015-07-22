# -*- coding: utf-8 -*-
import urllib2
import socket
import httplib
import time
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def download_info(url) :
	header = {'User-Agent': 'Mozilla/5.0'}
	request = urllib2.Request(url, headers=header)
	soup = BeautifulSoup(urllib2.urlopen(request).read())
	records = soup.find_all('div', {'class' : 'tech-div'})
	records.pop(0)
	return records

if __name__ == '__main__':
	start_time = time.time()

	url = 'http://www.indiabix.com/technical/core-java/'
	questions = []
	for i in range(1, 23) :
		print 'Page No.' + str(i) + '.....Done'
		questions += download_info(url + str(i))


	f = open('Result/java.xml', 'a')
	f.write('<?xml version="1.0" encoding="utf-8"?>'+'\n')
	f.write('<documents>\n')
	for r in questions :
		r = r.prettify()
		f.write(r)
	f.write('</documents>\n')
	f.close()

	print("--- %s seconds ---" % (time.time() - start_time))

	