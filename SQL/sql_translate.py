import MySQLdb
import csv

# -------------- Prepare data from script (Space and Quotation) --------------
def prepare_data(raw_data) :
	data = []
	for d in raw_data :
		if type(d) is str:
			data.append(MySQLdb.escape_string(d.strip()))
		else :
			data.append(d)
	return data

# ------------ Location Data (City, State, Abbreviation, Country, Latitude, Longitude) ---------------
def upload_location(raw_data) :
	f = open('Result/upload_location.sql', 'a')
	location = prepare_data(raw_data)
	sql = '''INSERT INTO zd_new_location(City, State, Abbreviation, Country, Latitude, Longitude) VALUES (\'{0[0]}\', \'{0[1]}\', \'{0[2]}\', \'{0[3]}\', {1}, {2}) ON DUPLICATE KEY UPDATE State = VALUES(State), Latitude = VALUES(Latitude), Longitude = VALUES(Longitude);'''.format(location, float(location[4]), float(location[5]))
	f.write(sql + '\n')
	# print sql

# ----------- Job Data(Title, Url, City, Abbreviation, Country, Snippet, tags) ----------
def upload_job(company, raw_data) :
	f = open('Result/upload_jobs.sql', 'a')
	job = prepare_data(raw_data)
	if job[5] == '' :  # Default created time is current date
		job[5] = 'CURDATE()'
	if job[6] == '' :
		job[6] = '0000-00-00' # Default expire time is empty
	sql = '''INSERT INTO zd_new_job (Title, Url, Url_status, Created_on, Org_id, Loc_id, Snippet, tags) SELECT \'{0[0]}\', \'{0[1]}\', 200, \'CURDATE()\', org1.ID, loc1.ID, \'{0[5]}\', \'{0[6]}\' FROM zd_new_organization AS org1, zd_new_location AS loc1 WHERE org1.Name = \'{1}\' AND loc1.City = \'{0[2]}\' AND loc1.Abbreviation = \'{0[3]}\' AND loc1.Country = \'{0[4]}\' ON DUPLICATE KEY UPDATE Snippet = \'{0[5]}\', tags = \'{0[6]}\';'''.format(job, company)
	f.write(sql + '\n')
	# print sql

# ----------- Organization Data (Name, Url, org_tags, org_nickname, snippet) -------------
def upload_organization(raw_data) :
	f = open('Result/upload_organization.sql', 'a')
	organization = prepare_data(raw_data)
	sql = '''INSERT INTO zd_new_organization(Name, Url, org_tags, org_nickname, snippet) VALUES (\'{0[0]}\', \'{0[1]}\', \'{0[2]}\', \'{0[3]}\', \'{0[4]}\') ON DUPLICATE KEY UPDATE org_nickname = \'{0[3]}\';'''.format(organization)
	f.write(sql + '\n')
	# print sql

# ---------------- Location Data(City, State, Abbreviation, Country, Latitude, Longitude) -------------
def update_location(raw_data) :
	f = open('Result/update_location.sql', 'a')
	location = prepare_data(raw_data)
	sql = '''UPDATE zd_new_location SET State = \'{0[1]}\', Latitude = \'{1}\', Longitude = \'{2}\' WHERE City = \'{0[0]}\' AND Abbreviation = \'{0[2]}\' AND Country = \'{0[3]}\';'''.format(location, float(location[4]), float(location[5]))
	f.write(sql + '\n')
	# print sql


# ----------- Job Data(Title, Url, City, Abbreviation, Country, Snippet, tags) ----------
def update_job(company, raw_data) :
	f = open('Result/update_job.sql', 'a')
	job = prepare_data(raw_data)
	sql = '''UPDATE zd_new_job AS job JOIN zd_new_organization AS org JOIN zd_new_location AS loc ON job.Org_id = org.ID AND job.Loc_id = loc.ID SET Snippet = \'{0[5]}\', tags = \'{0[6]}\' WHERE Title = \'{0[0]}\' AND job.Url = \'{0[1]}\' AND City = \'{0[2]}\' AND Abbreviation = \'{0[3]}\' AND Country = \'{0[4]}\' AND org.Name = \'{1}\';'''.format(job, company)
	f.write(sql + '\n')
	# print sql


# ----------- Organization Data (Name, Url, org_tags, org_nickname, snippet) -------------
def update_organization(raw_data) :
	f = open('Result/update_organization.sql', 'a')
	organization = prepare_data(raw_data)
	sql = '''UPDATE zd_new_organization SET org_tags = \'{0[2]}\',  org_nickname = \'{0[3]}\' WHERE Name = \'{0[0]}\';'''.format(organization)
	f.write(sql + '\n')
	# print sql


if __name__ == '__main__':
	start_time = time.time()

	print ''

	print("--- %s seconds ---" % (time.time() - start_time))


	# f = csv.reader(open('location_fixed.csv', 'rU'))
	# for row in f : 
	# 	rec = [row[0], row[1], row[2], row[3], row[4], row[5]]
	# 	update_location(rec)
