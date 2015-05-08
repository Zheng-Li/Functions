# -*- coding: utf-8 -*-
import re
import random
import gspread
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def login(spreadsheet) :
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open(spreadsheet)
	return sh

def basf_parse_javascript(browser) :
	records = []
	WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="filters"]/div[1]/div/div[1]/div/div[1]/a/span[1]'))).click()
	WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="filters-inner"]/div[2]/div/div/div/ul/li[1]/label'))).click()
	sleep(2)

	for i in range(0, 5) :
		show_more_button = browser.find_element_by_xpath('//*[@id="mapinfos"]/div[2]/button')
		show_more_button.click()
		sleep(1)

	jobs = browser.find_element_by_xpath('//*[@id="mapinfos"]/div[1]/div[2]').find_elements_by_tag_name('a')
	for j in jobs:
		job_title = j.find_element_by_tag_name('div').find_elements_by_tag_name('div')[0].text
		job_url = j.get_attribute("href")
		job_location = j.find_element_by_tag_name('div').find_elements_by_tag_name('div')[1].text
		job_city = re.split(', ', job_location)[0]
		job_country = re.split(', ', job_location)[1]
		job_posted = j.find_element_by_tag_name('div').find_elements_by_tag_name('div')[4].text
		record = [job_title, job_url, job_city, '', job_country , job_posted]
		records.append(record)
		print record

	update_spreadsheet(records, 'BASF Corporation')


def update_spreadsheet(data, sheet_name) :
	sheet = login('Test')
	worksheet = sheet.worksheet(sheet_name)

	for x, row in enumerate(data) :
		num = x + 2
		cell_list = worksheet.range('A'+str(num)+':F'+str(num))
		for i, val in enumerate(row) :
			cell_list[i].value = val
		worksheet.update_cells(cell_list)


if __name__ == '__main__':
	url = 'https://www.basf.com/en/company/career/jobs.html'

	browser = webdriver.Firefox()
	browser.get(url)

	basf_parse_javascript(browser)

	browser.quit()











