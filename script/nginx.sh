#!/bin/bash
 
red=`tput setaf 1`
green=`tput setaf 2`
yellow=`tput setaf 3`
blue=`tput setaf 4`
magenta=`tput setaf 5`
cyan=`tput setaf 6`
reset=`tput sgr0`

echo "${cyan}  _______           _______  _______  _______  _______           _______ "
echo "  (  ____ \|\     /|(  ___  )(  ____ \(  ____ )(  ___  )|\     /|(  ____ )"
echo "  | (    \/| )   ( || (   ) || (    \/| (    )|| (   ) || )   ( || (    )|"
echo "  | (__    | |   | || (___) || |      | (____)|| |   | || |   | || (____)|"
echo "  |  __)   ( (   ) )|  ___  || | ____ |     __)| |   | || |   | ||  _____)"
echo "  | (       \ \_/ / | (   ) || | \_  )| (\ (   | |   | || |   | || (      "
echo "  | (____/\  \   /  | )   ( || (___) || ) \ \__| (___) || (___) || )      "
echo "  (_______/   \_/   |/     \|(_______)|/   \__/(_______)(_______)|/       "
echo "                                                                          "
echo "   _______  _______           _______  _______  _______  _______          "
echo "   (  ____ )(  ____ \|\     /|(  ____ \(  ____ )(  ____ \(  ____ \         "
echo "   | (    )|| (    \/| )   ( || (    \/| (    )|| (    \/| (    \/         "
echo "   | (____)|| (__    | |   | || (__    | (____)|| (_____ | (__             "
echo "   |     __)|  __)   ( (   ) )|  __)   |     __)(_____  )|  __)            "
echo "   | (\ (   | (       \ \_/ / | (      | (\ (         ) || (               "
echo "   | ) \ \__| (____/\  \   /  | (____/\| ) \ \__/\____) || (____/\         "
echo "   |/   \__/(_______/   \_/   (_______/|/   \__/\_______)(_______/ ${reset}        "

spinner()
{
local pid=$!
local delay=0.75
local spinstr='...'
echo "${cyan}      Installation..${reset} "
while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
    local temp=${spinstr#?}
    printf "      %s  " "$spinstr"
    local spinstr=$temp${spinstr%"$temp"}
    sleep $delay
    printf "\b\b\b"
    done
    printf "    \b\b\b\b"
    printf "\n"
}


if [[ "$EUID" -ne 0 ]]; then
	echo -e "${red}Veuillez lancer ce script en root${reset}"
	exit 1
fi


# Clear log file
if [[ (-f /tmp/nginx-autoinstall.log ) ]];then
	rm /tmp/nginx-autoinstall.log
fi

if [[ ! -d  /etc/nginx  ]]; then
	rm -r -f /etc/nginx
fi

if [[ ! -d /usr/local/src/nginx ]]; then
	rm -r -f /usr/local/src/nginx
fi
if [[ (-f /etc/init.d/nginx) ]]; then
	rm -f /etc/init.d/nginx
fi

if [[ ! -d "/opt/flask" ]]; then
	mkdir /opt/flask
	mkdir /opt/flask/templates
fi
cp script/templates/* /opt/flask/templates

# Variables
NGINX_MAINLINE_VER=1.13.10
NGINX_STABLE_VER=1.12.2


echo "${blue}INSTALLATION DE NGINX${reset}"

echo ""
echo "Ce script va installer Nginx et des modules optionnels."
echo ""
echo "Voulez-vous installer Nginx stable ou mainline?"
echo "   1) Stable $NGINX_STABLE_VER"
echo "   2) Mainline $NGINX_MAINLINE_VER"
echo ""

while [[ $nginx_version != "1" && $nginx_version != "2" ]];do
	read -p "Selectionnez une option [1-2]: " nginx_version 
done
case $nginx_version in 
	1)
		nginx_version=$NGINX_STABLE_VER
		PAGESPEED_VER=1.12.34.2
		pagespeed_module="stable"
	;;
	2)
		nginx_version=$NGINX_MAINLINE_VER
		PAGESPEED_VER=1.13.35.2
		pagespeed_module="mainline"
	;;
esac


echo ""
echo "Souhaitez-vous installer le module Pagespeed ? "
while [[ $pagespeed != "y" && $pagespeed != "n" ]];do
	read -p "Pagespeed $PAGESPEED_VER [y/n] : "  -e pagespeed
done

if [[ ! -d /usr/local/src/nginx/modules ]];then
	mkdir -p /usr/local/src/nginx/modules >> /tmp/nginx-autoinstall.log 2>&1
fi

echo "deb http://ftp.debian.org/debian stretch-backports main" > /etc/apt/sources.list.d/backports.list


echo "       Update and Upgrade                "
apt-get update -qq && apt-get upgrade > /dev/null 2>&1 & spinner

if [ $? -eq 0 ]; then
	echo -ne "       Update and Upgrade                [${green}OK${reset}]"
	echo -ne "\n"
else
	echo -e "        Update and Upgrade                [${red}FAIL${reset}]"
	echo ""
	echo "Veuillez regarder les logs :  /tmp/nginx-autoinstall.log"
	echo ""
	exit 1
fi

apt-get install screen build-essential ca-certificates wget curl libpcre3 libpcre3-dev  net-tools autoconf unzip automake libtool tar git libssl-dev zlib1g-dev uuid-dev  python-pip gcc -y >> /tmp/nginx-autoinstall.log 2>&1 
if [ $? -eq 0 ]; then
	echo -ne "       Installation des dependances      [${green}OK${reset}]\r"
	echo -ne "\n"
else
	echo -ne "       Installation des dependances      [${red}FAIL${reset}]"
	echo ""
	echo "Veuillez regarder les logs :  /tmp/nginx-autoinstall.log"
	echo ""
	exit 1
fi


cd /usr/local/src/nginx
wget http://nginx.org/download/nginx-${nginx_version}.tar.gz  >> /tmp/nginx-autoinstall.log 2>&1 
tar -xvzf nginx-${nginx_version}.tar.gz >> /tmp/nginx-autoinstall.log 2>&1
cd nginx-${nginx_version}

if [ $? -eq 0 ]; then
	echo -ne "       Telechargement de Nginx           [${green}OK${reset}]"
	echo -ne "\n"
else
	echo -e "        Telechargement de Nginx           [${red}FAIL${reset}]"
	echo ""
	echo "Veuillez regarder les logs :  /tmp/nginx-autoinstall.log"
	echo ""
	exit 1
fi


if [[ $pagespeed == 'y' ]];then 
	cd /usr/local/src/nginx/modules
	wget https://github.com/pagespeed/ngx_pagespeed/archive/v${PAGESPEED_VER}-stable.zip >> /tmp/nginx-autoinstall.log 2>&1
	unzip v${PAGESPEED_VER}-stable.zip >> /tmp/nginx-autoinstall.log 2>&1
	cd /usr/local/src/nginx/modules/incubator-pagespeed-ngx-${PAGESPEED_VER}-stable

	psol_url=https://dl.google.com/dl/page-speed/psol/${PAGESPEED_VER}-x64.tar.gz >> /tmp/nginx-autoinstall.log 2>&1 
	wget $psol_url  >> /tmp/nginx-autoinstall.log 2>&1
	tar -xzvf ${PAGESPEED_VER}-x64.tar.gz  >> /tmp/nginx-autoinstall.log 2>&1

	touch /var/ngx_pagespeed_cache
	chown -R www-data:www-data /var/ngx_pagespeed_cache
	#setfacl -m u:nginx:rwx  /var/ngx_pagespeed_cache
	#wget -O /usr/local/src/nginx/nginx-${nginx_version}/conf/nginx.conf  https://raw.githubusercontent.com/ashura82/Evagroup/master/pagespeed_conf  >> /tmp/nginx-autoinstall.log 2>&1  

if [ $? -eq 0 ]; then
	echo -ne "       Telechargement de Pagespeed       [${green}OK${reset}]"
	echo -ne "\n"
else
	echo -e "        Telechargement de Pagespeed      [${red}FAIL${reset}]"
	echo ""
	echo "Veuillez regarder les logs :  /tmp/nginx-autoinstall.log"
	echo ""
	exit 1
fi
fi
#
#cd /temp
#wget http://nginx.org/keys/nginx_signing.key
#apt-key add nginx_signing.key
#echo "deb http://nginx.org/packages/mainline/debian/ stretch nginx" >> /etc/apt/sources.list
#apt-get update
#apt-get install nginx

NGINX_OPTIONS="\
	--prefix=/etc/nginx \
	--sbin-path=/usr/sbin/nginx \
	--conf-path=/etc/nginx/nginx.conf \
	--error-log-path=/var/log/nginx/error.log \
	--http-log-path=/var/log/nginx/access.log \
	--pid-path=/var/run/nginx.pid \
	--lock-path=/var/run/nginx.lock \
	--http-client-body-temp-path=/var/cache/nginx/client_temp \
	--http-proxy-temp-path=/var/cache/nginx/proxy_temp \
	--http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp \
	--user=nginx \
	--group=nginx \
	--with-cc-opt=-Wno-deprecated-declarations"


NGINX_MODULES="\
	--without-http_ssi_module \
	--without-http_scgi_module \
	--without-http_uwsgi_module \
	--without-http_geo_module \
	--without-http_split_clients_module \
	--without-http_memcached_module \
	--without-http_empty_gif_module \
	--without-http_browser_module \
	--with-threads \
	--with-file-aio \
	--with-http_ssl_module \
	--with-http_v2_module \
	--with-http_mp4_module \
	--with-http_auth_request_module \
	--with-http_slice_module \
	--with-http_stub_status_module \
	--with-http_realip_module"
NGINX_MOD_OPT="--user=nginx                          \
	--group=nginx                         \
	--prefix=/etc/nginx                   \
	--sbin-path=/usr/sbin/nginx           \
	--conf-path=/etc/nginx/nginx.conf     \
	--pid-path=/var/run/nginx.pid         \
	--lock-path=/var/run/nginx.lock       \
	--error-log-path=/var/log/nginx/error.log \
	--http-log-path=/var/log/nginx/access.log \
	--with-http_gzip_static_module        \
	--with-http_stub_status_module        \
	--with-http_ssl_module                \
	--with-pcre                           \
	--with-file-aio                       \
	--with-http_realip_module             \
	--without-http_scgi_module            \
	--without-http_uwsgi_module           \
	--without-http_fastcgi_module"




if [[ $pagespeed == 'y' ]];then 
	NGINX_MOD_OPT=$(echo $NGINX_MOD_OPT;echo "--add-dynamic-module=/usr/local/src/nginx/modules/incubator-pagespeed-ngx-${PAGESPEED_VER}-stable")
	#NGINX_MODULES=$(echo $NGINX_MODULES;echo "--add-dynamic-module=/usr/local/src/nginx/modules/incubator-pagespeed-ngx-${PAGESPEED_VER}-stable")
fi


cd /usr/local/src/nginx/nginx-${nginx_version}
./configure $NGINX_MOD_OPT >> /tmp/nginx-autoinstall.log 2>&1
#./configure $NGINX_OPTIONS $NGINX_MODULES >> /tmp/nginx-autoinstall.log 2>&1

if [ $? -eq 0 ]; then
	echo -ne "       Configuration de Nginx            [${green}OK${reset}]"
	echo -ne "\n"
else
	echo -e "        Configuration de Nginx            [${red}FAIL${reset}]"
	echo ""
	echo "Veuillez regarder les logs :  /tmp/nginx-autoinstall.log"
	echo ""
	exit 1
fi
make -j $(nproc) >> /tmp/nginx-autoinstall.log 2>&1
if [ $? -eq 0 ]; then
	echo -ne "       Compilation de Nginx              [${green}OK${reset}]"
	echo -ne "\n"
else
	echo -e "        Compilation de Nginx              [${red}FAIL${reset}]"
	echo ""
	echo "Veuillez regarder les logs :  /tmp/nginx-autoinstall.log"
	echo ""
	exit 1
fi

make install >> /tmp/nginx-autoinstall.log 2>&1
if [ $? -eq 0 ]; then
	echo -ne "       Installation  de Nginx            [${green}OK${reset}]"
	echo -ne "\n"
else
	echo -e "        Installation  de Nginx            [${red}FAIL${reset}]"
	echo ""
	echo "Veuillez regarder les logs :  /tmp/nginx-autoinstall.log"
	echo ""
	exit 1
fi
cd /usr/local/src/nginx/nginx-${nginx_version}/conf
ln -sf  /etc/nginx/nginx.conf  /usr/local/src/nginx/nginx-${nginx_version}/conf/nginx.conf 


if [[ ! -d /etc/nginx/sites-available ]]; then
	mkdir -p /etc/nginx/sites-available
fi

rc2=$?

if [[ ! -d /etc/nginx/sites-enabled ]]; then
	mkdir -p /etc/nginx/sites-enabled	
fi
rc3=$?



if [[ ! -d /var/cache/nginx ]]; then
	mkdir -p /var/cache/nginx
fi


id -u nginx > /dev/null 2>&1
if [ $? -eq 1 ]; then
	useradd -r nginx
fi


if [[ ! -f /etc/init.d/nginx ]]; then
	wget -O /etc/init.d/nginx https://raw.githubusercontent.com/ashura82/Evagroup/master/nginx > /dev/null 2>&1
	chmod +x /etc/init.d/nginx
	update-rc.d nginx defaults
fi

apt-get install python-certbot-nginx -y -Y -t stretch-backports >> /tmp/nginx-autoinstall.log > /dev/null 2>&1 

if [[ ! -d "/opt/certbot" ]]; then 
	mkdir /opt/certbot
fi

cd /opt/certbot
wget -O /opt/certbot/certbot-auto  https://dl.eff.org/certbot-auto  > /dev/null 2>&1
chmod a+x /opt/certbot/certbot-auto


if [ $? -eq 0 ]; then
	echo -ne "       Installation CertBot              [${green}OK${reset}]"
	echo -ne "\n"
else
	echo -e "       Installation CertBot                [${red}FAIL${reset}]"
	echo ""
	echo "Veuillez regarder les logs :  /tmp/nginx-autoinstall.log"
	echo ""
	exit 1
fi

id -u user1 > /dev/null 2>&1
if [ $? -eq 1 ]; then 
	groupadd adm
	useradd -g adm user1 
fi

pip install flask > /dev/null 2>&1
pip install psutil  > /dev/null 2>&1
pip install linux_metrics > /dev/null 2>&1
pip install pathlib2 > /dev/null 2>&1




if [[ ! -d "/opt/flask" ]]; then
	mkdir /opt/flask
fi

cd /opt/flask
wget https://github.com/ashura82/Evagroup_Reverse/raw/master/ressources/venv.tar.gz >> /tmp/flask-install.log 2>&1
tar -xvf venv.tar.gz >> /tmp/flask-install.log 2>&1
rm venv.tar.gz

#virtualenv /opt/flask/venv/
# Init

wget https://raw.githubusercontent.com/ashura82/Evagroup_Reverse/master/script/api.py >> /tmp/flask-install.log 2>&1
chmod +x api.py

source /opt/flask/venv/bin/activate
export FLASK_APP="/opt/flask/api.py"
screen -d -m flask run --host 0.0.0.0 --port 8010 >> /tmp/flask-install.log 2>&1

#netstat -tulpn | grep 8010 > /dev/null 2>&1
 
if [ $? -eq 0 ]; then
	echo -ne "       Installation et déploiement de l'api      [${green}OK${reset}]\n"
	echo -ne "	 Fichier log : /tmp/nginx-autoinstall.log\n"
	echo -ne "	 Fichier Version Nginx /tmp/nginx_ver\n"
	echo -ne "\n"
else
	echo -e "        Installation et déploiement de l'api      [${red}FAIL${reset}]"
	echo ""
	echo "Veuillez regarder les logs :  /tmp/flask-install.log"
	echo ""
	exit 1
fi

if [ $? -eq 0 ]; then
	echo -ne "       Installation & Configuration      [${green}OK${reset}]\n"
	echo -ne "	 Fichier log : /tmp/nginx-autoinstall.log\n"
	echo -ne "	 Fichier Version Nginx /tmp/nginx_ver\n"
	echo -ne "\n"
else
	echo -e "        Installation & Configuration         [${red}FAIL${reset}]"
	echo ""
	echo "Veuillez regarder les logs :  /tmp/nginx-autoinstall.log"
	echo ""
	exit 1
fi

