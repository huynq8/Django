#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
    import ftplib
import re
import os
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
    if request.FILES:
        uploaded_file = request.FILES['file']
        str_text = ''
        for line in uploaded_file:
            str_text = str_text + line.decode()  # "str_text" will be of `str` type
        dict_file.update([(str(request.FILES['file']),str_text)])

    # do something
    elif request.method == "POST":
        print('ok')
        fromJs = QueryDict(request.body)
        listResult = []
        response_data = {}
        if fromJs['content'] == "":
            response_data = {"result": "Bạn chưa nhập dữ liệu."}
            return JsonResponse(response_data)
        else:
            reg = web.list_regular(fromJs['content'])
            for list_config in dict_file:
                list_command = dict_file[list_config].splitlines()
                #print(list_command)
                response_data, response_data_cfg = web.search_rule(list_command,reg)
                response_data['result'] = str(response_data)
                #pprint.pprint(response_data)
            dict_file.clear()
            return JsonResponse(response_data)
        
    # product = Product.objects.get(pk=id)
    return render(request, 'first_app/searchrule.html')
def selectfile(request, id=None):
    print("xxx====",request.POST.get('content'))
    if request.POST.get('content') == "qtsc" or request.POST.get('content') == "singfarm":
        ftp = ftplib.FTP('116.193.74.219', 'noctool',
        'noctool@123#')
        #List the files in the current directory
        #print ("File List:")
        files = ftp.dir()
        date_time = strftime("%Y-%m-%d", gmtime())
        date_time ="2020-04-14"
        ftp.cwd("QTSC/"+str((date_time)))
        files = ftp.dir()
        #ftp.retrlines("LIST")
        
        ls = []
        #ftp.retrlines('MLSD', ls.append)
        ftp.retrlines('LIST', ls.append)
        list_result = ["QTSC/"+str((date_time))+"/"+re.search("(.*\s+)([\._\-a-zA-Z0-9]+)",item).group(2) for item in ls]
        return render(request, 'first_app/selectfile.html',context={'result':list_result})
    elif request.POST.get('content') == "campus":
        ftp = ftplib.FTP('localhost', 'admin',
        'admin')
        #List the files in the current directory
        #print ("File List:")
        #files = ftp.dir()
        ftp.cwd("C:\\Users\\LAP11357-local\\Downloads")
        #files = ftp.dir()
        #ftp.retrlines("LIST")
        '''with open( 'test.txt', 'wb' ) as file :
            ftp.retrbinary('RETR srx5800.txt', file.write)'''
        ls = []
        #ftp.retrlines('MLSD', ls.append)
        ftp.retrlines('LIST', ls.append)
        list_result = [re.search("(.*\s+)([\.\-a-zA-Z0-9]+)",item).group(2) for item in ls]
        return render(request, 'first_app/selectfile.html',context={'result':list_result})
    else:
        return render(request, 'first_app/selectfile.html',context={'result':list_result})
def resultsearchrule(request, id=None):
    if request.FILES:
        uploaded_file = request.FILES['file']
        str_text = ''
        for line in uploaded_file:
            str_text = str_text + line.decode()  # "str_text" will be of `str` type
        dict_file.update([(str(request.FILES['file']),str_text)])
    # do something
    elif request.method == "POST":
        response_data={'result':{}}
        fromJs = QueryDict(request.body)
        try:
            if fromJs['filename']:
                print(fromJs['filename'])
                ftp = ftplib.FTP('116.193.74.219', 'noctool',
                'noctool@123#')
                #List the files in the current directory
                #print ("File List:")
                ftp.dir()
                ftp.cwd("/")
                gFile = open("readme.txt", "wb")
                ftp.retrbinary('RETR '+str(fromJs['filename']),gFile.write)
                list_file = open("readme.txt",'r').readlines()    
        except:
            pass
        listResult = []
        if fromJs['content'] == "":
            response_data = {"result": "Bạn chưa nhập dữ liệu."}
        else:
            list_ip = fromJs['content']
            #print(list_command)
            result_func = web.search_rule(fromJs['filename'],list_file,list_ip)
            response_data['result'].update(result_func)
           # print(response_data)
            return render(request, 'first_app/resultsearchrule.html',context={"result":dict(response_data['result'])})
        ######
        #get file
        #######

        listResult = []
        if fromJs['content'] == "":
            response_data = {"result": "Bạn chưa nhập dữ liệu."}
            
            return render(request, 'first_app/resultsearchrule.html',context={"result":str(response_data)})
        else:
            print(fromJs['content'])
            #reg = web.list_regular(fromJs['content'])
            for list_config in dict_file:
                file_name = list_config
                list_command = dict_file[list_config].splitlines()
                list_ip = fromJs['content']
                #print(list_command)
                result_func = web.search_rule(file_name,list_command,list_ip)
                response_data['result'].update(result_func)
                print(response_data)
                #pprint.pprint(response_data)
            dict_file.clear()
            return render(request, 'first_app/resultsearchrule.html',context={"result":dict(response_data['result'])})    
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
        #List the files in the current directory
        #print ("File List:")
        date = "2020-04-14"        
        ftp.cwd("QTSC/"+date)
        ftp.dir()
        ls = []
        #ftp.retrlines('MLSD', ls.append)
        ftp.retrlines('LIST', ls.append)
        list_file = [re.search("(.*\s+)([\.\-a-zA-Z_0-9]+)",item).group(2) for item in ls]
        path = str(os.getcwdb(), encoding="utf-8")
        os.chdir(path +"\\files_folder")
        for filename in list_file:
            if os.path.isfile(filename):
                continue
            else:
                gFile = open(filename, "wb")
                ftp.retrbinary('RETR '+str(filename),gFile.write)   
        os.chdir(path)
        dict_val = json.loads(fromJs['dict_val'])
        listResult = []
        ticketId = dict_val['ticketId']
        protocol = dict_val['protocol']
        srcVlan = dict_val['srcVlan']
        srcPort = dict_val['srcPort']
        dstVlan = dict_val['dstVlan']
        dstPort = dict_val['dstPort']
        dstIp  = dict_val['dstIp']
    return render(request, 'first_app/campus.html')


def cart_add(request, product_id=None):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CardAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'], update_quantity=cd['update'])

    return redirect('cart_detail')


def cart_remove(request, product_id=None):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        # print(item)
        item['update_quantity_form'] = CardAddProductForm(
            initial={'quantity': item['quantity'], 'update': True})
    return render(request, 'first_app/cart_detail.html', {'cart': cart})


def order_create(request):
    cart = Cart(request)
    form = OrderCreateForm()
    if request.method == 'POST':
        print("I'm here")
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order, product=item['product'], price=item['fee'], quantity=item['quantity'])
                # clear the cart
                cart.clear()

                # order_created.display(order.id)
                return render(request, 'first_app/created.html', context={'order': order})
    else:
        form = OrderCreateForm()

    return render(request, 'first_app/create.html', context={'form': form, 'cart': cart})


def result(request):
    result_list = []
    ten_xe = Product.objects.order_by("name")
    if request.method == "GET":
        word = request.GET.get('word')
    for item in ten_xe:
        if str(word).lower() in str(item).lower():
            result_list.append(item)
    return render(request, 'first_app/search.html', context={'result': result_list})


def contact(request):
    name_ = request.POST.get('fullname')
    email_ = request.POST.get('email')
    message_ = request.POST.get('message')
    phone_ = request.POST.get('phone')
    Contact.objects.create(name=str(name_), email=str(
        email_), message=str(message_), phone=str(phone_))

    return render(request, 'first_app/contact.html')


'''def resultconvertjunos(request):
    response_data = {}
    print("===================")
    print(request)
    # change từ encode request http to string python
    fromJs = QueryDict(request.body)
     # now we can load our JSON from JS
    # open('output.txt','w').write((Input))
    # input1 = open('output.txt','r').read()  
    result1 = web.convert_junos_fun(fromJs['content'])
    result = "\n".join(result1)
    response_data['result']= result
    print(response_data)
    # return render(request, 'first_app/convertjunos.html', context={'result':result,'input':input1})   
    return JsonResponse(response_data)'''
