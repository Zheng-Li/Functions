# -*- coding: utf-8 -*-
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def convert(text) :
	text = '<br>'.join(text.split('\n'))

	# English
	text = text.replace('YOUR TASKS AND RESPONSIBILITIES', '<br>YOUR TASKS AND RESPONSIBILITIES')
	text = text.replace('WHO YOU ARE', '<br>WHO YOU ARE')
	text = text.replace('YOUR APPLICATION', '<br>YOUR APPLICATION')

	# French
	text = text.replace('Libellé de poste ','<br>Libellé de poste')
	text = text.replace('Votre profil','<br>Votre profil')
	text = text.replace('Votre Candidature','<br>Votre Candidature')

	# German
	text = text.replace('IHRE AUFGABEN UND VERANTWORTLICHKEITEN','<br>IHRE AUFGABEN UND VERANTWORTLICHKEITEN')
	text = text.replace('WAS SIE MITBRINGEN','<br>WAS SIE MITBRINGEN')
	text = text.replace('IHRE BEWERBUNG','<br>IHRE BEWERBUNG')

	# Italian
	text = text.replace('Attività','<br>Attività')
	text = text.replace('Requisiti','<br>Requisiti')
	text = text.replace('Condizioni','<br>Condizioni')

	return text


if __name__ == '__main__':
	text = ''''''
	text = convert(text)
	print text

	# sql = '''INSERT INTO zd_new_job(Title, Snippet ,Url, Url_status, Created_on, Org_id, Loc_id, tags) 
	# SELECT \'%s\', \'%s\', \'%s\', 200, %s, org.ID, loc.ID, \'%s\' 
	# FROM zd_new_organization AS org, zd_new_location AS loc 
	# WHERE org.Name = \'%s\' AND loc.City = \'%s\' AND loc.Abbreviation = \'%s\' AND loc.Country = \'%s\' 
	# ON DUPLICATE KEY UPDATE tags = \'%s\';'''

	
