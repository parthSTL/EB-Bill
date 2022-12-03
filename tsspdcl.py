import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import sqlite3
import numpy as np
import time
from tqdm import tqdm
import re
t=time.localtime()

conn = sqlite3.connect("eb_bill.db")

# df1=pd.read_excel(r'C:\Users\parth.pandey\Desktop\TFiber Project\EB Bill/EB Master Data 11-aug-22.xlsx')
df1=pd.read_sql('SELECT * FROM lgd',conn)
df1=df1[['Authority','USCNumber']]
df1=df1[df1['Authority']=='TSSPDCL']
# l=list(df1['USC Number'].dropna())
# df1.dropna(subset=['USC Number'],inplace=True)
# df1['USC Number']=df1['USC Number'].astype(str)
# df1['USC Number']=df1['USC Number'].apply(lambda i: i.replace(u'\xa0', u''))
l=list(df1['USCNumber'])

# df=pd.DataFrame(columns=['USCNo','SerialNo','BillDate','DueDate','BillAmount','ACDAmount','Amount'])

driver = webdriver.Chrome(r"C:\Users\parth.pandey\Downloads\chromedriver_win32/chromedriver.exe")

def extraction(l):
    j=0
    no_usc=[]
    for i in tqdm(l):
        if len(re.findall('\d+',i))==0:
            continue
        j+=1
        # if j%100==0:
        # #     print(j)
        webpage = r"https://www.billdesk.com/pgidsk/pgmerc/tsspdclpgi/TSSPDCLPGIDetails.jsp#" # edit me
        
        try:
            driver.get(webpage)
            elem = driver.find_element(By.NAME, "uscno")
            # print(elem)
            elem.clear()
            elem.send_keys(str(i))
            elem=driver.find_element(By.NAME, "txtEmailID")
            elem.clear()
            elem.send_keys('xyz@jj.com')
            # elem.send_keys(Keys.RETURN)
            # submit.click()
            elem=driver.find_element(By.NAME, "makePayment")
            elem.click()
            elem=driver.find_element(By.NAME, "uniqueno")
            usc_no=elem.get_attribute('value')
            usc_no=usc_no.replace(' ','')
    #         print(usc_no)
            
            elem=driver.find_element(By.NAME, "txtCustomerID")
            ser_no=elem.get_attribute('value')
            ser_no=ser_no.replace(' ','')
    #         print(ser_no)
            elem=driver.find_element(By.NAME, "bill_date")
            bill_date=elem.get_attribute('value')
            bill_date=bill_date.replace(' ','')
    #         print(bill_date)
            elem=driver.find_elements(By.NAME, "due_date")
            due_date=elem[0].get_attribute('value')
            due_date=due_date.replace(' ','')
    #         print(due_date)
            bill_amt=elem[1].get_attribute('value')
            bill_amt=bill_amt.replace(' ','')
    #         print(bill_amt)
            acd_amt=elem[2].get_attribute('value')
            acd_amt=acd_amt.replace(' ','')
    #         print(acd_amt)
            elem=driver.find_element(By.NAME, "txtTxnAmount")
            amount=elem.get_attribute('value')
            amount=amount.replace(' ','')
    #         print(amount)
            # Introducing SQL Commands to check and insert new bill data
            cur = conn.cursor()
            command="SELECT billdate ,CASE WHEN billdate == \'"+bill_date+"\' THEN 'no need to add' ELSE 'need to add' END AS result FROM tsspdcl WHERE uscno = \'"+usc_no+"\'"
            cur.execute(command)
            rows=cur.fetchall()
        #     print(1)
            if len(rows)==0 or rows[-1][1]== 'need to add':
                # Insert new row
                command="INSERT INTO tsspdcl (uscno, serialno, billdate, duedate, billamount, acdamount, amount) VALUES (\'"+usc_no+"\', \'"+ser_no+"\', \'"+bill_date+"\', \'"+due_date+"\', \'"+bill_amt+"\', \'"+acd_amt+"\',\'"+amount+"\')"
                cur.execute(command)
                # print('xxx>>>>><<<<<<xxx')
                conn.commit()
        except:
        #     print(i)
        #     print(2)
            no_usc.append(i)
    return no_usc
l=extraction(l[1000:])
l=extraction(l)
with open("no_usc.txt", "a") as f:
    c=time.strftime("%D", t)
    f.write(f"{c}\n")
    f.write("TSSPDCL \n")    
    for i in l:
        f.write(f"{i}\t")
    f.write("\n")
driver.close()