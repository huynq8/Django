# used to cleanup acl
#case 1: rule on SRX not on EX
#case 2: rule on EX not on SRX
from pprint import pprint
from netaddr import *
import os
#from delete_acl import xuat_rule_srx, xuat_rule_ex, filter_rule_ex, filter_rule_srx
#from edit_acl import vlan_inf
import re
import xlwt
import time
def filter_rule_srx(srx_file):
    list_rule_srx=[]
    with open(srx_file,'r') as f1:
        for line in f1.readlines():
            if "security policies from-zone" in line or "system host-name" in line:
                list_rule_srx.append(line)
    return  list_rule_srx
def filter_rule_ex(ex_file):
    list_rule_ex=[]
    with open(ex_file,'r') as f2:
        for line in f2.readlines():
            if "firewall family inet filter" in line or "system host-name" in line:
                list_rule_ex.append(line)
    return list_rule_ex
def xuat_rule_ex(file,vlan_info):
    dict_app={'ftp': '21', 'klogin':'543','tftp': '69', 'rtsp': '554', 'netbios-session': '139', 'smb-session': '445', \
              'ssh': '22', 'telnet': '23', 'smtp': '25', 'tacacs': '49', 'tacacs-ds': '65', \
              'dhcp-client': '68', 'dhcp-server': '67', 'bootpc': '68', 'bootps': '67', 'finger': '79', \
              'http': '80', 'https': '443', 'pop3': '110', 'ident': '113', 'nntp': '119', 'ntp': '123', \
              'imap': '143', 'imaps': '993', 'bgp': '179', 'ldap': '389', 'snpp': '444', 'biff': '512', \
              'who': '513', 'syslog': '514', 'printer': '515', 'rip': '520', 'radius': '1812', 'radacct': '1813', \
              'nfsd-tcp': '2049', 'nfsd-udp': '2049', 'cvspserver': '2401', 'ldp-tcp': '646', 'ldp-udp': '646', \
              'xnm-ssl': '3220', 'xnm-clear-text': '3221', 'ike': '500', 'snmp-get': '161', 'snmp-get-next': '161', \
              'snmp-trap': '162', 'citrix-winframe': '1494', 'citrix-winframe-udp': '1604', 'h323': '1720', \
              'iiop-java': '1975', 'iiop-orbix': '3075', 'netshow': '1755', 'netbios-name-udp': '137',\
              'netbios-name-tcp': '137', 'netbios-datagram': '138', 'talk-tcp': '517', 'talk-udp': '517', \
              'ntalk': '518', 'rexec': '512', 'rlogin': '513', 'traceroute': '33434-33450', \
              'traceroute-ttl-1': '33434-33450', 'h323-ras': '1719', 'sip': '5060', 'sqlnet': '1521', \
              'realaudio': '7070', 'rpc-portmap-tcp': '111', 'rpc-portmap-udp': '111', 'rsh': '514', 'dns-udp': '53', \
              'dns-tcp': '53', 'pptp': '1723', 'dce-rpc-portmap': '135','domain':'53'}
    dict_={}
    dict_conf = {}
    protocol = []
    srcIP = []
    destIP = []
    destport = []
    config = []
    sourceport = []
    sourcename = {'hostname': 'UNKNOW', 'vlan': 'UNKNOW'}
    destname = {'hostname': 'UNKNOW', 'vlan': 'UNKNOW'}
    hostname = "UNKNOW"
    for item in file:
        try:
            # print(re.search("set (.*) system host-name (.*)",item).group(2))
            hostname = re.search("set[a-zA-Z0-9\s]+system host-name (.*)", item).group(1)
            break
            # print(hostname)
        except:
            pass
    for line in file:
        m = 0
        if 'source-address' in line:
            config.append(line)
            line = line[line.find('source-address') + 15:].strip()
            srcIP.append(line)
        elif 'destination-address' in line:
            config.append(line)
            line = line[line.find('destination-address') + 20:].strip()
            destIP.append(line)
        elif "protocol" in line:
            config.append(line)
            protocol.append(line[line.find('protocol') + 9:].strip())
        elif "source-port" in line:
            config.append(line)
            for key in dict_app:
                if line[line.find('source-port') + 12:].strip() == str(key):
                    sourceport.append(str(dict_app[key]))
                    m=1
                    break
            if m!=1:
                sourceport.append(line[line.find('source-port') + 12:].strip())
        elif "destination-port" in line:
            config.append(line)
            for key in dict_app:
                if line[line.find('destination-port') + 17:].strip() == str(key):
                    destport.append(str(dict_app[key]))
                    m=1
                    break
            if m!=1:
                destport.append(line[line.find('destination-port') + 17:].strip())
        elif "then accept" in line:
            fzone="UNKNOW"
            tzone="UNKNOW"
            config.append(line)
            term = line[line.find('term') + 5:line.find('then') - 1]
            firewall_name = line[line.find('firewall family inet filter') + 28:line.find('term') - 1]
            if "any" in srcIP or srcIP==[]:
                srcIP=["any"]
            if "any" in destIP or destIP==[]:
                destIP=["any"]
            if "any" in sourceport or sourceport==[]:
                sourceport = ["any"]
            if "any" in destport or destport==[]:
                destport = ["any"]
            if "any" in protocol or protocol==[]:
                protocol=["any"]
            try:
                for vlan in vlan_info:
                    if IPNetwork(srcIP[0]) in IPNetwork(vlan):
                        sourcename=vlan_info[vlan]
                        break
            except:
                pass
            try:
                for vlan in vlan_info:
                    if IPNetwork(destIP[0]) in IPNetwork(vlan):
                        destname=vlan_info[vlan]
                        break
            except:
                pass
            # check rule multiple source or destination vlan
            tag = ""
            try:
                for ip in srcIP:
                    if IPNetwork(str(IPNetwork(srcIP[0]).ip)+"/24") not in IPNetwork(str(IPNetwork(ip).ip)+"/24"):
                        tag = "rule multiple source vlan"
                        break
            except:
                pass
            try:
                for ip in destIP:
                    if IPNetwork(str(IPNetwork(destIP[0]).ip)+"/24") not in IPNetwork(str(IPNetwork(ip).ip)+"/24"):
                        tag = "rule multiple destination vlan"
                        break
            except:
                pass
            fzone=sourcename['vlan']
            tzone=destname['vlan']
            dict_term = {"term":term,"sourceip": sorted(srcIP), "destip": sorted(destIP), "sourceport":sorted(sourceport),"destport": sorted(destport),\
                         "protocol":sorted(protocol),"ins":firewall_name,"sourcename":sourcename,"destname":destname,\
                         'fzone':fzone,'tzone':tzone,'hostname':hostname,'config':config,"tag":tag}
            try:
                if dict_[term+"_"+firewall_name]:
                    dict_.update([(term+"_"+firewall_name+"_2", dict_term)])
                    dict_conf.update([(term + "_" + firewall_name+"_2", config)])
            except:
                dict_.update([(term + "_" + firewall_name, dict_term)])
                dict_conf.update([(term + "_" + firewall_name, config)])
            dict_term = {}
            srcIP = []
            destIP = []
            lst_destport = []
            destport = []
            config = []
            protocol = []
            sourceport = []
            sourcename = {'hostname': 'UNKNOW', 'vlan': 'UNKNOW'}
            destname = {'hostname': 'UNKNOW', 'vlan': 'UNKNOW'}
    return dict_, dict_conf
def hitcount(list_hitcount):
    dict_hitcount={}
    for file in list_hitcount:
        list_hitcount=open(file,"r").readlines()
        for item in list_hitcount:
            try:
                list_tem=re.split("\s+",item)
                list_tem.remove("")
                list_tem.remove('')
                key=list_tem[3]+"_"+list_tem[1]+"_"+list_tem[2]
                dict_hitcount.update([(key,list_tem[4])])
            except:
                pass
    #print(dict_hitcount["T9_EXTERNAL_VLAN447"])
    return dict_hitcount
def xuat_rule_srx(file,vlan_info):#,hit_count):
    dict_app_ex={'ftp': '21', 'klogin':'543','tftp': '69', 'rtsp': '554', 'netbios-session': '139', 'smb-session': '445', \
              'ssh': '22', 'telnet': '23', 'smtp': '25', 'tacacs': '49', 'tacacs-ds': '65', \
              'dhcp-client': '68', 'dhcp-server': '67', 'bootpc': '68', 'bootps': '67', 'finger': '79', \
              'http': '80', 'https': '443', 'pop3': '110', 'ident': '113', 'nntp': '119', 'ntp': '123', \
              'imap': '143', 'imaps': '993', 'bgp': '179', 'ldap': '389', 'snpp': '444', 'biff': '512', \
              'who': '513', 'syslog': '514', 'printer': '515', 'rip': '520', 'radius': '1812', 'radacct': '1813', \
              'nfsd-tcp': '2049', 'nfsd-udp': '2049', 'cvspserver': '2401', 'ldp-tcp': '646', 'ldp-udp': '646', \
              'xnm-ssl': '3220', 'xnm-clear-text': '3221', 'ike': '500', 'snmp-get': '161', 'snmp-get-next': '161', \
              'snmp-trap': '162', 'citrix-winframe': '1494', 'citrix-winframe-udp': '1604', 'h323': '1720', \
              'iiop-java': '1975', 'iiop-orbix': '3075', 'netshow': '1755', 'netbios-name-udp': '137',\
              'netbios-name-tcp': '137', 'netbios-datagram': '138', 'talk-tcp': '517', 'talk-udp': '517', \
              'ntalk': '518', 'rexec': '512', 'rlogin': '513', 'traceroute': '33434-33450', \
              'traceroute-ttl-1': '33434-33450', 'h323-ras': '1719', 'sip': '5060', 'sqlnet': '1521', \
              'realaudio': '7070', 'rpc-portmap-tcp': '111', 'rpc-portmap-udp': '111', 'rsh': '514', 'dns-udp': '53', \
              'dns-tcp': '53', 'pptp': '1723', 'dce-rpc-portmap': '135','domain':'53'}
    dict_app={'junos-ftp': {'protocol': 'tcp', 'port': '21'}, 'junos-tftp': {'protocol': 'udp', 'port': '69'},\
              'junos-rtsp': {'protocol': 'tcp', 'port': '554'}, 'junos-netbios-session': {'protocol': 'tcp', 'port': '139'},\
              'junos-smb-session': {'protocol': 'tcp', 'port': '445'}, 'junos-ssh': {'protocol': 'tcp', 'port': '22'},\
              'junos-telnet': {'protocol': 'tcp', 'port': '23'}, 'junos-smtp': {'protocol': 'tcp', 'port': '25'},\
              'junos-tacacs': {'protocol': 'tcp', 'port': '49'}, 'junos-tacacs-ds': {'protocol': 'tcp', 'port': '65'}, \
              'junos-dhcp-client': {'protocol': 'udp', 'port': '68'}, 'junos-dhcp-server': {'protocol': 'udp', 'port': '67'},\
              'junos-bootpc': {'protocol': 'udp', 'port': '68'}, 'junos-bootps': {'protocol': 'udp', 'port': '67'},\
              'junos-finger': {'protocol': 'tcp', 'port': '79'}, 'junos-http': {'protocol': 'tcp', 'port': '80'},\
              'junos-https': {'protocol': 'tcp', 'port': '443'}, 'junos-pop3': {'protocol': 'tcp', 'port': '110'},\
              'junos-ident': {'protocol': 'tcp', 'port': '113'}, 'junos-nntp': {'protocol': 'tcp', 'port': '119'},\
              'junos-ntp': {'protocol': 'udp', 'port': '123'}, 'junos-imap': {'protocol': 'tcp', 'port': '143'}, \
              'junos-imaps': {'protocol': 'tcp', 'port': '993'}, 'junos-bgp': {'protocol': 'tcp', 'port': '179'}, \
              'junos-ldap': {'protocol': 'tcp', 'port': '389'}, 'junos-snpp': {'protocol': 'tcp', 'port': '444'},\
              'junos-biff': {'protocol': 'udp', 'port': '512'}, 'junos-who': {'protocol': 'udp', 'port': '513'},\
              'junos-syslog': {'protocol': 'udp', 'port': '514'}, 'junos-printer': {'protocol': 'tcp', 'port': '515'},\
              'junos-rip': {'protocol': 'udp', 'port': '520'}, 'junos-radius': {'protocol': 'udp', 'port': '1812'},\
              'junos-radacct': {'protocol': 'udp', 'port': '1813'}, 'junos-nfsd-tcp': {'protocol': 'tcp', 'port': '2049'},\
              'junos-nfsd-udp': {'protocol': 'udp', 'port': '2049'}, 'junos-cvspserver': {'protocol': 'tcp', 'port': '2401'},\
              'junos-ldp-tcp': {'protocol': 'tcp', 'port': '646'}, 'junos-ldp-udp': {'protocol': 'udp', 'port': '646'},\
              'junos-xnm-ssl': {'protocol': 'tcp', 'port': '3220'},\
              'junos-xnm-clear-text': {'protocol': 'tcp', 'port': '3221'}, 'junos-ike': {'protocol': 'udp', 'port': '500'},\
              'any term t1': {'protocol': '0'}, 'junos-aol term t1': {'protocol': '6', 'port': '5190-5193'},\
              'junos-chargen term t1': {'protocol': 'udp', 'port': '19'}, \
              'junos-dhcp-relay term t1': {'protocol': 'udp', 'port': '67'},\
              'junos-discard term t1': {'protocol': 'udp', 'port': '9'}, \
              'junos-dns-udp term t1': {'protocol': 'udp', 'port': '53'},\
              'junos-dns-tcp term t1': {'protocol': 'tcp', 'port': '53'},\
              'junos-echo term t1': {'protocol': 'udp', 'port': '7'}, \
              'junos-gopher term t1': {'protocol': 'tcp', 'port': '70'}, \
              'junos-gnutella term t1': {'protocol': 'udp', 'port': '6346-6347'}, 'junos-gre term t1': {'protocol': '47','port':'0'},\
              'junos-gprs-gtp-c-tcp term t1': {'protocol': 'tcp', 'port': '2123'}, \
              'junos-gprs-gtp-c-udp term t1': {'protocol': 'udp', 'port': '2123'},\
              'junos-gprs-gtp-c term t1': {'protocol': 'tcp', 'port': '2123'},\
              'junos-gprs-gtp-c term t2': {'protocol': 'udp', 'port': '2123'}, \
              'junos-gprs-gtp-u-tcp term t1': {'protocol': 'tcp', 'port': '2152'}, \
              'junos-gprs-gtp-u-udp term t1': {'protocol': 'udp', 'port': '2152'}, \
              'junos-gprs-gtp-u term t1': {'protocol': 'tcp', 'port': '2152'},\
              'junos-gprs-gtp-u term t2': {'protocol': 'udp', 'port': '2152'}, \
              'junos-gprs-gtp-v0-tcp term t1': {'protocol': 'tcp', 'port': '3386'}, \
              'junos-gprs-gtp-v0-udp term t1': {'protocol': 'udp', 'port': '3386'},\
              'junos-gprs-gtp-v0 term t1': {'protocol': 'tcp', 'port': '3386'},\
              'junos-gprs-gtp-v0 term t2': {'protocol': 'udp', 'port': '3386'}, \
              'junos-gprs-sctp term t1': {'protocol': '132', 'port': '0'}, \
              'junos-http-ext term t1': {'protocol': 'tcp', 'port': '7001'},\
              'junos-icmp-all term t1': {'protocol': 'icmp'}, 'junos-icmp-ping term t1': {'protocol': 'icmp','port':'0'}, \
              'junos-internet-locator-service term t1': {'protocol': 'tcp', 'port': '389'}, \
              'junos-ike-nat term t1': {'protocol': 'udp', 'port': '4500'},\
              'junos-irc term t1': {'protocol': 'tcp', 'port': '6660-6669'}, \
              'junos-l2tp term t1': {'protocol': 'udp', 'port': '1701'},\
              'junos-lpr term t1': {'protocol': 'tcp', 'port': '515'}, \
              'junos-mail term t1': {'protocol': 'tcp', 'port': '25'},\
              'junos-h323 term t1': {'protocol': 'tcp', 'port': '1720'}, \
              'junos-h323 term t2': {'protocol': 'udp', 'port': '1719'},\
              'junos-h323 term t3': {'protocol': 'tcp', 'port': '1503'}, \
              'junos-h323 term t4': {'protocol': 'tcp', 'port': '389'}, \
              'junos-h323 term t5': {'protocol': 'tcp', 'port': '522'}, \
              'junos-h323 term t6': {'protocol': 'tcp', 'port': '1731'}, \
              'junos-mgcp-ua term t1': {'protocol': 'udp', 'port': '2427'}, \
              'junos-mgcp-ca term t1': {'protocol': 'udp', 'port': '2727'}, \
              'junos-msn term t1': {'protocol': 'tcp', 'port': '1863'}, \
              'junos-ms-rpc-tcp term t1': {'protocol': 'tcp', 'port': '135'},\
              'junos-ms-rpc-udp term t1': {'protocol': 'udp', 'port': '135'}, 'junos-ms-rpc-epm term t1': {'protocol': 'tcp'},\
              'junos-ms-rpc-msexchange-directory-rfr term t1': {'protocol': 'tcp'}, \
              'junos-ms-rpc-msexchange-info-store term t1': {'protocol': 'tcp'},\
              'junos-ms-rpc-msexchange-directory-nsp term t1': {'protocol': 'tcp'}, \
              'junos-ms-rpc-wmic-admin term t1': {'protocol': 'tcp'}, 'junos-ms-rpc-wmic-webm-level1login term t1': \
                  {'protocol': 'tcp'}, 'junos-ms-rpc-wmic-webm-objectsink term t1': {'protocol': 'tcp'},\
              'junos-ms-rpc-wmic-webm-services term t1': {'protocol': 'tcp'}, 'junos-ms-rpc-wmic-webm-callresult term t1': \
                  {'protocol': 'tcp'}, 'junos-ms-rpc-wmic-webm-login-clientid term t1': {'protocol': 'tcp'}, \
              'junos-ms-rpc-wmic-webm-login-helper term t1': {'protocol': 'tcp'},\
              'junos-ms-rpc-wmic-webm-refreshing-services term t1': {'protocol': 'tcp'}, \
              'junos-ms-rpc-wmic-webm-remote-refresher term t1': {'protocol': 'tcp'}, 'junos-ms-rpc-wmic-webm-shutdown term t1':\
                  {'protocol': 'tcp'}, 'junos-ms-rpc-wmic-webm-classobject term t1': {'protocol': 'tcp'}, \
              'junos-ms-rpc-wmic-admin2 term t1': {'protocol': 'tcp'}, 'junos-ms-rpc-wmic-mgmt term t1': {'protocol': 'tcp'},\
              'junos-ms-rpc-iis-com-1 term t1': {'protocol': 'tcp'}, 'junos-ms-rpc-iis-com-adminbase term t1': {'protocol': 'tcp'},\
              'junos-ms-rpc-uuid-any-tcp term t1': {'protocol': 'tcp'}, 'junos-ms-rpc-uuid-any-udp term t1': {'protocol': 'udp'},\
              'junos-ms-sql term t1': {'protocol': 'tcp', 'port': '1433'},\
              'junos-nbname term t1': {'protocol': 'udp', 'port': '137'}, 'junos-nbds term t1': {'protocol': 'udp', 'port': '138'},\
              'junos-nfs term t1': {'protocol': 'udp', 'port': '111'}, \
              'junos-ns-global term t1': {'protocol': 'tcp', 'port': '15397'}, \
              'junos-ns-global-pro term t1': {'protocol': 'tcp', 'port': '15397'}, \
              'junos-nsm term t1': {'protocol': 'udp', 'port': '69'}, 'junos-ospf term t1': {'protocol': '89'}, \
              'junos-pc-anywhere term t1': {'protocol': 'udp', 'port': '5632'}, 'junos-ping term t1': {'protocol': '1'}, \
              'junos-pingv6 term t1': {'protocol': '58'}, 'junos-icmp6-dst-unreach-addr term t1': {'protocol': '58'}, \
              'junos-icmp6-dst-unreach-admin term t1': {'protocol': '58'}, \
              'junos-icmp6-dst-unreach-beyond term t1': {'protocol': '58'}, \
              'junos-icmp6-dst-unreach-port term t1': {'protocol': '58'}, \
              'junos-icmp6-dst-unreach-route term t1': {'protocol': '58'}, \
              'junos-icmp6-echo-reply term t1': {'protocol': '58'}, 'junos-icmp6-echo-request term t1': {'protocol': '58'},\
              'junos-icmp6-packet-too-big term t1': {'protocol': '58'}, 'junos-icmp6-param-prob-header term t1': {'protocol': '58'}, 'junos-icmp6-param-prob-nexthdr term t1': {'protocol': '58'}, 'junos-icmp6-param-prob-option term t1': {'protocol': '58'}, 'junos-icmp6-time-exceed-reassembly term t1': {'protocol': '58'}, 'junos-icmp6-time-exceed-transit term t1': {'protocol': '58'}, 'junos-icmp6-all term t1': {'protocol': '58'}, 'junos-pptp term t1': {'protocol': 'tcp', 'port': '1723'}, 'junos-realaudio term t1': {'protocol': 'tcp', 'port': '554'}, 'junos-sccp term t1': {'protocol': 'tcp', 'port': '2000'}, 'junos-sctp-any term t1': {'protocol': '132'}, 'junos-sip term t1': {'protocol': 'udp', 'port': '5060'}, 'junos-sip term t2': {'protocol': 'tcp', 'port': '5060'}, 'junos-rsh term t1': {'protocol': 'tcp', 'port': '514'}, 'junos-smb term t1': {'protocol': 'tcp', 'port': '139'}, 'junos-smb term t2': {'protocol': 'tcp', 'port': '445'}, 'junos-sql-monitor term t1': {'protocol': 'udp', 'port': '1434'}, 'junos-sqlnet-v1 term t1': {'protocol': 'tcp', 'port': '1525'}, 'junos-sqlnet-v2 term t1': {'protocol': 'tcp', 'port': '1521'}, 'junos-sun-rpc-tcp term t1': {'protocol': 'tcp', 'port': '111'}, 'junos-sun-rpc-udp term t1': {'protocol': 'udp', 'port': '111'}, 'junos-sun-rpc-portmap-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-portmap-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-nfs-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-nfs-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-mountd-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-mountd-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-ypbind-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-ypbind-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-status-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-status-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-ypserv-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-ypserv-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-rquotad-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-rquotad-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-nlockmgr-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-nlockmgr-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-ruserd-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-ruserd-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-sadmind-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-sadmind-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-sprayd-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-sprayd-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-walld-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-walld-udp term t1': {'protocol': 'udp'}, 'junos-sun-rpc-any-tcp term t1': {'protocol': 'tcp'}, 'junos-sun-rpc-any-udp term t1': {'protocol': 'udp'}, 'junos-talk term t1': {'protocol': 'udp', 'port': '517'}, 'junos-talk term t2': {'protocol': 'tcp', 'port': '517'}, 'junos-ntalk term t1': {'protocol': 'udp', 'port': '518'}, 'junos-ntalk term t2': {'protocol': 'tcp', 'port': '518'}, 'junos-tcp-any term t1': {'protocol': 'tcp'}, 'junos-udp-any term t1': {'protocol': 'udp'}, 'junos-uucp term t1': {'protocol': 'udp', 'port': '540'}, 'junos-vdo-live term t1': {'protocol': 'udp', 'port': '7000-7010'}, 'junos-vnc term t1': {'protocol': 'tcp', 'port': '5800'}, 'junos-wais term t1': {'protocol': 'tcp', 'port': '210'}, 'junos-whois term t1': {'protocol': 'tcp', 'port': '43'}, 'junos-winframe term t1': {'protocol': 'tcp', 'port': '1494'}, 'junos-x-windows term t1': {'protocol': 'tcp', 'port': '6000-6063'}, 'junos-ymsg term t1': {'protocol': 'tcp', 'port': '5000-5010'}, 'junos-ymsg term t2': {'protocol': 'tcp', 'port': '5050'}, 'junos-ymsg term t3': {'protocol': 'udp', 'port': '5000-5010'}, 'junos-ymsg term t4': {'protocol': 'udp', 'port': '5050'}, 'junos-wxcontrol term t1': {'protocol': 'tcp', 'port': '3578'}, 'junos-snmp-agentx term t1': {'protocol': 'tcp', 'port': '705'}, 'junos-stun term t1': {'protocol': 'udp', 'port': '3478-3479'}, 'junos-stun term t2': {'protocol': 'tcp', 'port': '3478-3479'}, 'junos-persistent-nat term t1': {'protocol': '255', 'port': '65535'}, 'junos-r2cp term t1': {'protocol': 'udp', 'port': '28672'}}
    action_list = ["then permit","then discard","then accept","then deny","then reject"]
    dict_ = {}
    dict_conf = {}
    protocol = []
    srcIP = []
    destIP = []
    destport = []
    config = []
    sourceport = []
    application = []
    fzone =""
    tzone= ""
    instance = ""
    sourcename = {'hostname': 'UNKNOW', 'vlan': 'UNKNOW'}
    destname = {'hostname': 'UNKNOW', 'vlan': 'UNKNOW'}
    hostname="UNKNOW"
    action = ""
    term =""
    for item in file:
        try:
            # print(re.search("set (.*) system host-name (.*)",item).group(2))
            hostname = re.search("set[a-zA-Z0-9\s]+system host-name (.*)_N0", item).group(1)
            break
            # print(hostname)
        except:
            try:
                hostname = re.search("set[a-zA-Z0-9\s]+system host-name (.*)", item).group(1)
            except:
                pass
            break
            pass
    for line in file:
        m = 0
        if re.search('(firewall|security policies).*(source-address)',line):
            config.append(line)
            line = line[line.find('source-address') + 15:].strip()
            srcIP.append(line)
        elif re.search('(firewall|security policies).*(destination-address)',line):
            config.append(line)
            line = line[line.find('destination-address') + 20:].strip()
            destIP.append(line)
        elif "protocol" in line:
            config.append(line)
            protocol.append(line[line.find('protocol') + 9:].strip())
        elif "source-port" in line:
            config.append(line)
            for key in dict_app_ex:
                if line[line.find('source-port') + 12:].strip() == str(key):
                    sourceport.append(str(dict_app_ex[key]))
                    m=1
                    break
            if m!=1:
                sourceport.append(line[line.find('source-port') + 12:].strip())
        elif "destination-port" in line:
            config.append(line)
            for key in dict_app_ex:
                if line[line.find('destination-port') + 17:].strip() == str(key):
                    destport.append(str(dict_app_ex[key]))
                    m=1
                    break
            if m!=1:
                destport.append(line[line.find('destination-port') + 17:].strip())

        elif 'application' in line:  # used for SRX
            config.append(line)
            line = line[line.find('application') + 12:]
            application.append(line)
            if 'any' not in line:
                if 'tcp' in line and 'udp' in line:
                    protocol = ['tcp', 'udp']
                    lst_destport = re.findall("[\d\-]+", line)
                    destport.extend(lst_destport)
                elif 'tcp' in line:
                    protocol = ['tcp']
                    lst_destport = re.findall("[\d\-]+", line)
                    destport.extend(lst_destport)
                elif 'udp' in line:
                    protocol = ['udp']
                    lst_destport = re.findall("[\d\-]+", line)
                    destport.extend(lst_destport)
                else:
                    for key in dict_app:
                        if line in str(key):
                            protocol.append(str(dict_app[key]['protocol']))
                            try:
                                destport.append(str(dict_app[key]['port']))
                            except:
                                destport.append('0')
                            m=1
                            break
                    if m!=1:
                        protocol.append(line)
                        destport.append(line)
            else:
                if 'tcp' in line and 'udp' in line:
                    protocol = ['tcp', 'udp']
                    #destport.append('any')
                elif 'tcp' in line:
                    protocol = ['tcp']
                    #destport.append('any')
                elif 'udp' in line:
                    protocol = ['udp']
                    #destport.append('any')
                else:
                    protocol = ['any']
                    #destport.append('any')
            try:
                destport = [x for x in destport if x != "-"]
            except:
                pass
        elif any(action in line for action in action_list): 
            config.append(line)
            if re.search("(policy|term)\s(.*)\sthen",line): term = re.search("(policy|term)\s(.*)\sthen",line).group(2)
            if re.search("groups\s(.*)\ssecurity",line): instance = re.search("groups\s(.*)\ssecurity",line).group(1)
            if re.search("from-zone\s(.*)\sto-zone",line): fzone = re.search("from-zone\s(.*)\sto-zone",line).group(1)
            if re.search("to-zone\s(.*)\spolicy",line): tzone = re.search("to-zone\s(.*)\spolicy",line).group(1)
            action = line[line.find('then') + 5:]
            if "EXTERNAL" in line[line.find('from-zone') + 10:line.find('to-zone') - 1]:
                type = "ex2vl"
            elif "EXTERNAL" in line[line.find('to-zone') + 8:line.find('policy') - 1]:
                type = "vl2ex"
            elif "PRIVATE" in line:
                 type = "internal"
            else:
                type = "vl2vl"
            if "any" in srcIP or srcIP==[]:
                srcIP=["any"]
            if "any" in destIP or destIP==[]:
                destIP=["any"]
            if "any" in sourceport or sourceport==[]:
                sourceport=["any"]
            if "any" in destport or destport==[]:
                destport=["any"]
            if "any" in protocol or protocol==[]:
                protocol=["any"]
            elif "tcp" in protocol and "udp" in protocol:
                protocol=["any"]
            ##update dict
            #destport = [x + "\n" for x in destport]
            try:
                for vlan in vlan_info:
                    if IPNetwork(srcIP[0]) in IPNetwork(vlan):
                        sourcename=vlan_info[vlan]
                        #sourcevlan="VLAN"+vlan_info[vlan]['vlan']
                        break
            except:
                pass
            try:
                for vlan in vlan_info:
                    if IPNetwork(destIP[0]) in IPNetwork(vlan):
                        destname=vlan_info[vlan]
                        #destvlan = "VLAN" + vlan_info[vlan]['vlan']
                        break
            except:
                pass
            # check rule multiple source or destination vlan
            tag = ""
            try:
                for ip in srcIP:
                    if IPNetwork(str(IPNetwork(srcIP[0]).ip)+"/24") not in IPNetwork(str(IPNetwork(ip).ip)+"/24"):
                        tag = "rule multiple source vlan"
                        break
            except:
                pass
            try:
                for ip in destIP:
                    if IPNetwork(str(IPNetwork(destIP[0]).ip)+"/24") not in IPNetwork(str(IPNetwork(ip).ip)+"/24"):
                        tag = "rule multiple destination vlan"
                        break
            except:
                pass
            #print(sourcename)
            #print(destname)
            hit="unknow"
            
            #print(hit)
            dict_term = {"term": term, "sourceip": sorted(srcIP), "destip": sorted(destIP), "sourceport": sorted(sourceport),\
                         "destport": sorted(destport),"protocol": sorted(protocol), "fzone": fzone, "tzone": tzone, "ins": instance,\
                         "type": type,"sourcename":sourcename,"destname":destname,'hostname':hostname,\
                         'application':application,'config':config,"tag":tag,"action":action}
            # print(dict_term)
            dict_.update([(term + "_" + fzone+"_"+tzone, dict_term)])
            dict_[term + "_" + fzone + "_" + tzone].update([("hitcount", hit)])
            dict_conf.update([(term + "_" + fzone+"_"+tzone, config)])
            dict_term = {}
            fzone =""
            tzone =""
            srcIP = []
            destIP = []
            lst_destport = []
            destport = []
            config = []
            protocol = []
            application = []
            action = ""
            term = ""
            sourcename = {'hostname': 'UNKNOW', 'vlan': 'UNKNOW'}
            destname = {'hostname': 'UNKNOW', 'vlan': 'UNKNOW'}
    return dict_, dict_conf
def dict_application_ex(file_application):#import file show configuration groups junos-defaults
    dict_app={}
    list_app=open(file_application,"r").readlines()
    for item in list_app:
        try:
            name=re.search("set groups junos-defaults applications application junos-(.*) destination-port (.*)",\
                           item).group(1)
            port = re.search("set groups junos-defaults applications application junos-(.*) destination-port (.*)",\
                         item).group(2)
            dict_app.update([(name, port)])
        except:
            pass
    return dict_app
def dict_application_srx(file_application): #import file show configuration groups junos-defaults
    dict_app = {}
    list_app = open(file_application, "r").readlines()
    for item in list_app:
        try:
            name = re.search("set groups junos-defaults applications application (.*) protocol (.*)", \
                             item).group(1)
            protocol = re.search("set groups junos-defaults applications application (.*) protocol (.*)", \
                             item).group(2)
            dict_app.update([(name,{"protocol":protocol})])
            dict_app[name].update([("protocol",protocol)])

        except:
            pass
        try:
            name = re.search("set groups junos-defaults applications application (.*) destination-port (.*)", \
                             item).group(1)
            port = re.search("set groups junos-defaults applications application (.*) destination-port (.*)", \
                                 item).group(2)
            dict_app[name].update([("port",port)])
        except:
            pass
    return dict_app

def vlan_inf(list_file):
    dict_inf={}
    dict_filter = {}
    hostname = "UNKNOW"
    for file in list_file:
        list_conf=open(file,"r").readlines()
        for item in list_conf:
            try:
                #print(re.search("set (.*) system host-name (.*)",item).group(2))
                hostname=re.search("set[a-zA-Z0-9\s]+system host-name (.*)_N[0-1]",item).group(1)
                break
                #print(hostname)
            except:
                pass
            try:
                #print(re.search("set (.*) system host-name (.*)",item).group(2))
                hostname=re.search("set[a-zA-Z0-9\s]+system host-name (.*)",item).group(1)
                break
                #print(hostname)
            except:
                pass
        #print(hostname)
        for item in list_conf:
            if re.search("set(.*)interfaces irb (.*)unit(.*)family inet filter (output|input) (.*)",item) and "interfaces fxp" not in item and "interfaces lo" not in item:
                key=re.search("set(.*)interfaces(.*)unit(.*)family inet filter (output|input) (.*)",item)
                vlan="VLAN" + str(key.group(3)).strip()
                filter=str(key.group(5)).strip()
                direct=str(key.group(4)).strip()
                #print(filter+vlan)
                dict_filter.update([(vlan,{"filter":filter,"direct":direct,"hostname":hostname})])
                #print(dict_filter[vlan])
            elif re.search("set(.*)interfaces (.*) unit (.*)family inet address(.*)",
                         item) and "interfaces fxp" not in item and "interfaces lo" not in item:
                #print(item)
                key = re.search("set(.*)interfaces (.*) unit (.*)family inet address(.*)", item)
                vlan = "VLAN" + str(key.group(3)).strip()
                address1=key.group(4)
                address = IPNetwork(address1[0:address1.find("/")+3]).cidr
                #print(address)
                dict_inf.update([(address, {"hostname": hostname, "vlan": vlan})])
    #print(dict_inf[IPNetwork('10.60.40.5/32\n').cidr])
    #print(IPNetwork('10.60.40.5/32\n')in IPNetwork("10.60.40.0/24"))
    return dict_inf, dict_filter #{'VLAN5 ': {'hostname': 'AU08_SRX_01_N0', 'address': IPNetwork('10.0.5.0/24')}..

'''with open('srx5800.txt','r') as f:
    print(xuat_rule_srx(f.readlines(),[]))'''