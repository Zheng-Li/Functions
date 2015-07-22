# -*- coding: utf-8 -*-
import re
import urllib2
import socket
import httplib
import csv
import json
import gspread
import time
from File.file import *
from oauth2client.client import SignedJwtAssertionCredentials
from Geolocation.geolocation_reference import get_abbreviation
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
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


def check_if_exists (title, remove_keyword_dict) :
	title = title.strip().lower()
	for ky in remove_keyword_dict :
		ky_tmp = re.escape(ky.strip().lower())
		reg = '\\b' + ky_tmp + '[,.]?\\b'
		result = re.search(reg, title)  
		if result :
			return True
	return False


def load_remove_keywords () :
	spreadsheet_name = 'Test Project'
	worksheet_name = 'Keywords_Jobs to Remove'
	ws = login(spreadsheet_name, worksheet_name)

	keyword_dict = ws.col_values(1)
	del keyword_dict[0]

	return keyword_dict

def load_tag_keywords () :
	spreadsheet_name = 'Test Project'

	worksheet_name_1 = 'Keywords Page 1 Job Tags Noun'
	ws_1 = login(spreadsheet_name, worksheet_name_1)
	keyword_dict_1 = {}

	raw_data_1 = ws_1.get_all_values()
	for row in raw_data_1 :
		key = row.pop(0).lower().strip()
		values = filter(None, row)
		keyword_dict_1[key] = [x.lower() for x in values]

	worksheet_name_2 = 'Keywords Page 2 Job Tags Adjective'
	ws_2 = login(spreadsheet_name, worksheet_name_2)
	keyword_dict_2 = {}

	raw_data_2 = ws_2.get_all_values()
	for row in raw_data_2 :
		key = row.pop(0).lower().strip()
		values = filter(None, row)
		keyword_dict_2[key] = [x.lower() for x in values]

	return  keyword_dict_1, keyword_dict_2

def load_special_tag_keywords () :
	spreadsheet_name = 'Test Project'
	worksheet_name = 'Tech Related Architecture Keywords'
	ws = login(spreadsheet_name, worksheet_name)
	keyword_dict = {}

	raw_data = ws.get_all_values()
	del raw_data[0]
	for row in raw_data :
		del row[0]
		key = row.pop(0).lower().strip()
		values = filter(None, row)
		keyword_dict[key] = [x.lower() for x in values]

	return keyword_dict


def tag_job (title, keyword_dict) :
	tag_list = []
	title = title.strip().lower()
	for ky in keyword_dict.keys() :
		ky_tmp = re.escape(ky)
		reg = '\\b' + ky_tmp + '[,.]?\\b'
		result = re.search(reg, title.encode('utf-8'))  
		if result :
			tag_list.append(ky)
			tag_list += keyword_dict[ky]
	tags = list(set(tag_list))
	return tags


def tag_special_job (title, keyword_dict, special_tag) :
	tag_list = []
	title = title.strip().lower()
	for ky in keyword_dict.keys() :
		ky_tmp = re.escape(ky)
		reg = '\\b' + ky_tmp + '[,.]?\\b'
		result = re.search(reg, title)  
		if result is not None :
			tag_list.append(ky + ' ' + special_tag)
			tag_list += keyword_dict[ky]

	tags = list(set(tag_list))
	return tags


if __name__ == '__main__':
	start_time = time.time()

	arch_list = ['architecture','architect','architectural','architects']
	design_list = ['design', 'designer','designers']

	remove_keyword_dict = load_remove_keywords()
	tag_keyword_dict_1, tag_keyword_dict_2 = load_tag_keywords()
	special_keyword_dict = load_special_tag_keywords()

	spreadsheet_name = 'Organization Parsing Project 01'
	worksheet_name = 'Deloitte'
	title_col = 1

	worksheet = login(spreadsheet_name, worksheet_name)
	titles = worksheet.col_values(title_col)
	del titles[0]

	for i, title in enumerate(titles) :
		title = title.lower()
		if check_if_exists(title, remove_keyword_dict) :
			tags = 'Experienced'
		else :
			tags = ''
			tag = tag_job(title, tag_keyword_dict_1)
			if tag :
				tag += tag_job(title, tag_keyword_dict_2)

				# architect issues
				if any(key in title for key in arch_list) and check_if_exists(title, special_keyword_dict):
					tag = list(set(tag))
					arch_remove_list = tag_keyword_dict_2.get('architect')
					arch_remove_list.append('architect')
					for item in arch_remove_list :
						if item in tag :
							tag.remove(item)
					tag += tag_special_job(title, special_keyword_dict, 'architecture')	
				
				# design issues
				if any(key in title for key in design_list) and check_if_exists(title, special_keyword_dict):
					tag = list(set(tag))
					design_remove_list = tag_keyword_dict_2.get('design')
					design_remove_list.append('design')
					for item in design_remove_list :
						if item in tag :
							tag.remove(item)
					tag += tag_special_job(title, special_keyword_dict, 'designer')
				
				tags = ','.join(list(set(tag)))
		print tags

	print("--- %s seconds ---" % (time.time() - start_time))


