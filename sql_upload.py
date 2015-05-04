import MySQLdb
import csv

# -------------- Prepare data from script (Space and Quotation) --------------
def prepare_data(raw_data) :
	data = []
	for d in raw_data :
		data.append(MySQLdb.escape_string(d.strip()))
	return data

# ------------ Location Data (City, State, Abbreviation, Country, Latitude, Longitude) ---------------
def upload_location(raw_data) :
	f = open('Result/upload_location.sql', 'a')
	location = prepare_data(raw_data)
	sql = '''INSERT INTO zd_new_location(City, State, Abbreviation, Country, Latitude, Longitude) 
			 VALUES (\'{0[0]}\', \'{0[1]}\', \'{0[2]}\', \'{0[3]}\', {1}, {2}) 
			 ON DUPLICATE KEY 
			 UPDATE State = VALUES(State), Latitude = VALUES(Latitude), Longitude = VALUES(Longitude);
			 '''.format(location, float(location[4]), float(location[5]))
	f.write(sql + '\n')
	# print sql

# ----------- Job Data(Title, Url, City, Abbreviation, Country, Created_on, Expired_on, Snippet, tags) ----------
def upload_job(company, raw_data) :
	f = open('Result/upload_jobs.sql', 'a')
	job = prepare_data(raw_data)
	if job[5] == '' :  # Default created time is current date
		job[5] = 'CURDATE()'
	if job[6] == '' :
		job[6] = '0000-00-00' # Default expire time is empty
	sql = '''INSERT INTO zd_new_job(Title, Url, Url_status, Created_on, Expired_on, Org_id, Loc_id, Snippet, tags) 
			 SELECT \'{0[0]}\', \'{0[1]}\', 200, \'{0[5]}\', \'{0[6]}\', org1.ID, loc1.ID, \'{0[7]}\', \'{0[8]}\' 
			 FROM zd_new_organization AS org1, zd_new_location AS loc1 
			 WHERE org1.Name = \'{1}\' AND loc1.City = \'{0[2]}\' AND loc1.Abbreviation = \'{0[3]}\' AND loc1.Country = \'{0[4]}\' 
			 ON DUPLICATE KEY UPDATE Snippet = \'{0[7]}\', tags = \'{0[8]}\';
			 '''.format(job, company)
	f.write(sql + '\n')
	# print sql

# ---------------- Location Data(City, State, Abbreviation, Country, Latitude, Longitude) -------------
def update_location(raw_data) :
	f = open('Result/update_location.sql', 'a')
	location = prepare_data(raw_data)
	sql = '''UPDATE zd_new_location
			 SET State = \'{0[1]}\', Latitude = \'{1}\', Longitude = \'{2}\'
			 WHERE City = \'{0[0]}\' AND Abbreviation = \'{0[2]}\' AND Country = \'{0[3]}\';
			 '''.format(location, float(location[4]), float(location[5]))
	f.write(sql + '\n')
	# print sql


# ----------- Job Data(Title, Url, City, Abbreviation, Country, Created_on, Expired_on, Snippet, tags) ----------
def update_job(company, raw_data) :
	f = open('Result/update_job.sql', 'a')
	job = prepare_data(raw_data)
	sql = '''UPDATE zd_new_job AS job JOIN zd_new_organization AS org JOIN zd_new_location AS loc 
			 ON job.Org_id = org.ID AND job.Loc_id = loc.ID 
			 SET Snippet = \'{0[7]}\', tags = \'{0[8]}\', Expired_on = \'{0[7]}\' 
			 WHERE Title = \'{0[0]}\' AND job.Url = \'{0[1]}\' AND City = \'{0[2]}\' AND Abbreviation = \'{0[3]}\' AND Country = \'{0[4]}\' AND org.Name = \'{1}\';
			 '''.format(job, company)
	f.write(sql + '\n')


if __name__ == '__main__':
	print 'Working!'

# ++++++++++++++++++++++++++++++
# Job Index (Title, Url, Org_id, Loc_id)
# Location Index (City, Abbreviation, Country)
# ++++++++++++++++++++++++++++++