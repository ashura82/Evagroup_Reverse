#!/usr/bin/python
# -*- coding: latin-1 -*-
#Auteur : Jonathan DAUTRICOURT

import paramiko
import os
import getpass
import socket
import subprocess

def upIp():

		print ''
		print 'Entrez IP pour acces SSH BDD :'
		ipBdd = raw_input()
	
		print 'Entrez le mot de passe pour acces SSH BDD :'
		mdpBdd = getpass.getpass()

		#Récupération IP et hostname
		subprocess.call('ping -c 4 -i 0.2 ' + ipBdd + ' > /dev/null 2>&1',shell=True)
		hostnameCsf = socket.gethostname()
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect((ipBdd,1))
		ipCsf = s.getsockname()[0]

		#Connexion SSH BDD
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(ipBdd, username='root', password=mdpBdd)
		print 'Connexion serveur BDD                   [OK]'

		#Création dossier .ssh et fichier authorized_key
		os.system('mkdir /root/.ssh/ && touch /root/.ssh/authorized_keys')
		#Téléchargement BDD.pub vers CSF
		sftp = client.open_sftp()
		destination = '/root/.ssh/authorized_keys'
		source = '/root/.ssh/id_rsa.pub'
		sftp.get(source,destination)

		#Ajout de l'ip et hostname CSF vers fichier tmpip BDD
		cmd = 'echo ' + ipCsf + ',' + hostnameCsf + ' >> /srv/csf/tmpip.conf'
		stdin, stdout, stderr = client.exec_command(cmd)
		#Changement state BDD vers fichier state pour prise en compte maj
		cmd2 = 'echo "BDD" > /srv/csf/script/state.conf'
		stdin, stdout, stderr = client.exec_command(cmd2)

		print 'Enregistrement CSF                      [OK]'

		sftp.close()
		client.close()

upIp()