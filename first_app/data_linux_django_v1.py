import os
import glob
import re
import xlwt
import xlrd
import pandas as pd
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo

def export_graph():
    THIS_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print('xxxxxxxxxxxxxxxxx',THIS_FOLDER)
    list_folder = ['EQX',]
    for folder in list_folder:
        folder_path = os.path.join(THIS_FOLDER,'static','files',folder)
        title = folder
        dict_result = {}
        # nhập ip tương ứng vào list_fixip
        list_fixip = ["unknown","49.231.56.65","49.231.58.1","202.91.18.234","202.91.18.233","61.90.231.1","61.91.1.1",
        "114.125.0.1","114.125.1.1","114.4.46.1","114.4.48.1","112.215.88.5","112.215.88.6",
        "14.225.10.65","222.255.216.1","171.244.28.65","171.244.128.1","210.245.38.65","43.239.149.129",
        "112.205.128.1","49.146.96.1","203.177.125.1","203.177.128.1","121.96.0.1","121.96.4.1"
        ,"211.95.17.50","218.102.52.37","80.12.48.2","46.51.178.50","52.8.191.254","129.250.8.145",
        "129.250.3.101",
        "52.68.63.252","60.199.147.17","49.213.64.46","49.213.64.50",]
        ##
        list_tag = ["unknown","thailan","thailan","thailan","thailan","thailan","thailan","indonesia","indonesia",
            "indonesia","indonesia","indonesia","indonesia",
            "vietnam","vietnam","vietnam","vietnam","vietnam","vietnam",
            "philipines","philipines","philipines","philipines","philipines","philipines","china","HongKong","France",
            "EU","USA (West)","USA (East)","Singapore","Japan","Taiwan","QTSC1","QTSC2",]
        # Nhập as tương ứng với vị trí IP
        list_as = ["unknown","AS45430","AS45430","AS24378","AS24378","AS9287","AS9287","AS23693",
        "AS23693","AS4761","AS4761","AS24203","AS24203","AS45899","AS45899","AS7552","AS7552","AS18403",
        "AS18403","AS9299","AS9299","AS4775","AS4775","AS6648","AS6648"
        ,"china","HongKong","France","EU","USA (West)","USA (East)","Singapore","Japan","Taiwan","QTSC1","QTSC2",]  
        ##
        # Nhập tên ISP tương ứng với IP
        list_isp = ["unknown","AIS","AIS","DTAC","DTAC","TrueMove","TrueMove","Telkomsel",
        "Telkomsel","Indosat Ooredoo","Indosat Ooredoo","XL Axiata","XL Axiata","VNPT","VNPT","Viettel","Viettel","FPT",
        "FPT","PLTD","PLTD","Globe tele","Globe tele","Bayan tele","Bayan tele"
        ,"china","HongKong","France","EU","USA (West)","USA (East)","Singapore","Japan","Taiwan","QTSC1","QTSC2",]
        ##
        for index,item in enumerate(list_tag):
            try:
                dict_result[list_tag[index]][list_isp[index]].update([(list_fixip[index],{})])
            except:
                try:
                    dict_result[list_tag[index]].update([(list_isp[index],{})])
                    dict_result[list_tag[index]][list_isp[index]].update([(list_fixip[index],{})])
                except:
                    dict_result.update([(list_tag[index],{})])
                    dict_result[list_tag[index]].update([(list_isp[index],{})])
                    dict_result[list_tag[index]][list_isp[index]].update([(list_fixip[index],{})])

        for filename in glob.glob(os.path.join(folder_path, '*.log')):
            STT =""
            with open(filename, 'r') as f:
                listfile = f.read().splitlines()
            datefile = re.search(r"(\d+)_data_(\d+\.\d+\.\d+\.\d+)\.log",filename).group(1)
            date_file = datefile[0:4]+"-"+datefile[4:6]+"-"+datefile[6:8]
            ipfile = re.search(r"(\d+)_data_(\d+\.\d+\.\d+\.\d+)\.log",filename).group(2)
            listresult = []
            dict_temp ={}
            date =""
            time =""
            for i, e in enumerate(list_fixip):
                if e in filename:
                    STT = str(i)
                    AS = list_isp[i]
                    TAG = list_tag[i]
                    break
            for line in listfile:
                if "result PING" in line and re.search(r"(\d+-\d+-\d+_\d+)",line):
                    try:
                        date = re.search(r"(\d+-\d+-\d+_\d+\.\d+\.\d+)",line).group()
                        time = int(re.search(r"(\d+-\d+-\d+)_(\d+)\.\d+\.\d+",line).group(2))
                        time.zfill(2)
                        #print(date)
                    except:
                        pass
                elif "rtt min/avg/max/mdev" in line and date != "":
                    latency = float(re.search(r"rtt min/avg/max/mdev = [0-9\.]+/([0-9\.]+)",line).group(1))
                    try:
                        dict_temp[time].append(latency)
                    except:
                        dict_temp.update([(time,[latency])])
                    #listresult.append((time,latency))  
                    date = ""
                elif "100% packet loss" in line and date !="":
                    latency = 0
                    try:
                        dict_temp[time].append(latency)
                    except:
                        dict_temp.update([(time,[latency])])
                    #listresult.append((time,latency))    
                    date = ""
            for tag in dict_result:
                for _as in dict_result[tag]:
                    for ip in dict_result[tag][_as]:
                        if ip==ipfile:
                            dict_result[tag][_as][ip].update([(date_file,dict_temp)])
                            break
        for tag in dict_result:
            for _as in dict_result[tag]:
                for ip in dict_result[tag][_as]:
                    for date_ in dict_result[tag][_as][ip]:
                        for time_ in dict_result[tag][_as][ip][date_]:
                            dict_result[tag][_as][ip][date_][time_] = sum(dict_result[tag][_as][ip][date_][time_])/len(dict_result[tag][_as][ip][date_][time_])
        for i in range(24):
            for tag in dict_result:
                for _as in dict_result[tag]:
                    for ip in dict_result[tag][_as]:
                        for date_ in dict_result[tag][_as][ip]:
                            if any(str(j) == str(i) for j in list(dict_result[tag][_as][ip][date_].keys())):
                                pass
                            else:
                                dict_result[tag][_as][ip][date_].update([(i,0)])
        #pprint(dict_result['philipines']['AS9299'])
            #open("_result__"+STT,'a').write("".join(listresult))        
        f2=xlwt.Workbook()
        color=xlwt.easyxf('align:wrap yes, vert centre,horiz centre;''pattern: pattern solid, fore_colour yellow;''font: colour red,name Arial, bold True;''borders: top double, bottom thin, left thin, right thin')
        color1=xlwt.easyxf('align:vert top,horiz left;''borders:top dashed,right thin,left thin,bottom dashed;')
        color2=xlwt.easyxf('align: wrap yes,vert top, horiz left;''borders:top dashed,right thin,left thin,bottom dashed;')
        #pprint(dict_result)
        f3=f2.add_sheet('result')
        m=0
        n=0
        dict_result.pop('unknown')
        f3.write(0,0,"Timestamp")
        for tag in dict_result:
                for _as in dict_result[tag]:
                    for ip in dict_result[tag][_as]:
                        f3.write(0,n+1,tag+"_"+_as+"_"+ip)
                        for date_ in dict_result[tag][_as][ip]: 
                            for time_ in sorted(dict_result[tag][_as][ip][date_].keys()): 
                                try:
                                    f3.write(m+1,0,str(date_)+" "+str(time_))
                                except:
                                    pass
                                f3.write(m+1,n+1,dict_result[tag][_as][ip][date_][time_])
                                m+=1
                        n+=1
                        m=0
        # Create graph 
        f2.save(title+"result"+'.xls')
        read_file = pd.read_excel (title+'result.xls')
        read_file.to_csv (title + 'result.csv', index = None, header=True)
        df = pd.read_csv(title + 'result.csv')
        data = [go.Scatter(x=df["Timestamp"], y= df[col], name=col ) for col in df.drop(columns="Timestamp")]
        #title = "GOOGLE-TO_SEA_LATENCY_GRAPH"
        layout = go.Layout(title = title +'_TO_SEA_LATENCY (DESIGNED by NRD TEAM of DC)',xaxis_title='Date',yaxis_title='ms')
        fig = go.Figure(data=data,layout=layout)
        #fig.update_xaxes(rangeslider_visible=True)
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=5, label="5min", step="minute", stepmode="backward"),
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"), 
                    dict(count=7, label="7d", step="day", stepmode="backward"),
                    #dict(count=1, label="1m", step="month", stepmode="backward"),
                    #dict(count=6, label="6m", step="month", stepmode="backward"),
                    #dict(count=1, label="YTD", step="year", stepmode="todate"),
                    #dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        pyo.plot(fig, filename=title+'_TO_SEA_LATENCY.html')
        