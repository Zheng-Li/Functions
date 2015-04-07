import MySQLdb
import csv

def upload_location(data) :
	f = open('location.sql', 'a')
	sql = '''INSERT INTO zd_new_location(City, State, Abbreviation, Country, Latitude, Longitude) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', %s, %s) ON DUPLICATE KEY UPDATE State = VALUES(State), Latitude = VALUES(Latitude), Longitude = VALUES(Longitude);''' %(MySQLdb.escape_string(data[0]), MySQLdb.escape_string(data[1]), MySQLdb.escape_string(data[2]), MySQLdb.escape_string(data[3]), float(data[4]), float(data[5]))
	f.write(sql + '\n')
	print data

def upload_job(data) :
	f = open('jobs.sql', 'a')
	data[0] = MySQLdb.escape_string(data[0].strip())
	data[1] = MySQLdb.escape_string(data[1].strip())
	data[2] = MySQLdb.escape_string(data[2].strip())
	data[3] = MySQLdb.escape_string(data[3].strip())
	data[4] = MySQLdb.escape_string(data[4].strip())
	data[5] = MySQLdb.escape_string(data[5].strip())
	data[6] = MySQLdb.escape_string(data[6].strip())
	data[7] = MySQLdb.escape_string(data[7].strip())
	job_sql = '''INSERT INTO zd_new_job(Title, Url, Url_status, Created_on, Expired_on, Org_id, Loc_id, tags) SELECT \'{0[1]}\', \'{0[2]}\', 200, CURDATE(), \'{0[6]}\', org1.ID, loc1.ID, \'{0[7]}\' FROM zd_new_organization AS org1, zd_new_location AS loc1 WHERE org1.Name = \'{0[0]}\' AND loc1.City = \'{0[3]}\' AND loc1.Abbreviation = \'{0[4]}\' AND loc1.Country = \'{0[5]}\' AND NOT EXISTS (SELECT 1 FROM zd_new_job as job WHERE Title = \'{0[1]}\' AND job.Org_id = org1.ID AND job.Loc_id = loc1.ID AND job.Url = \'{0[2]}\');'''.format(data)
	f.write(job_sql + '\n')
	# f2 = open('jobs_tags.sql', 'a')
	# tags = data[7].split(',')
	# for tag in tags :
	# 	tag_sql = '''INSERT INTO zd_new_job_tag (ID, Tag) VALUES (LAST_INSERT_ID(), \'%s\');''' %(tag)
	# 	f2.write(tag_sql + '\n')


def update_job(data) :
	f = open('update.sql', 'a')
	data[0] = MySQLdb.escape_string(data[0].strip())
	data[1] = MySQLdb.escape_string(data[1].strip())
	data[2] = MySQLdb.escape_string(data[2].strip())
	data[3] = MySQLdb.escape_string(data[3].strip())
	data[4] = MySQLdb.escape_string(data[4].strip())
	data[5] = MySQLdb.escape_string(data[5].strip())
	data[6] = MySQLdb.escape_string(data[6].strip())
	data[7] = MySQLdb.escape_string(data[7].strip())
	update_sql = '''UPDATE zd_new_job AS job JOIN zd_new_organization AS org JOIN zd_new_location AS loc ON job.Org_id = org.ID AND job.Loc_id = loc.ID SET tags = \'{0[7]}\', Expired_on = \'{0[6]}\' WHERE Title = \'{0[1]}\' AND job.Url = \'{0[2]}\' AND City = \'{0[3]}\' AND Abbreviation = \'{0[4]}\' AND Country = \'{0[5]}\';'''.format(data)
	f.write(update_sql + '\n')


if __name__ == '__main__':
	database = MySQLdb.connect(host = '127.0.0.1', user = 'db_admin', passwd = 'pusEgu5U', db = 'zoomdojo', port = 3307)
	cursor = database.cursor()

	data = read_file('geolocation.csv')
	for item in data :
		upload_location(item)

	cursor.close()
	database.close()

# ++++++++++++++++++++++++++++++
# ALTER TABLE zd_new_location ADD UNIQUE (City, Abbreviation, Country)
# ++++++++++++++++++++++++++++++