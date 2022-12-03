import sqlite3
import pandas as pd
conn=sqlite3.connect(r'C:\Users\parth.pandey\Desktop\TFiber Project\EB Bill/eb_bill.db')
df=pd.read_sql('''select lgd.package,lgd.zone,lgd.dist,lgd.mandal,lgd.gpname,lgd.zonemandalgp,lgd.lgdcode,tsnpdcl.uscno,
tsnpdcl.previousreading,tsnpdcl.currentreading,tsnpdcl.lastdate,tsnpdcl.currentdate,
tsnpdcl.addlcharges,tsnpdcl.totalamount,tsnpdcl.newamount,tsnpdcl.acdamount,tsnpdcl.arrearamount,
tsnpdcl.energycharge,tsnpdcl.fixedcharge,tsnpdcl.custcharge,tsnpdcl.adjustment,tsnpdcl.other,tsnpdcl.scno,tsnpdcl.name,tsnpdcl.eroarea, tsnpdcl.unit
FROM tsnpdcl
LEFT JOIN lgd ON tsnpdcl.uscno== lgd.uscnumber''',conn)
df1=pd.read_sql('''SELECT lgd.package,lgd.zone,lgd.dist,lgd.mandal,lgd.gpname,lgd.zonemandalgp,lgd.lgdcode,tsspdcl.uscno,
tsspdcl.serialno,tsspdcl.billdate,tsspdcl.duedate,tsspdcl.billamount,tsspdcl.acdamount,tsspdcl.amount
from tsspdcl left join lgd on lgd.uscnumber==tsspdcl.uscno''',conn)
df2=pd.read_sql('''SELECT lgd.package,lgd.zone,lgd.dist,lgd.mandal,lgd.gpname,lgd.zonemandalgp,lgd.lgdcode,
cess.uscno,cess.areacode,cess.billmonth,cess.billdate,cess.billno,cess.totalbillamt,
cess.unit, cess.arrearamount
from cess left join lgd on lgd.uscnumber==cess.uscno''',conn)
df.to_csv('tsnpdcl.csv',index=False)
df1.to_csv('tsspdcl.csv',index=False)
df2.to_csv('cess.csv',index=False)
conn.close()