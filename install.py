#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
sys.path.append('./script')

from mod import *


######################
# Installation NGINX #
######################
subprocess.call('./script/nginx.sh',shell=True)

##########################
# Installation IDS SNORT #
##########################
print '##################'
print 'Installation SNORT'
print '##################'
print ''
installSnort()
print ''

#####################
# Installation SNMP #
#####################
print '#################'
print 'Installation SNMP'
print '#################'
print ''
installSnmp()
print ''

#############################
# Installation pare-feu CSF #
#############################
print '################'
print 'Installation CSF'
print '################'
print ''
installCsf()
print ''
print 'Fin Installation'
