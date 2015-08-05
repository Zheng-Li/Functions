from File.file import *
from SQL.sql_translate import *
import time
from time import sleep
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def upload_sql(row) :
	row 


if __name__ == '__main__':
	start_time = time.time()

	spreadsheet_name = 'Test Project'
	worksheet_name = 'Organizations Updated July 15'
	start_row = 323
	end_row = 357
	has_header = True

	organization_list = read_spreadsheet(spreadsheet_name, worksheet_name, has_header)
	organization_list = organization_list[start_row-2 : end_row-1]

	for row in organization_list :
		row = filter(None, row)
		name = row[0]
		nickname = row[1]
		url = row[2]
		snippet = row[3]
		tags = ','.join(row[4:])
		organization = [name, url, tags, nickname, snippet]
		print organization
		upload_organization(organization)


	print("--- %s seconds ---" % (time.time() - start_time))
