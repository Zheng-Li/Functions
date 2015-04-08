import csv

abbr = {
	'AL' :	'Alabama',
	'AK' :	'Alaska',
	'AZ' :	'Arizona',
	'AR' :	'Arkansas',
	'CA' :	'California',
	'CO' :	'Colorado',
	'CT' :	'Connecticut',
	'DE' :	'Delaware',
	'FL' :	'Florida',
	'GA' :	'Georgia',
	'HI' :	'Hawaii',
	'ID' :	'Idaho',
	'IL' :	'Illinois',
	'IN' :	'Indiana',
	'IA' :	'Iowa',
	'KS' :	'Kansas',
	'KY' :	'Kentucky',
	'LA' :	'Louisiana',
	'ME' :	'Maine',
	'MD' :	'Maryland',
	'MA' :	'Massachusetts',
	'MI' :	'Michigan',
	'MN' :	'Minnesota',
	'MS' :	'Mississippi',
	'MO' :	'Missouri',
	'MT' :	'Montana',
	'NE' :	'Nebraska',
	'NV' :	'Nevada',
	'NH' :	'New Hampshire',
	'NJ' :	'New Jersey',
	'NM' :	'New Mexico',
	'NY' :	'New York',
	'NC' :	'North Carolina',
	'ND' :	'North Dakota',
	'OH' :	'Ohio',
	'OK' :	'Oklahoma',
	'OR' :	'Oregon',
	'PA' :	'Pennsylvania',
	'RI' :	'Rhode Island',
	'SC' :	'South Carolina',
	'SD' :	'South Dakota',
	'TN' :	'Tennessee',
	'TX' :	'Texas',
	'UT' :	'Utah',
	'VT' :	'Vermont',
	'VA' :	'Virginia',
	'WA' :	'Washington',
	'WV' :	'West Virginia',
	'WI' :	'Wisconsin',
	'WY' :	'Wyoming',
	'DC' :	'District of Columbia',
	'NS' :	'Nova Scotia',
	'NB' :	'New Brunswick',
	'ON' :	'Ontario',
	'BC' :	'British Columbia',
	'QC' :	'Quebec',
}

def get_full_name(abbrevation) :
	if abbrevation in abbr :
		return abbr[abbrevation]
	else :
		full_name = abbrevation
		return full_name

def get_abbrevation(full_name) :
	for abbrevation, full in abbr.iteritems() :
		if full_name == full :
			return abbrevation

if __name__ == '__main__':
	w = csv.writer(open('abbrevation.csv', 'w'))
	for key, val in abbr.items() :
		w.writerow([key,val])