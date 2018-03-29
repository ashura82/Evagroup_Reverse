#!/usr/bin/python
# -*- coding: latin-1 -*-
#Auteur : Jonathan DAUTRICOURT

import paramiko
import os
import getpass
import socket
import subprocess
import psutil

def upIp():

		print ''
		print 'Entrez IP pour acces SSH BDD :'
		ipBdd = raw_input()
	
		print 'Entrez le mot de passe pour acces SSH BDD :'
		mdpBdd = getpass.getpass()

		addrs = psutil.net_if_addrs()
		ListNet = addrs.keys()

		print 'Choix de la carte CSF :'
		compt = 0

		for a in ListNet:
			compt += 1
			print str(compt) + ' - ' + a

		print''
		print 'Indiquez le nom de la carte pour déploiement : '
		intNet = raw_input()

		#Récupération IP et hostname
		subprocess.call('ping -c 4 -i 0.2 ' + ipBdd + ' > /dev/null 2>&1',shell=True)
		hostnameCsf = socket.gethostname()
		ipCsf = os.popen('ip addr show ' + intNet).read().split("inet ")[1].split("/")[0]

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