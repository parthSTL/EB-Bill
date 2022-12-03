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
conn = sqlite3.connect("eb_bill.db")
df1=pd.read_sql('SELECT * FROM lgd',conn)
# l=list(df1[df1['Authority']=='CESS']['USCNumber'])


# df1=pd.read_excel(r'C:\Users\parth.pandey\Downloads/EB Master Data 11-aug-22.xlsx')
df1=df1[['Authority','USCNumber']]
df1=df1[df1['Authority']=='CESS']

df1.dropna(subset=['USCNumber'],inplace=True)
df1['USCNumber']=df1['USCNumber'].astype(str)
df1['USCNumber']=df1['USCNumber'].apply(lambda i: i.replace(u'\xa0', u''))
df1['USCNumber']=df1['USCNumber'].apply(lambda i: i.replace(' ', ''))
l=list(df1['USCNumber'])


st=time.time()
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# df=pd.DataFrame(columns=['uscno','areacode','billmonth','billdate','billno','totalbillamt'])
# uscno='8081901729'
# uscno=uscno.strip()
driver = webdriver.Chrome(r"C:\Users\parth.pandey\Downloads\chromedriver_win32/chromedriver.exe")
def extraction(l):
    nousc=[]
    # if len(uscno)==10:
    #     uscno=uscno[:5]+' '+uscno[5:]
    
    for uscno_ in tqdm(l):
        areacode=''
        billmonth=''
        billdate=''
        billno=''
        unit=''
        totalbillamt=''
        try:
            uscno=uscno_.strip()
            if len(uscno)==10:
                uscno=uscno[:5]+' '+uscno[5:]
            else:
                continue
            webpage = r"http://www.cesssircilla.com/gprsBillReportDetails" # edit me
            driver.get(webpage)
            elem=driver.find_element(By.NAME,"id.serviceNo")
            elem.clear()
            elem.send_keys(uscno)
            elem=driver.find_element(By.ID,"submit")
            elem.click()
            # print('OK1')
            elem=driver.find_element(By.XPATH,"//div[@class='dataTables_scrollBody']/table/tbody")
            # print(elem.text)
            time.sleep(1)
            trs=elem.find_elements(By.TAG_NAME,'tr')
            for tr in trs:
                tds=tr.find_elements(By.TAG_NAME,'td')
                for tds_ind in range(len(tds)):
                    if tds_ind==2:
                        areacode=tds[tds_ind].text
                    if tds_ind==3:
                        billmonth=tds[tds_ind].text
                    if tds_ind==4:
                        billdate=tds[tds_ind].text
                    if tds_ind==5:
                        billno=tds[tds_ind].text
                    if tds_ind==6:
                        unit=tds[tds_ind].text
                    if tds_ind==7:
                        totalbillamt=tds[tds_ind].text
                # print('OK2')
                # df=df.append({'uscno':uscno_,    'areacode':areacode,'billmonth':billmonth,    'billdate':billdate,'billno':billno,
                #           'unit':unit,    'totalbillamt':totalbillamt},ignore_index=True)
                cur=conn.cursor()
                command="SELECT billdate, CASE WHEN billdate==\'"+billdate+"\' THEN 'no need to add' ELSE 'need to add' END AS result FROM cess WHERE uscno=\'"+uscno_+"\'"
                cur.execute(command)
                rows=cur.fetchall()
                # print('OK3')
                add=True
                for i in rows:
                    if i[1]=='no need to add':
                        add=False
                        break
                if len(rows)==0 or add:
                    # print(uscno_)
                    
                    command="INSERT INTO cess (uscno,areacode,billmonth,billdate,billno,unit,totalbillamt) VALUES (\'"+uscno_+"\',\'"+areacode+"\',\'"    +billmonth+"\',\'"+billdate+"\',\'"+billno    +"\',\'"+unit+"\',\'"+totalbillamt+"\')"
                    cur.execute(command)
                    # print('OK4')
                    conn.commit()
                    # print('----<>----')    
                # else:
                #     print('Not add')
        except:
            nousc.append(uscno_)
    return nousc
# l=extraction(l)
# l=extraction(l)

# driver.close()
# with open("no_usc.txt", "a") as f:
#     c=time.strftime("%D", t)
#     f.write(f"{c}\n")
#     f.write("CESS \n")    
#     for i in l:
#         f.write(f"{i}\t")
#     f.write("\n")

# l=list(df1['USC Number'])
def extraction_(l):
    nousc=[]
    # if len(uscno)==10:
    #     uscno=uscno[:5]+' '+uscno[5:]
    
    for uscno_ in tqdm(l):
        arrearamount=''
        # print(uscno_)
        # try:
        uscno=uscno_.strip()
        # print(uscno_)
        if len(uscno)==10:
            uscno=uscno[:5]+' '+uscno[5:]
        else:
            continue
        webpage = r"http://www.cesssircilla.com/LTMakePayMent" # edit me
        try:
            driver.get(webpage)
            elem=driver.find_element(By.ID,"csmServiceNo")
            elem.clear()
            elem.send_keys(uscno)
            elem=driver.find_element(By.XPATH,"//div[@class='col-sm-2']/input")
            elem.click() # Clicking on webpage

            elem=driver.find_element(By.XPATH,"//div[@class='form-group'][6]/div")
            arrearamount=elem.text
            # Extracting Arrear Amount
            elem=driver.find_element(By.XPATH,"//div[@class='form-group'][4]/div")
            billdate=elem.text
            billdate=billdate[:10]
            billdate=datetime.datetime.strptime(billdate,'%Y-%m-%d')
            # print(billdate)
            cur=conn.cursor()
            command="SELECT billmonth, arrearamount FROM cess WHERE uscno=\'"+uscno_+"\'"
            cur.execute(command)
            rows=cur.fetchall()
            for row in rows:
                cur_date=datetime.datetime.strptime(row[0],'%m-%Y')
                # print(cur_date)
                # command="SELECT arrearamount FROM cess WHERE uscno=\'"+uscno_+"\'"
                # cur.execute(command)
                # print(row)
                # rows=cur.fetchall()
                cur_arrear=row[1]
                # print(cur_date.month, cur_date.year)
                # print(billdate.month, billdate.year)
                # print(arrearamount,cur_arrear)
                if cur_date.month==billdate.month and cur_date.year==billdate.year and arrearamount!=cur_arrear:
                    command="UPDATE cess SET arrearamount= \'"+arrearamount+"\' WHERE uscno=\'"+uscno_+"\' AND billmonth=\'"+row[0]+"\'"
                    cur.execute(command)
                    conn.commit()
                    print('----<>----')
                #############################
                # driver.execute_script("document.body.style.zoom='50%'")# Zoom out
                # os.chdir('Bill-Image')
                # if str(cur_date.month)+'-'+str(cur_date.year) not in os.listdir():
                #     os.mkdir(os.getcwd()+'/'+ str(cur_date.month)+'-'+str(cur_date.year))
                # os.chdir(str(cur_date.month)+'-'+str(cur_date.year))
                # driver.get_screenshot_as_file(uscno_+'.jpg')
                # os.chdir('..')
                # os.chdir('..')
            #############################
        except:
            nousc.append(uscno_)    
    return nousc
l=list(df1['USCNumber'])
amt_l=extraction(l)
amt_l=extraction(amt_l)
print(amt_l)
l=list(df1['USCNumber'])
arr_l=extraction_(l)
arr_l=extraction_(arr_l)
print(arr_l)
driver.close()
end=time.time()
print(end-st)
