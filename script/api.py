#! /usr/bin/python
# -*- coding:utf-8 -*-
import os
import time
import os.path
import sys
import json
import psutil
import commands
import subprocess
from linux_metrics import cpu_stat, mem_stat, disk_stat, net_stat
from flask import Flask, jsonify, request, render_template_string, render_template
from pathlib2 import Path

app = Flask(__name__)


#########################
#   Gestion des Vhosts  #
#########################

@app.route('/details/<vhost>')
#A JOUR
def details(vhost):
    data = []
    item = {'name': vhost}
    item['conf']=Path("/etc/nginx/sites-available/%s" % vhost).read_text()
    item['active'] = os.path.exists("/etc/nginx/sites-enabled/%s" % vhost)
    data.append(item)
    jason = json.dumps(data)
    return jason


@app.route('/add_vhost/', methods=['POST'])
def add_vhost():
    if request.method == 'POST':
        vhost = request.form['vhost']
        ip = request.form['ip']
        port = request.form['port']
        mail = request.form['mail']
        with open("/etc/nginx/sites-available/%s" % vhost, "wb") as fo:
            fo.write(render_template(
                'new-vhost', vhost=vhost, port=port, ip=ip))
        # AJOUTER CERT BOT
        os.chdir("/opt/certbot/")
        subprocess.call(
            "echo 2 |  ./certbot-auto  --nginx --email %s --agree-tos  -d %s" % mail, vhost, True)
    return "Ajout réussi"


@app.route('/remove_vhost/<vhost>')
def remove_vhost(vhost):
    import shutil
    shutil.rmtree('/etc/nginx/sites-available/%s' % vhost)
    path = "/etc/nginx/sites-available/"
    dirs = os.listdir(path)
    return "%s" % dirs


@app.route('/view_vhosts')
def view_vhosts():
    path = "/etc/nginx/sites-available/"
    dirs = os.listdir(path)
    print dirs
    data = []
    for vhost in dirs:
        item = {"name": vhost}
        for attribute in vhost:
            item["last_modified"] = time.ctime(
                os.path.getmtime("/etc/nginx/sites-available/%s" % vhost))
        item["active"] = os.path.exists("/etc/nginx/sites-enabled/%s" % vhost)
        data.append(item)
    jason = json.dumps(data)
    return jason


#############################
#  Verification des status  #
#############################

@app.route('/nginx_status')
def nginx_status():
    cmd = 'systemctl status nginx'
    var = subprocess.check_output(cmd, shell=True)
    if var:
        var = "0"
    else:
        var = "1"
    return var

#######################
#  Gestion des logs   #
#######################


@app.route('/logs/<file>')
def logs(file):
    contents = Path("/var/log/%s" % file).read_text()
    return contents


@app.route('/logs_csf/<file>')
def logs_csf(file):
    contents = Path("/etc/csf/%s" % file).read_text()
    return contents

# /var/log/deamon.log
# /var/log/lfd.log
# /var/log/messages
# /var/log/auth.log
# /etc/csf/csf.allow
# /etc/csf/csf.deny


#########################
# Gestion des métriques #
#########################


def sizeof_fmt(num, suffix='B'):
    for unit in ['', ' Ki', ' Mi', ' Gi', ' Ti', ' Pi', ' Ei', ' Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


@app.route('/metrics')
def metrics():
    # cpu
    cpu = psutil.cpu_percent()
    item = {"cpu": cpu}

    # memory
    mem_t = psutil.virtual_memory()[0] / 1024 ** 2
    item["mem_t"] = mem_t

    mem_a = psutil.virtual_memory()[1] / 1024 ** 2
    item["mem_a"] = mem_a

    mem_u = psutil.virtual_memory()[3] / 1024 ** 2
    item["mem_u"] = mem_u

    # network
    rx_bits, tx_bits = net_stat.rx_tx_bits('ens224')
    net_r = sizeof_fmt(rx_bits)
    item["net_r"] = net_r

    net_s = sizeof_fmt(tx_bits)
    item["net_s"] = net_s

    # disk
    disk_t = psutil.disk_usage('/')[0] / 1024 ** 3
    item["disk_total"] = disk_t

    disk_u = psutil.disk_usage('/')[1] / 1024 ** 3
    item["disk_usage"] = disk_u

    disk_f = psutil.disk_usage('/')[2] / 1024 ** 3
    item["disk_free"] = disk_f

    disk_p = psutil.disk_usage('/')[3]
    item["disk_percent_used"] = disk_p

    jason = json.dumps(item)
    return jason

###########################
#   Configuration CSF     #
###########################


@app.route('/start_csf')
def start_csf():
    cmd_start_csf = 'csf -e'
    subprocess.call(cmd_start_csf, shell=True)
    return "Demarrage de csf"


@app.route('/shutdown_csf')
def shut_csf():
    cmd_shut_csf = 'csf -x'
    subprocess.call(cmd_shut_csf, shell=True)
    return "Arret de csf"


@app.route('/unlock_csf_ip/<ip>')
def unblock_ip_csf(ip):
    cmd_unblock_ip_csf = 'csf -cr %s' % ip
    cmd_unblock_ip_csf2 = 'csf -dr %s' % ip
    subprocess.call(cmd_unblock_ip_csf, shell=True)
    subprocess.call(cmd_unblock_ip_csf2, shell=True)
    return "L'ip %s est debloquee" % ip


@app.route('/allow_csf_ip/<ip>')
def allow_ip_csf(ip):
    cmd_allow_ip = 'csf -ca %s ' % ip
    cmd_allow_ip2 = 'csf -a %s ' % ip
    subprocess.call(cmd_allow_ip, shell=True)
    subprocess.call(cmd_allow_ip2, shell=True)
    return "L'ip %s est maintenant autorisee" % ip


@app.route('/restart_csf')
def restart_csf():
    cmd_restart_csf = 'csf -ra'
    cmd_restart_csf2 = 'csf -crs'
    subprocess.call(cmd_restart_csf, shell=True)
    subprocess.call(cmd_restart_csf2, shell=True)
    return "Restart CSF ok"


@app.route('/deny_csf_ip/<ip>')
def deny_ip_csf(ip):
    cmd_deny_ip_csf = 'csf -cd %s' % ip
    cmd_deny_ip_csf2 = 'csf -d %s' % ip
    subprocess.call(cmd_deny_ip_csf, shell=True)
    subprocess.call(cmd_deny_ip_csf2, shell=True)
    return "L'ip %s est banni" % ip


@app.route('/grep_csf_ip/<ip>')
def grep_ip_csf(ip):
    cmd_grep_ip_csf = 'csf -g %s' % ip
    var = subprocess.check_output(cmd_grep_ip_csf, shell=True)
    return var


@app.route('/list_csf_iptable')
def list_iptable_csf():
    cmd_list_iptable_csf = 'csf -l'
    var = subprocess.check_output(cmd_list_iptable_csf, shell=True)
    return var


@app.route('/ping_ip_csf/<ip>')
def ping_ip_csf(ip):
    cmd_ping_ip_csf = 'csf -cp %s' % ip
    var = subprocess.check_output(cmd_ping_ip_csf, shell=True)
    return var


@app.route('/remove_csf_ip/<ip>')
def remove_csf_ip(ip):
    cmd_remove_ip_csf = 'csf -car %s' % ip
    cmd_remove_ip_csf2 = 'csf -ar %s' % ip
    subprocess.call(cmd_remove_ip_csf, shell=True)
    subprocess.call(cmd_remove_ip_csf2, shell=True)
    return "L'IP %s est supprimée" % ip


if __name__ == '__main__':
    app.run(debug=True)

