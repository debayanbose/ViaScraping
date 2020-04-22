#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 16:25:46 2019

@author: debayanbose
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 20:08:16 2019

@author: debayanbose
"""

import csv
import selenium.webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
#from multiprocessing.pool import ThreadPool, Pool
#import threading
from selenium import webdriver
#from multiprocessing import Process
#import multiprocessing
import time
import warnings
import datetime
from dateutil.rrule import rrule, DAILY
#import config
import pandas as pd
import numpy as np
from pymongo import MongoClient 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys



warnings.filterwarnings("ignore", category=UserWarning, module='bs4')


def get_driver():
    options = webdriver.ChromeOptions()    
#    options.add_argument("--headless")
#    options.add_argument("window-size=1920,1080")
#    options.add_argument("start-maximised")
#    options.add_argument("--use-fake-ui-for-media-stream")
#    options.add_argument("--disable-user-media-security=true")
    driver = selenium.webdriver.Chrome(executable_path='C:/Users/debayan.bose/Downloads/chromedriver_win32/chromedriver.exe',chrome_options=options)
#    driver = selenium.webdriver.Chrome()
#    options = Options()
#    options.headless = True
#    driver = webdriver.Firefox(options=options, executable_path=r'C:/D Backup/geckodriver.exe')

    return driver



def scrape_via_int(url,depdate):
        driver=get_driver()
        driver.get(url)  			 # URL requested in browser.
        body_init = driver.page_source
        time.sleep(20)
        counter = 0
        soup_init = BeautifulSoup(body_init, "lxml")
        load_perc = soup_init.find_all('div', attrs={'class': 'loadPercent'})[0].text
        while(load_perc !='100%'):
            time.sleep(4)
            body_init = driver.page_source
            soup_init = BeautifulSoup(body_init, "lxml")
            load_perc = soup_init.find_all('div', attrs={'class': 'loadPercent'})[0].text
            counter = counter +1
            print(counter)
            if(counter>10):
                break
        if load_perc !='100%':
            print('timeout for url - ',url)
            return None

#        for j in range(1,15):
#            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
#            time.sleep(0.5)
    	
        actions = ActionChains(driver)
        for _ in range(100):
            actions.send_keys(Keys.PAGE_DOWN).perform()
        body = driver.page_source
        soup = BeautifulSoup(body, "lxml")
        fil = open("out_via_fare.txt", "w", encoding='utf-8')
        fil.write(driver.page_source)
        flight_num = soup.find_all('div', attrs={'class': 'fltNum'})
        if len(flight_num)==0:
            print('no flights found for'+ url)
            driver.close()
            driver.quit()
            return None
        else:
            
            flight_code = soup.find_all('div', attrs={'class': 'airDet'})
            flight_name = []
            for j in range(len(flight_code)):
                temp1 = flight_code[j].find_all('div',attrs={'class':'name js-toolTip'})[0].text
                temp1 = temp1.replace('\t','')
                temp1 = temp1.replace('\n','')
                temp1 = temp1.replace(' ','')
                flight_name.append(temp1)
                
            fare = soup.select('span[class=price]')
            price=[]
            for j in range(len(fare)):
                temp2 = fare[j].text
                temp2 = temp2.replace('\t','')
                temp2 = temp2.replace('\n','')
                temp2 = temp2.replace(' ','')
                price.append(temp2)
            
            base_fare = soup.find_all('div', attrs={'class': 'paxTax u_invisible'})
            base_fare_final = []
            for j in range(len(base_fare)):
                base_fare_details = base_fare[j].text
                base_fare_details = base_fare_details.replace('+ Taxes','')
                base_fare_details = base_fare_details.replace(' ','')
                
                base_fare_final.append(base_fare_details)
            
            
            depTime_add = soup.find_all('div', attrs={'class': "depTime"})
            depTime = []
            for i in range(len(depTime_add)):
                time_details = depTime_add[i].find('div',attrs={'class':'time'})
                depTime.append(time_details.text)
            
            depCity = []
            for i in range(len(depTime_add)):
                city_details = depTime_add[i].find('div',attrs={'class':'city'})
                depCity.append(city_details.text)
            
            arrTime_add = soup.find_all('div', attrs={'class': "arrTime"})
            arrTime = []
            for i in range(len(arrTime_add)):
                time_details = arrTime_add[i].find('div',attrs={'class':'time'})
                arrTime.append(time_details.text)
            
            arrCity = []
            for i in range(len(arrTime_add)):
                city_details = arrTime_add[i].find('div',attrs={'class':'city'})
                arrCity.append(city_details.text)
            
            duration_add = soup.find_all('div', attrs={'class': "fltDur"})
            duration = []
            for i in range(len(duration_add)):
                dur_details = duration_add[i].find('div',attrs={'class':'dur'})
                duration.append(dur_details.text)
            
            duration = [x.replace('\n', '') for x in duration]
            duration = [x.replace('\t', '') for x in duration]
            
            stops = []
            for i in range(len(duration_add)):
                stop_details = duration_add[i].find('span',attrs={'class':'stops'})
                stops.append(stop_details.text)
            stops = [w.strip() for w in stops]
            for j in range(len(duration)):
                duration[j] = duration[j].replace(stops[j],'')
                
            route = soup.find_all('div', attrs={'class': 'route js-toolTip'})
            final_dest = []
            final_orig = []
            for j in range(len(route)):
                temp1 = route[j].text
                temp1 = temp1.replace('\t','')
                temp1 = temp1.replace('\n','')
                temp1 = temp1.replace(' ','')
                temp2 = temp1[len(temp1)-3:len(temp1)]
                temp3 = temp1[0:3]
                final_dest.append(temp2)
                final_orig.append(temp3)
            
            flightsData = []
            for j in range(0, len(duration_add)):
                flightsData.append([depdate, flight_name[j], flight_num[j].text, depTime[j], depCity[j], duration[j], arrTime[j], arrCity[j], price[j], base_fare_final[j],stops[j],final_orig[j],final_dest[j]])
            flightsData = pd.DataFrame(flightsData)
            driver.close()
            driver.quit()
            
        return flightsData
def scrapenew_via_int(origin,destin,fromdate,todate,job_time, passengers, stops):
    a = datetime.datetime.strptime(fromdate, "%d/%m/%Y").date()
    b = datetime.datetime.strptime(todate, "%d/%m/%Y").date()
    trDate = list()
    for dt in rrule(DAILY, dtstart=a, until=b):
        dept_date = str(dt.strftime("%m/%d/%Y"))
        trDate.append(dept_date)
    all_urls = list()  
    for j in range(len(trDate)):
        url = 'https://in.via.com/flight/search?returnType=one-way&destination='
        url = url + destin +'&bdestination='+destin+'&source='+origin+'&bsource='+origin+'&sourceCity=&source'
        dt_format = int(datetime.datetime.strptime(trDate[j], "%m/%d/%Y").date().strftime('%d'))
        mon_format = int(datetime.datetime.strptime(trDate[j], "%m/%d/%Y").date().strftime('%m'))
        year_format = int(datetime.datetime.strptime(trDate[j], "%m/%d/%Y").date().strftime('%Y'))
        url = url + 'CN=&month='+str(mon_format)+'&day='+str(dt_format)+'&year='+str(year_format)+'&date='+trDate[j]
        
        passengers = 'A-1_C-0_I-0'
        adults = passengers[2]
        children = passengers[6]
        infants = passengers[10]
        url = url + '&numAdults='+ adults + '&numChildren=' + children + '&numInfants='+ infants
        url = url + '&validation_result=&domesinter=international&livequote=-1&flightClass=ALL&travType=DOM&routingType=ALL&preferredCarrier=ALL&prefCarrier=0&isAjax=false'
        all_urls.append(url)
    data=list()
    for urls in range(len(all_urls)):
        temp1 = scrape_via_int(all_urls[urls],trDate[urls])
        if not (temp1 is None):
            data.append(temp1)
    if len(data) == 0:
        return 0
    df = pd.concat(data)
    df.columns = ['DepartureDate','FlightName', 'FlightCode', 'DepTime','DepCity','FlightDuration','ArrivalTime','ArrivalCity','fare','BaseFare','stops','Origin','Destination']
#    for i in range(len(data)):
#        for j in range(len(data[i])):
#            df = df.append(pd.Series(data[i][j],index = ['DepartureDate','FlightName', 'FlightCode', 'DepTime','DepCity','FlightDuration','ArrivalTime','ArrivalCity','fare','stops']),ignore_index=True)
#   
    df = df[df['Destination']==destin] 
    del df['Destination']  
    df = df[df['Origin']==origin] 
    del df['Origin']  
              
    df['fare'] = [w.replace('₹ ', '') for w in df['fare']]
    df['fare'] = [w.replace(',', '') for w in df['fare']]
    df['fare']= np.array(df['fare'],float)
    df['BaseFare']= np.array(df['BaseFare'],float)
    df['SurchargeFare'] = df['fare'] - df['BaseFare']
    df['Discounts'] = 0
    
    df['sector']= origin +'_'+destin
    df['job_time'] = job_time
    df['NSTOP'] = df['stops']
    for j in range(len(df)):
        if df['stops'].iloc[j] == 'Non-Stop':
            df['NSTOP'].iloc[j] = '0'
    df['NSTOP'] = [w.replace('Stop(s)','') for w in df['NSTOP']]
    df['NSTOP'] = [w.replace(' ','') for w in df['NSTOP']]
    df['NSTOP'] = np.array(df['NSTOP'],int)
    df_del = df[df['NSTOP']==0] 
    df_del = df_del[df_del['FlightName'].str.contains('MultipleAirlines')]
    df = df.drop(df_del.index, axis=0) 
    df['stops'] = df['NSTOP']
    del df['NSTOP']
    
    df = df[['DepartureDate','FlightName', 'FlightCode', 
                               'DepTime','DepCity','FlightDuration',
                               'ArrivalTime','ArrivalCity','stops',
                               'fare','BaseFare','SurchargeFare','Discounts','sector','job_time']]
    
    if (stops >= 0):
        df = df.query("stops == "+str(stops))

    if len(df.index) == 0:
        return 0
    df['source'] = 'VIA.COM'
#    conn = MongoClient(config.DB_SERVER)
#    db = conn.database 
#    new_database = db.scrapedb  
#    data = df.to_dict(orient='records') 
#    result = new_database.insert_many(data)
    
    return df


if __name__ == '__main__':
    #url = 'https://in.via.com/flight/search?returnType=one-way&destination=DXB&bdestination=DXB&destinationL=Dubai%20Intl%20Arpt,Dubai&destinationCity=&destinationCN=&source=BLR&bsource=BLR&sourceL=Bangalore,Bangalore&sourceCity=&sourceCN=&month=2&day=25&year=2020&date=2/25/2020&numAdults=1&numChildren=0&numInfants=0&validation_result=&domesinter=international&livequote=-1&flightClass=ALL&travType=INTL&routingType=ALL&preferredCarrier=ALL&prefCarrier=0&isAjax=false'
    
    mydata = scrapenew_via_int('BKK','AMD','1/3/2020','1/3/2020','12/12/2019 16:48',
                       passengers='A-1_C-0_I-0', stops = 0 )