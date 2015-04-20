import requests
import gspread
import time
from geolocation import send_request_by_location
from sql_upload import upload_location
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


if __name__ == '__main__':
	start_time = time.time()
	gc = gspread.login('zheng@zoomdojo.com', 'marymount05')
	sh = gc.open('Zheng: Jobs for Upload: April 17_2015_Project7')

	# worksheet = sh.worksheet('Accor')
	# worksheet = sh.worksheet('Acne Studios')
	# worksheet = sh.worksheet('Acxiom')
	# worksheet = sh.worksheet('Airbnb, Inc.')
	# worksheet = sh.worksheet('American Rivers')
	# worksheet = sh.worksheet('Associated Bank')
	# worksheet = sh.worksheet('Amnesty International')
	# worksheet = sh.worksheet('Baxter International Inc.')
	# worksheet = sh.worksheet('Orbital ATK Inc.')

	for x in range(2, 38) :
		url = worksheet.acell('C'+str(x)).value
		status = url_check(url)
		print 'No.' + str(x) + ' ,' +  url + '.......' + str(status) 
		worksheet.update_acell('H'+str(x), status)

	# result = get_locations(sh)
	# worksheet = sh.worksheet("Locations")
	# for x, item in enumerate(result) :
	# 	cell_list = worksheet.range('A'+str(x+1)+':F'+str(x+1))
	# 	for i, val in enumerate(item) :
	# 		cell_list[i].value = val
	# 	worksheet.update_cells(cell_list)


	print("--- %s seconds ---" % (time.time() - start_time))