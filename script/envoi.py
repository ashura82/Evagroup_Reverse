#!/usr/bin/python
# -*- coding: latin-1 -*-

import paramiko
import getpass
import socket
import subprocess
import psutil
import os

def upIp():

	print ''
	print 'Entrez IP pour acces SSH BDD :'
	ipBdd = raw_input()
	
	print 'Entrez le mot de passe pour acces SSH BDD :'
	mdpBdd = getpass.getpass()

	addrs = psutil.net_if_addrs()
	listNet = addrs.keys()

	print ''
	print 'Choix de la carte CSF :'
	test = 0

	while test == 0:
		compt = 0
		for a in listNet:
			compt += 1
			print str(compt) + ' - ' + a

		print''
		print "Indiquez l'index carte pour déploiement : "

		intNet = raw_input()
			
		try :
			intNet = int(intNet)
		except ValueError :
			print 'Saisissez un nombre'

		if type(intNet) is int:
			indexError = len(listNet)
				
			if intNet > indexError :
				print 'Erreur index'
			else:
				intNet -= 1
				ipNet = listNet[intNet]
				for a in listNet:
					if a == ipNet :
						test = 1

	#Récupération IP et hostname
	subprocess.call('ping -c 4 -i 0.2 ' + ipBdd + ' > /dev/null 2>&1',shell=True)
	hostnameCsf = socket.gethostname()
	recupIp = subprocess.Popen('ip a | grep ' + ipNet + ' | grep inet | cut -d "/" -f 1 | cut -c10-', stdout=subprocess.PIPE, shell=True)
	ipCsf = recupIp.communicate()[0].split()[0]

	#Erreur SSH-AGENT
	subprocess.call('eval `ssh-agent -s` | ssh-add > /dev/null 2>&1',shell=True)

	#Connexion SSH BDD
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(hostname = ipBdd, username='root', password=mdpBdd, port=22)
	print 'Connexion serveur BDD                   [OK]'

	#Création dossier .ssh et fichier authorized_key
	if os.path.exists('/root/.ssh') == True :
		subprocess.call('touch /root/.ssh/authorized_keys',shell=True)
	else:
		subprocess.call('mkdir /root/.ssh/ && touch /root/.ssh/authorized_keys',shell=True)
	
	#Téléchargement BDD.pub vers CSF
	sftp = client.open_sftp()
	destination = '/root/.ssh/authorized_keys'
	source = '/root/.ssh/id_rsa.pub'
	sftp.get(source,destination)

	#Ajout de l'ip et hostname CSF vers fichier tmpip BDD
	cmd = 'echo ' + str(ipCsf) + ',' + hostnameCsf + ' >> /srv/csf/tmpip.conf'
	stdin, stdout, stderr = client.exec_command(cmd)
	#Changement state BDD vers fichier state pour prise en compte maj
	cmd2 = 'echo "BDD" > /srv/csf/script/state.conf'
	stdin, stdout, stderr = client.exec_command(cmd2)

	print 'Enregistrement CSF                      [OK]'

	sftp.close()
	client.close()

upIp()
