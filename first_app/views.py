#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import ftplib
import re
import os
import shutil
import csv
# Create your views here.
from first_app import forms
from first_app.models import Product
from django.http.response import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product
from .cart import Cart
from .forms import CardAddProductForm
from .models import OrderItem, Contact
from .forms import OrderCreateForm
from . import web
import html2text
import json
from django.http import QueryDict
import pprint
from time import gmtime, strftime
dict_file = {}


def homepage(request):
    pro_list = Product.objects.order_by('name')
    return render(request, 'first_app/homepage.html', context={"product": pro_list})


def homepage1(request):
    pro_list = Product.objects.order_by('name')
    return render(request, 'first_app/homepage.html', context={"product": pro_list})


def convertjunos(request, id=None):
    response_data = {}
    # product = Product.objects.get(pk=id)
    if request.method == "POST":
        fromJs = QueryDict(request.body)
        if fromJs['content'] == "":
            response_data = {"result": "Bạn chưa nhập dữ liệu."}
            return JsonResponse(response_data)
        else:
            # change từ encode request http to string python
            # now we can load our JSON from JS
            # open('output.txt','w').write((Input))
            # input1 = open('output.txt','r').read()
            result1 = web.convert_junos_fun(fromJs['content'])
            result = "\n".join(result1)
            response_data['result'] = result
        # return render(request, 'first_app/convertjunos.html', context={'result':result,'input':input1})
            return JsonResponse(response_data)
    return render(request, 'first_app/convertjunos.html')


def hitcount(request, id=None):
    # product = Product.objects.get(pk=id)
    if request.method == "POST":
        fromJs = QueryDict(request.body)
        listResult = []
        response_data = {}
        if fromJs['content'] == "":
            response_data = {"result": "Bạn chưa nhập dữ liệu."}
            return JsonResponse(response_data)
        # change từ encode request http to string python
        # now we can load our JSON from JS
        # open('output.txt','w').write((Input))
        # input1 = open('output.txt','r').read()
        else:
            open('file', 'w').write(fromJs['content'])
            result1 = web.top_hit('file')
            for policy in result1:
                elementPolicy = result1[policy]
                _str = "show configuration security policies from-zone "
                listResult.append(
                    _str+elementPolicy['fzone']+" to-zone "+elementPolicy['tzone']+" policy "+elementPolicy['term'])
                result = "\n".join(listResult)
            response_data['result'] = result
            return JsonResponse(response_data)
    return render(request, 'first_app/hitcount.html')


def searchrule(request, id=None):
    return render(request, 'first_app/searchrule.html')


def resultsearchrule(request, id=None):
    if request.FILES:
        uploaded_file = request.FILES['file']
        str_text = ''
        for line in uploaded_file:
            str_text = str_text + line.decode()  # "str_text" will be of `str` type
        file_name_upload = str(request.FILES['file'])
        with open(file_name_upload, 'w') as f:
            f.write(str_text)
        dict_file.update([(str(request.FILES['file']), file_name_upload)])
    # do something
    elif request.method == "POST":
        response_data = {'result': {}}
        fromJs = QueryDict(request.body)

        listResult = []
        if fromJs['content'] == "":
            response_data = {"result": "Bạn chưa nhập dữ liệu."}

            return render(request, 'first_app/resultsearchrule.html', context={"result": str(response_data)})
        else:
            #reg = web.list_regular(fromJs['content'])
            for name in dict_file:
                file_name = name
                list_command = open(file_name, 'r').readlines()
                list_ip = fromJs['content']
                # print(list_command)
                result_func = web.search_rule(file_name, list_command, list_ip)
                response_data['result'].update(result_func)
                # pprint.pprint(response_data)
            dict_file.clear()
            THIS_FOLDER = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            os.chdir(THIS_FOLDER)
            my_folder = os.getcwd()
            my_file_source = os.path.join(my_folder, file_name+'.csv')
            with open(my_file_source, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Configuration", "Rule Type delete", "Device", "Policy/Term name", "application",
                                 "Protocol", "Source VLAN", "Source IP", "Source Port", "Dest VLAN", "Dest IP", "Dest Port"])
                for filename in response_data['result']:
                    for dict_rule in response_data['result'][filename]:
                        for rule in response_data['result'][filename][dict_rule]:
                            rule_detail = response_data['result'][filename][dict_rule][rule]
                            conf = rule_detail['config']
                            rule_type_delete = dict_rule
                            device = filename
                            term_name = rule_detail['term']
                            application = rule_detail['application']
                            protocol = rule_detail['protocol']
                            source_vlan = rule_detail['fzone']
                            source_ip = rule_detail['sourceip']
                            dest_ip = rule_detail['destip']
                            dest_vlan = rule_detail['tzone']
                            source_port = rule_detail['sourceport']
                            dest_port = rule_detail['destport']
                            writer.writerow([conf, device, term_name, application, protocol,
                                             source_vlan, source_ip, source_port, dest_vlan, dest_ip, dest_port])
            my_file_dest = os.path.join(my_folder, "static", file_name+'.csv')
            shutil.move(my_file_source, my_file_dest)
            return render(request, 'first_app/resultsearchrule.html', context={"result": dict(response_data['result']), "filename": file_name+".csv"})
    return render(request, 'first_app/resultsearchrule.html')


def regular(request, id=None):
    response_data = {}
    # product = Product.objects.get(pk=id)
    if request.method == "POST":
        fromJs = QueryDict(request.body)
        if fromJs['content'] == "":
            response_data = {"result": "Bạn chưa nhập dữ liệu."}
            return JsonResponse(response_data)
        else:
            # change từ encode request http to string python
            # now we can load our JSON from JS
            # open('output.txt','w').write((Input))
            # input1 = open('output.txt','r').read()
            result1 = web.list_regular(fromJs['content'])
            result = "".join(result1)
            response_data['result'] = result
        # return render(request, 'first_app/convertjunos.html', context={'result':result,'input':input1})
            return JsonResponse(response_data)
    return render(request, 'first_app/regular.html')


def generate_campus(request, id=None):

    return render(request, 'first_app/campus.html')


def result_generate_campus(request, id=None):
    if request.POST:
        fromJs = QueryDict(request.body)
        ftp = ftplib.FTP('116.193.74.219', 'noctool',
                         'noctool@123#')
        # List the files in the current directory
        #print ("File List:")
        date = "2020-04-14"
        ftp.cwd("QTSC/"+date)
        ftp.dir()
        ls = []
        #ftp.retrlines('MLSD', ls.append)
        ftp.retrlines('LIST', ls.append)
        list_file = [re.search("(.*\s+)([\.\-a-zA-Z_0-9]+)",
                               item).group(2) for item in ls]
        path = str(os.getcwdb(), encoding="utf-8")
        os.chdir(path + "\\files_folder")
        for filename in list_file:
            if os.path.isfile(filename):
                continue
            else:
                gFile = open(filename, "wb")
                ftp.retrbinary('RETR '+str(filename), gFile.write)
        os.chdir(path)
        dict_val = json.loads(fromJs['dict_val'])
        listResult = []
        ticketId = dict_val['ticketId']
        protocol = dict_val['protocol']
        srcVlan = dict_val['srcVlan']
        srcPort = dict_val['srcPort']
        dstVlan = dict_val['dstVlan']
        dstPort = dict_val['dstPort']
        dstIp = dict_val['dstIp']
    return render(request, 'first_app/campus.html')


def parse_firewall(request, id=None):
    return render(request, 'first_app/parse_firewall.html')


def result_parse_firewall(request, id=None):
    print("xxxxxxxxx")
    if request.FILES:
        print("xxxxxxxxxxxxx",request)
        uploaded_file = request.FILES['file']
        str_text = ''
        for line in uploaded_file:
            str_text = str_text + line.decode()  # "str_text" will be of `str` type
        file_name_upload = str(request.FILES['file'])
        with open(file_name_upload, 'w') as f:
            f.write(str_text)
        dict_file.update([(str(request.FILES['file']), file_name_upload)])
        # print(dict_file)
    elif request.method == "POST":
        response_data = {'result': {}}
        for name in dict_file:
            file_name = name
            list_command = open(file_name, 'r').readlines()
            result_func = web.parse_rule(file_name, list_command)
            response_data['result'].update(result_func)
        dict_file.clear()
        THIS_FOLDER = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        os.chdir(THIS_FOLDER)
        my_folder = os.getcwd()
        my_file_source = os.path.join(my_folder, file_name+'.csv')
        with open(my_file_source, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Configuration", "Device", "Policy/Term name", "Application", "Protocol",
                             "Source VLAN", "Source IP", "Source Port", "Dest VLAN", "Dest IP", "Dest Port"])
            for filename in response_data['result']:
                for dict_rule in response_data['result'][filename]:
                    for rule in response_data['result'][filename][dict_rule]:
                        rule_detail = response_data['result'][filename][dict_rule][rule]
                        conf = rule_detail['config']
                        device = filename
                        term_name = rule_detail['term']
                        application = rule_detail['application']
                        protocol = rule_detail['protocol']
                        source_vlan = rule_detail['fzone']
                        source_ip = rule_detail['sourceip']
                        dest_vlan = rule_detail['tzone']
                        dest_ip = rule_detail['destip']
                        source_port = rule_detail['sourceport']
                        dest_port = rule_detail['destport']
                        writer.writerow([conf, device, term_name, application, protocol,
                                         source_vlan, source_ip, source_port, dest_vlan, dest_ip, dest_port])
        my_file_dest = os.path.join(my_folder, "static", file_name+'.csv')
        shutil.move(my_file_source, my_file_dest)
        # print("====++++++++++++++++++++",response_data['result'])
        return render(request, 'first_app/result_parse_firewall.html', context={"result": dict(response_data['result']), "filename": file_name+".csv"})
    return render(request, 'first_app/result_parse_firewall.html')
    # do something
def ping_latency(request, id=None):
    return render(request, 'first_app/ping_latency.html')


def result_ping_latency(request, id=None):
    THIS_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_folder = os.path.join(THIS_FOLDER,"static","files",'EQX')
    download_folder = os.path.join(THIS_FOLDER,"static","files",'download')
    if request.FILES:
        uploaded_file = request.FILES['file']
        listfile = uploaded_file.readlines()
        file_name_upload = str(request.FILES['file'])
        with open(os.path.join(upload_folder,file_name_upload), 'w') as f:
            f.write("".join(i.decode('utf8', 'ignore') for i in listfile))
        dict_file.update([(str(request.FILES['file']), file_name_upload)])
    # do something
    elif request.method == "POST":
        response_data = {'result': {}}
        os.chdir(download_folder)
        web.ping_latency()
        web_ip = "http://junos126.pythonanywhere.com/"
        file_download = "/".join([web_ip,'static','files','download',"EQX_TO_SEA_LATENCY.html"])
        return render(request, 'first_app/result_ping_latency.html', context={"result": dict(response_data['result']), "filename": file_download})
    return render(request, 'first_app/result_ping_latency.html')