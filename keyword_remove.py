# -*- coding: utf-8 -*-
import time
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

keywords = '''Abschnittsbauleiter
Abteilungsleiter
Accelerated Development
Administrator
Advisor
Commis
Concierge
Conseiller
Conseillers
Consulenti
Consultor
Consultores 
CONTROLEUR
Contrôleur
Controller
Coord
Coord. 
Coordenador 
Coordinateur
Coordinator
Counsel 
Director
Doradca
Dyrektor
Exec
Executive
Experienced
Experienced
Expert
Expert
Head
Instructor
Lead 
Leader
Manager
Mgr
Negotiator
Oversight
Principal
Professional
Senior
Sênior
Snr
Sr
Sr.
Supervisor
DIR
SPCLST
SUPV
Consultant
advanced'''
keyword_list = re.split('\n', keywords)


def check_if_exists (title) :
	if any (keyword in title for keyword in keyword_list) :
		return True
	else :
		return False

if __name__ == '__main__':
	start_time = time.time()
	
	print check_if_exists('Sr. Software Engineer')

	print("--- %s seconds ---" % (time.time() - start_time))

