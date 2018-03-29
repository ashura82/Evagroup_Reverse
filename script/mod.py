#!/usr/bin/python
# -*- coding: latin-1 -*-

import subprocess
import tarfile

#######
# CSF #
#######

def installCsf():

	print 'Installation prérequis                  [En cours]'
	subprocess.call('apt-get remove fail2ban > /dev/null 2>&1',shell=True)
	subprocess.call('apt-get update > /dev/null 2>&1 && apt-get install git bash wget gnupg grep unzip coreutils findutils gawk e2fsprogs iproute sendmail iptables traceroute perl libwww-perl libcrypt-ssleay-perl libio-socket-ssl-perl libgd-graph-perl libsocket6-perl libio-socket-inet6-perl ipset iotop iftop lsof dnsutils python-pip -y > /dev/null 2>&1',shell=True)
	subprocess.call('pip install paramiko psutil > /dev/null 2>&1',shell=True)
	print 'Installation prérequis                  [OK]'

	print 'Téléchargement CSF                      [En cours]'
	subprocess.call('wget https://download.configserver.com/csf.tgz > /dev/null 2>&1',shell=True)
	print 'Téléchargement CSF                      [OK]'

	print 'Installation CSF                        [En cours]'
	subprocess.call('tar -xzf csf.tgz > /dev/null 2>&1 && cd ./csf > /dev/null 2>&1 && ./install.sh > /dev/null 2>&1',shell=True)
	subprocess.call('rm csf.tgz',shell=True)
	print 'Installation CSF                        [OK]'

	subprocess.call('perl /usr/local/csf/bin/csftest.pl > /dev/null 2>&1',shell=True)
	print 'Test CSF                                [OK]'

	subprocess.call('sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/g" /etc/ssh/sshd_config',shell=True)
	subprocess.call('systemctl restart sshd',shell=True)
	print 'Configuration SSH                       [OK]'

	print 'Envoi des configurations au serveur BDD [En cours]'
	cmd = 'python ./script/envoi.py'
	subprocess.call(cmd,shell=True)
	print 'Envoi des configurations au serveur BDD [OK]'

#########
# SNORT #
#########

def installSnort():

	installDependences()
	
	subprocess.call('wget -P /usr/src/snort_src/ https://www.snort.org/downloads/snort/snort-2.9.11.1.tar.gz > /dev/null 2>&1',shell=True)

	tar = tarfile.open("/usr/src/snort_src/snort-2.9.11.1.tar.gz")
	tar.extractall(path='/usr/src/snort_src/')
	tar.close()

	subprocess.call('/usr/src/snort_src/snort-2.9.11.1/configure > /dev/null 2>&1',shell=True)
	subprocess.call('make -I /usr/src/snort_src/snort-2.9.11.1 > /dev/null 2>&1',shell=True)
	subprocess.call('make -I /usr/src/snort_src/snort-2.9.11.1 install > /dev/null 2>&1 ',shell=True)
	subprocess.call('ldconfig',shell=True)

	print 'Installation de SNORT             [OK]'

	configSnort()

def installDependences():
	subprocess.call('apt-get update > /dev/null 2>&1',shell=True)
	subprocess.call('apt-get upgrade -y > /dev/null 2>&1',shell=True)
	subprocess.call('apt-get install flex bison build-essential checkinstall libpcap-dev libnet1-dev libpcre3-dev libnetfilter-queue-dev iptables-dev libdumbnet-dev zlib1g-dev -y > /dev/null 2>&1',shell=True)
	print 'Installation des dépendences      [OK]'

	path_snort_src = "/usr/src/snort_src"
	subprocess.call('mkdir ' + path_snort_src,shell=True)

	subprocess.call('wget -P /usr/src/snort_src/ https://www.snort.org/downloads/snort/daq-2.0.6.tar.gz > /dev/null 2>&1',shell=True)

	tar = tarfile.open("/usr/src/snort_src/daq-2.0.6.tar.gz")
	tar.extractall(path='/usr/src/snort_src/')
	tar.close()

	subprocess.call('/usr/src/snort_src/daq-2.0.6/configure > /dev/null 2>&1',shell=True)
	subprocess.call('make -I /usr/src/snort_src/daq-2.0.6 > /dev/null 2>&1',shell=True)
	subprocess.call('make -I /usr/src/snort_src/daq-2.0.6 install > /dev/null 2>&1 ',shell=True)

	print 'Installation de DAC               [OK]'

def configSnort():
	path_snort = "/etc/snort"
	path_rules = "/etc/snort/rules"
	path_preproc_rules = "/etc/snort/preproc_rules"
	path_log = "/var/log/snort"
	path_snort_dynamicrules = "/usr/local/lib/snort_dynamicrules"

	rule ='var RULE_PATH ../rules'
	so_rule = 'var SO_RULE_PATH ../so_rules'
	preproc = 'var PREPROC_RULE_PATH ../preproc_rules'
	white_list = 'var WHITE_LIST_PATH ../rules'
	black_list = 'var BLACK_LIST_PATH ../rules'
	specific_rules = "# site specific rules"

	subprocess.call('mkdir ' + path_snort,shell=True)
	subprocess.call('mkdir ' + path_log,shell=True)
	subprocess.call('mkdir ' + path_snort_dynamicrules,shell=True)
	subprocess.call('mkdir ' + path_preproc_rules,shell=True)
	subprocess.call('mkdir ' + path_rules,shell=True)

	subprocess.call('touch /etc/snort/rules/white_list.rules /etc/snort/rules/black_list.rules /etc/snort/rules/local.rules',shell=True)
	subprocess.call('cp /usr/src/snort_src/snort*/etc/*.conf* /etc/snort',shell=True)
	subprocess.call('cp /usr/src/snort_src/snort*/etc/*.map /etc/snort',shell=True)

	oldConf = open('/etc/snort/snort.conf','r')
	newConf = open('/etc/snort/snort2.conf','w')
	lines = oldConf.readlines()

	for line in lines:
		found = line.split('/')

		if found[0] != 'include $RULE_PATH':
			if rule in line:
				newConf.write('var RULE_PATH /etc/snort/rules' + '\n')
			elif so_rule in line:
				newConf.write('var SO_RULE_PATH /etc/snort/so_rules' + '\n')
			elif preproc in line:
				newConf.write('var PREPROC_RULE_PATH /etc/snort/preproc_rules' + '\n')
			elif white_list in line:
				newConf.write('var WHITE_LIST_PATH /etc/snort/rules' + '\n')
			elif black_list in line:
				newConf.write('var BLACK_LIST_PATH /etc/snort/rules' + '\n')
			elif specific_rules in line:
				newConf.write('include $RULE_PATH/community.rules' + '\n')
			else:
				newConf.write(line)
		

	oldConf.close()
	newConf.close()

	subprocess.call('mv /etc/snort/snort2.conf /etc/snort/snort.conf',shell=True)

	subprocess.call('snort -T -c /etc/snort/snort.conf > /dev/null 2>&1',shell=True)

	print 'Configuration de SNORT            [OK]'

########
# SNMP #
########

def installSnmp():
	subprocess.call('apt-get update > /dev/null 2>&1',shell=True)
	subprocess.call('apt-get install snmpd snmp -y > /dev/null 2>&1',shell=True)
	print 'Installation SNMP                 [OK]'

	configSnmp()

def configSnmp():
	subprocess.call('sed -i "s/agentAddress  udp:127.0.0.1:161/#agentAddress  udp:127.0.0.1:161/g" /etc/snmp/snmpd.conf',shell=True)
	subprocess.call('sed -i "s/#agentAddress udp:161,udp6:\[::1\]:161/agentAddress udp:161,udp6:\[::1\]:161/g" /etc/snmp/snmpd.conf',shell=True)
	subprocess.call('sed -i "s/#rocommunity public  localhost/rocommunity public  localhost/g" /etc/snmp/snmpd.conf',shell=True)
	subprocess.call('systemctl restart snmpd > /dev/null 2>&1',shell=True)
	print 'Configuration SNMP                [OK]'
