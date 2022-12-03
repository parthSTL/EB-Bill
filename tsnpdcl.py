from unicodedata import name
from numpy import unicode_
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import warnings
import time
from tqdm import tqdm
from click import command
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import sqlite3
import time
from tqdm import tqdm
import datetime
import os
t=time.localtime()
warnings.filterwarnings("ignore")
conn = sqlite3.connect("eb_bill.db")
# cur=conn.cursor()
# command='ALTER TABLE tsnpdcl ADD COLUMN eroarea'
# cur.execute(command)
# conn.commit()
# df1=pd.read_excel(r'C:\Users\parth.pandey\Downloads/EB Master Data 11-aug-22.xlsx')
df1=pd.read_sql('SELECT * FROM lgd',conn)
# df1=df1[['Authority','USC Number']]
df1=df1[df1['Authority']=='TSNPDCL'][['Authority','USCNumber']]

# l=list(df1['USC Number'].dropna())
# df1.dropna(subset=['USCNumber'],inplace=True)
# df1['USCNumber']=df1['USCNumber'].astype(str)
# df1['USC Number']=df1['USC Number'].apply(lambda i: i.replace(u'\xa0', u''))
l=list(df1['USCNumber'])
print(len(l))
# df=pd.DataFrame(columns=['USC No','Previous reading','Current Reading','Last Date','Current Date','Addl. Charges',
#                         'Total Amount','New Amount'])

# usc=['10702218','16463561','16463565','16463563']

def extraction(l):
    no=0
    no_data_usc=[]
    driver = webdriver.Chrome(r"C:\Users\parth.pandey\Downloads\chromedriver_win32/chromedriver.exe")
    for i in tqdm(l):
        
        if len(re.findall('\d+',i))==0:
            continue
    #     if type(i)==str:
    #         continue
        no+=1
        # if no%100 ==0:
        #     print(no)
        try:
            
            prev_read=False
            curr_read=False
            last_date=False
            curr_date=False
            addl_chr=False
            tot_amt=False
            new_amt=False
            acd_amt=False
            arrear_amt=False
            energy_charge=False
            fixed_charge=False
            cust_charge=False
            adjustment=False
            other=False
            scno=False
            name=False
            ero_area=False
            unit=False
            webpage = r"https://tsnpdcl.in/Menu/KnowYourBillLT" # edit me
            driver.get(webpage)
            elem=driver.find_element(By.ID,"UscNo")
            elem.clear() 
            elem.send_keys(i)
            elem=driver.find_element(By.ID,"getBill")
            elem.click()
            tds=driver.find_elements(By.TAG_NAME,'td')
            for td in tds:
                j=td.text
                if not prev_read:
                    if 'Pv' in j:
                        if len(re.findall('\d+',j))>3: #Pv 832       05/09/2022      01
                            prev_read=j.split()[1]
                            last_date=j.split()[2]
                                
                if not curr_read:
                    if 'Ps' in j: # Ps 895       10/10/2022      01
                        if len(re.findall('\d+',j))>3:
                            curr_read=j.split()[1]
                            curr_date=j.split()[2]
                if not unit:
                    if 'UNITS:' in j: # UNITS:63            DAYS:30
                        unit=j.split(':')[-1]
                        unit=re.findall('\d+',unit)[0]
                if not addl_chr:
                    if 'Addl.' in j:
                        addl_chr=j.split()[-1]
                if not tot_amt:
                    if 'Total Amount' in j:
                        tot_amt=j.split()[-1]
                if not new_amt:
                    if 'New Amount' in j:
                        new_amt=j.split()[-1]
                if not acd_amt:
                    if 'Acd' in j:
                        acd_amt=j.split()[-1]
                if not arrear_amt:
                    if 'As on' in j:
                        arrear_amt=j.split()[-1]
                if not energy_charge:
                    if 'Energy Charges' in j:
                        energy_charge=j.split()[-1]
                if not fixed_charge:
                    if 'Fixed Charges' in j:
                        fixed_charge=j.split()[-1]
                if not cust_charge:
                    if 'Cust. Charges' in j:
                        cust_charge=j.split()[-1]
                if not adjustment:
                    if 'Adjustment' in j:
                        adjustment=j.split()[-1]
                if not scno:
                    if 'SCNO' in j:
                        if 'USCNO' in j:
                            continue
                        scno=j.split(':')[-1]
                if not name:
                    if 'NAME' in j:
                        name=j.split(':')[-1]
                if not ero_area:
                    if 'AAO/' in j:
                        ero_area=j.split('ERO/')[-1]
                        ero_area=ero_area.replace(' ','')

            # print(acd_amt)
            cur=conn.cursor()
            command="SELECT currentdate ,CASE WHEN currentdate == \'"+curr_date+"\' THEN 'no need to add' ELSE 'need to add' END AS result FROM tsnpdcl WHERE uscno = \'"+i+"\'"
            cur.execute(command)
            rows=cur.fetchall()
            if len(rows)==0 or rows[-1][1]=='need to add':
                # Insert new row
                other=round(float(tot_amt)+float(adjustment)-float(energy_charge)-float(fixed_charge)-float(cust_charge),2)
                command="INSERT INTO tsnpdcl (uscno, previousreading, currentreading, lastdate, currentdate, addlcharges, totalamount, newamount,acdamount,arrearamount, energycharge, fixedcharge, custcharge, adjustment, other, scno, name, eroarea,unit) VALUES (\'"+i+"\', \'"+prev_read+"\', \'"+curr_read+"\', \'"+last_date+"\', \'"+curr_date+"\', \'"+addl_chr+"\',\'"+tot_amt+"\',\'"+new_amt+"\',\'"+acd_amt+"\',\'"+arrear_amt+"\',\'"+energy_charge+"\',\'"+fixed_charge+"\',\'"+cust_charge+"\',\'"+adjustment+"\',\'"+str(other)+"\',\'"+str(scno)+"\',\'"+str(name)+"\',\'"+str(ero_area)+"\',\'"+str(unit)+"\')"
                cur.execute(command)

                # print('xxx>>>>><<<<<<xxx')
                conn.commit()
            # cur=conn.cursor()
            command="UPDATE tsnpdcl set eroarea=\'"+ero_area+"\' where uscno=\'"+str(i)+"\'"
            cur.execute(command)
            conn.commit()

            # print(3)

    
            # df=df.append({'USC No':i,'Previous reading':prev_read,'Current Reading':curr_read,'Last Date':last_date,
            #            'Current Date':curr_date,'Addl. Charges':addl_chr,'Total Amount':tot_amt,'New Amount':new_amt},ignore_index=True)
        except:
            # print('Error')
            # print(i)
            no_data_usc.append(i)
    return no_data_usc
l=extraction(l)
l=extraction(l)
with open("no_usc.txt", "a") as f:
    c=time.strftime("%D", t)
    f.write(f"{c}\n")
    f.write("TSNPDCL \n")    
    for i in l:
        f.write(f"{i}\t")
    f.write("\n")
# driver.close()