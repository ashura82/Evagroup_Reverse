#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
sys.path.append('./script')

from mod import *

#############################
# Installation pare-feu CSF #
#############################
installCsf()

##########################
# Installation IDS SNORT #
##########################
installSnort()

#####################
# Installation SNMP #
#####################
installSnmp()

######################
# Installation NGINX #
######################
subprocess.call('./script/nginx.sh',shell=True)