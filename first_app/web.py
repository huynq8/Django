import re
from collections import OrderedDict
import collections as col
#import matplotlib.pyplot as plt
from re import *
from netaddr import *
#from first_app.move_vlan import *
from .move_vlan import *
from .data_linux_django_v1 import *

def convert_junos_fun(text_input):
    # initListStr=open(inputFile,'r').read().replace(' ## SECRET-DATA','').splitlines()
    listFinalStr = []  # final list final strings
    listTempStr = []  # temp list of, use as stack
    for no, line in enumerate(text_input.split("\n")):
        # print 'process line : %s -> %s' %(no,line)
        if line.endswith('{'):
            if "inactive" in line:
                listTempStr.append(line[:-1].lstrip().replace("inactive:", ""))
                listFinalStr.append(
                    "deactivate "+''.join(listTempStr) + line.lstrip()[10:-1])
                # we not yet get to command line ; -> push it to listTempStr
            else:
                listTempStr.append(line[:-1].lstrip())
                #print (listTempStr)
        elif line.endswith(';'):
            if "inactive" in line:
                listFinalStr.append(
                    "deactivate "+''.join(listTempStr) + line.lstrip()[10:-1])
            else:
                listFinalStr.append(''.join(listTempStr) + line[:-1].lstrip())
            # print listTempStr
        elif line.endswith('}'):  # -> we need to pop last element from listTempStr
            if "inactive" in line:
                listTempStr.pop()
                listFinalStr.append(
                    "deactivate "+''.join(listTempStr) + line.lstrip()[10:-1])

            else:
                listTempStr.pop()
            # print listTempStr

        else:
            pass
    for n, i in enumerate(listFinalStr):
        if "deactivate" in i:
            pass
        else:
            listFinalStr[n] = "set "+i
    return listFinalStr


def top_hit(file1):
    dict_hit_1 = {}
    dict_hit_2 = {}
    dict_hit_update = {}
    list_hit = open(file1, 'r').read().split(
        "Logical system: root-logical-system")
    list_hit_1 = list_hit[-1].split('\n')
    list_hit_2 = list_hit[-2].split('\n')
    for line in list_hit_1:
        list_policy = [i for i in re.split(r"\s+", line) if i]
        try:
            key = list_policy[1]+list_policy[2]+list_policy[3]
            fzone = list_policy[1]
            tzone = list_policy[2]
            term = list_policy[3]
            value = int(list_policy[4])
            dict_hit_1.update(
                [(key, {"value": value, 'tzone': tzone, 'fzone': fzone, 'term': term})])
        except:
            pass
    for line in list_hit_2:
        list_policy = [i for i in re.split(r"\s+", line) if i]
        try:
            key = list_policy[1] + list_policy[2] + list_policy[3]
            fzone = list_policy[1]
            tzone = list_policy[2]
            term = list_policy[3]
            value = int(list_policy[4])
            dict_hit_2.update(
                [(key, {"value": value, 'tzone': tzone, 'fzone': fzone, 'term': term})])
        except:
            pass
    for key in dict_hit_2:
        fzone = dict_hit_2[key]['fzone']
        tzone = dict_hit_2[key]['tzone']
        term = dict_hit_2[key]['term']
        toc_do = dict_hit_1[key]['value']-dict_hit_2[key]['value']
        dict_hit_update.update(
            [(key, {"value": toc_do, 'tzone': tzone, 'fzone': fzone, 'term': term})])
    dict_sort = OrderedDict(
        sorted(dict_hit_update.items(), reverse=True, key=lambda x: x[1]['value']))
    lst_policy = []
    lst_hit = []
    n = 0
    for key in dict_sort:
        if n < 10:
            lst_policy.append(dict_sort[key]['term'])
            lst_hit.append(dict_sort[key]['value'])
            n += 1
    '''plt.hist(lst_hit, bins=10, edgecolor='r')
    plt.show()
    plt.clf()

    proportions = lst_hit
    plt.pie(
        proportions,
        labels=lst_policy,
        shadow=False,
        colors=['blue','red','green','yellow'],
        #explode = (0.15, 0),
        startangle = 90,
        autopct = '%1.1f%%',
    )
    plt.axis('equal')
    plt.title('top hitcount')
    #plt.plot(lst_policy,lst_hit)
    plt.tight_layout()
    plt.show()'''
    # print(dict_sort)
    return dict_sort

    # Iterate over the sorted sequence
    # print(listofTuples)
"""
function regular
"""
# coding=utf8

#  Split range to ranges that has its unique pattern.
#  Example for 12-345:
#
#  12- 19: 1[2-9]
#  20- 99: [2-9]\d
# 100-299: [1-2]\d{2}
# 300-339: 3[0-3]\d
# 340-345: 34[0-5]


def bounded_regex_for_range(min_, max_):
    return r'\b({})\b'.format(regex_for_range(min_, max_))


def regex_for_range(min_, max_):
    """
    > regex_for_range(12, 345)
    '1[2-9]|[2-9]\d|[1-2]\d{2}|3[0-3]\d|34[0-5]'
    """
    subpatterns = []

    start = min_
    for stop in split_to_ranges(min_, max_):
        subpatterns.append(range_to_pattern(start, stop))
        start = stop + 1

    return '|'.join(subpatterns)


def split_to_ranges(min_, max_):
    stops = {max_}

    nines_count = 1
    stop = fill_by_nines(min_, nines_count)

    while min_ <= stop < max_:
        stops.add(stop)
        nines_count += 1
        stop = fill_by_nines(min_, nines_count)

    zeros_count = 1
    stop = fill_by_zeros(max_, zeros_count) - 1
    while min_ < stop < max_:
        stops.add(stop)

        zeros_count += 1
        stop = fill_by_zeros(max_, zeros_count) - 1

    stops = list(stops)
    stops.sort()
    return stops


def fill_by_nines(integer, nines_count):
    return int(str(integer)[:-nines_count] + '9' * nines_count)


def fill_by_zeros(integer, zeros_count):
    return integer - integer % 10 ** zeros_count


def range_to_pattern(start, stop):
    pattern = ''
    any_digit_count = 0

    for start_digit, stop_digit in zip(str(start), str(stop)):

        if start_digit == stop_digit:
            pattern += start_digit
            # print(pattern)
        elif start_digit != '0' or stop_digit != '9':
            pattern += '[{}-{}]'.format(start_digit, stop_digit)
        else:
            any_digit_count += 1

    if any_digit_count:
        pattern += r'[0-9]'
    if any_digit_count > 1:
        pattern += '{{{}}}'.format(any_digit_count)
    return pattern


def regular(n):
    mask = IPNetwork(n).prefixlen
    re_lst1 = [i for i in IPNetwork(n)]
    min_1 = int(str(re_lst1[0]).split('.')[0])
    max_1 = int(str(re_lst1[-1]).split('.')[0])
    min_2 = int(str(re_lst1[0]).split('.')[1])
    max_2 = int(str(re_lst1[-1]).split('.')[1])
    min_3 = int(str(re_lst1[0]).split('.')[2])
    max_3 = int(str(re_lst1[-1]).split('.')[2])
    min_4 = int(str(re_lst1[0]).split('.')[3])
    max_4 = int(str(re_lst1[-1]).split('.')[3])
    re_lst1 = [str(re_lst1[0]).split('.')[0], str(
        re_lst1[0]).split('.')[1], str(re_lst1[0]).split('.')[2]]
    re_str1 = str('.'.join(re_lst1))
    regex1 = regex_for_range(min_1, max_1)
    regex2 = regex_for_range(min_2, max_2)
    regex3 = regex_for_range(min_3, max_3)
    regex4 = regex_for_range(min_4, max_4)
    lst1 = [regex1, regex2, regex3, regex4]
    lst2 = ["("+i+")" for i in lst1]
    subnetmask = regex_for_range(int(mask), int(32))
    # print(subnetmask)
    return "("+(str('\.'.join(lst2)))+'/'+"("+str(subnetmask)+")"+")"
# done hàm tính regular


def list_regular(text_input):
    regular_lst = ""
    lst = [i for i in text_input.split("\n") if i != ""]
    for n, item in enumerate(lst):
        # print(lst)
        if (len(lst) - n) > 1 and item != "":
            # print(len(lst))
            regular_lst = regular_lst + regular(str(item)) + "|"
            # print(item)
        elif item != "":
            regular_lst = regular_lst + regular(str(item))
    return str(regular_lst)
#####Done hàm tính regular######
####Hàm search rule####


def search_rule(file_name, file, list_ip):
    dict_result = {}
    dict_rule_one = {}
    dict_rule_any = {}
    list_rule_one = []
    list_rule_any = []
    # B1: export to dictionary rule
    dict_rule, dict_rule_config = xuat_rule_srx(file, [])
    # print(dict_rule)
    # B2: compare rule in source or dest: rule any or rule one
    reg = list_regular(list_ip)
    # print(dict_rule['A73431_999264363_VLAN381_VLAN368'])
    for key in dict_rule:
        policy = dict_rule[key]
        if all(re.search(reg, ip) for ip in policy['sourceip']) or all(re.search(reg, ip) for ip in policy['destip']):
            config = policy['config']
            #list_rule_any.extend([item.replace("set","delete") for item in config])
            dict_rule_any.update([(key, dict_rule[key])])
            dict_rule_any[key]['config'] = [
                item.replace("set", "delete") for item in config]
            # pprint(list_rule_any)
        elif any(re.search(reg, ip) for ip in policy['sourceip']) or any(re.search(reg, ip) for ip in policy['destip']):
            config = policy['config']
            #list_rule_one.extend([item.replace("set","delete") for item in config if re.search(reg,item)])
            #list_rule_one.extend([item for item in config if re.search(reg,item) is None])
            dict_rule_one.update([(key, dict_rule[key])])
            dict_rule_one[key]['config'] = [item.replace(
                "set", "delete") for item in config if re.search(reg, item)]
            dict_rule_one[key]['config'].extend(
                [item for item in config if re.search(reg, item) is None])
    dict_result.update(
        [(file_name, {'dict_rule_one': dict_rule_one, 'dict_rule_any': dict_rule_any})])
    for filename in dict_result:
        for type_policy in dict_result[file_name]:
            for key in dict_result[file_name][type_policy]:
                policy = dict_result[file_name][type_policy][key]
                policy['config'] = "\n".join(policy['config'])
                policy['sourceip'] = "\n".join(policy['sourceip'])
                policy['destip'] = "\n".join(policy['destip'])
                policy['protocol'] = "\n".join(policy['protocol'])
                policy['sourceport'] = "\n".join(policy['sourceport'])
                policy['destport'] = "\n".join(policy['destport'])
                policy['application'] = "\n".join(policy['application'])
    # print(dict_rule)
    return dict_result
    # B3: export result
#filename = "srx5800.txt"
#listip = "1.1.1.1"
#file = open(r"C:\Users\LAP11357-local\Downloads\ex9214.txt",'r').readlines()
#pprint(search_rule(filename, file, listip))


def parse_rule(file_name, file):
    dict_result = {}
    dict_rule, dict_rule_config = xuat_rule_srx(file, [])
    dict_result.update([(file_name, {'dict_rule': dict_rule})])
    for filename in dict_result:
        for type_policy in dict_result[file_name]:
            for key in dict_result[file_name][type_policy]:
                policy = dict_result[file_name][type_policy][key]
                policy['config'] = "\n".join(policy['config'])
                policy['sourceip'] = "\n".join(policy['sourceip'])
                policy['destip'] = "\n".join(policy['destip'])
                policy['protocol'] = "\n".join(policy['protocol'])
                policy['sourceport'] = "\n".join(policy['sourceport'])
                policy['destport'] = "\n".join(policy['destport'])
                policy['application'] = "\n".join(policy['application'])
    return dict_result
def ping_latency():
    export_graph()
