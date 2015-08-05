from File.file import *
import time
from time import sleep
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


if __name__ == '__main__':
	start_time = time.time()

	spreadsheet_name = 'Test Project'
	worksheet_name = 'Organizations Updated July 15'
	start_row = 323
	end_row = 357
	has_header = True

	organization_list = read_spreadsheet(spreadsheet_name, worksheet_name, has_header)
	print len(organization_list)
	upload_list = organization_list[start_row-2 : end_row-1]
	for row in upload_list :
		print row[0] + '...' + row[2]


	print("--- %s seconds ---" % (time.time() - start_time))
