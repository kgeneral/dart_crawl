# coding=utf-8                           #
# this is for coding in utf-8            #
####Caution###############################
# This code doesn't work in Web Compiler #
##########################################
#STEP 1
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import webbrowser

#STEP 2
auth_key="edc2a306984216f5d53315315d4955e1ea5c2035" #authority key
company_code="024110" #company code
start_date="1990101"

#STEP 3
url = "http://dart.fss.or.kr/api/search.xml?auth="+auth_key+"&crp_cd="+company_code+"&start_dt="+start_date+"&bsn_tp=A001&bsn_tp=A002&bsn_tp=A003"

#STEP 4
resultXML=urlopen(url)  #this is for response of XML
result=resultXML.read() #Using read method

#STEP 5
xmlsoup=BeautifulSoup(result,'html.parser')

#STEP 6
data = pd.DataFrame()

te=xmlsoup.findAll("list")

for t in te:
    temp=pd.DataFrame(([[t.crp_cls.string,t.crp_nm.string,t.crp_cd.string,t.rpt_nm.string,
        t.rcp_no.string,t.flr_nm.string,t.rcp_dt.string, t.rmk.string]]),
        columns=["crp_cls","crp_nm","crp_cd","rpt_nm","rcp_no","flr_nm","rcp_dt","rmk"])
    data=pd.concat([data,temp])

#STEP 7
data=data.reset_index(drop=True)

#OPTIONAL
#print(data)
user_num=int(input("몇 번째 보고서를 확인하시겠습니까?"))
url_user="http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+data['rcp_no'][user_num]
#print(url_user)
#webbrowser.open(url_user)

#######################################2장####################################

#STEP 1
import requests
import lxml.html
import re

url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+data['rcp_no'][user_num]
req = requests.get(url)
tree = lxml.html.fromstring(req.text)
onclick = tree.xpath('//*[@id="north"]/div[2]/ul/li[1]/a')[0].attrib['onclick']
pattern = re.compile("^openPdfDownload\('\d+',\s*'(\d+)'\)")
dcm_no = pattern.search(onclick).group(1)
url_parsing="http://dart.fss.or.kr/report/viewer.do?rcpNo="+data['rcp_no'][user_num]+"&dcmNo="+dcm_no+"&eleId=15&offset=1489233&length=105206&dtd=dart3.xsd"

#STEP 2
report=urlopen(url_parsing)
r=report.read()

from html_table_parser import parser_functions as parser

#STEP 3
xmlsoup_another=BeautifulSoup(r,'html.parser')
body=xmlsoup_another.find("body")
table=body.find_all("table")
p = parser.make2d(table[3])

sheet = pd.DataFrame(p[2:], columns=["구분","38기반기_3개월","38기반기_누적","37기반기_3개월","37기반기_누적"])

#STEP 4
sheet["38기반기_3개월"]=sheet["38기반기_3개월"].str.replace(",","")
sheet["temp"]=sheet["38기반기_3개월"].str[0]

sheet.ix[sheet["temp"]=="(","38기반기_3개월"]=sheet["38기반기_3개월"].str.replace("(","-")
sheet["38기반기_3개월"]=sheet["38기반기_3개월"].str.split(")").str[0]
sheet.ix[sheet["38기반기_3개월"]=="","38기반기_3개월"]="0"
sheet["38기반기_3개월"]=sheet["38기반기_3개월"].astype(int)

#STEP 5
sale = sheet[sheet["구분"]=="매출액"].iloc[0,1]
sale_cost = sheet[sheet["구분"]=="매출원가"].iloc[0,1]
sale_profit_ratio=(sale-sale_cost)/sale*100

# round는 반올림
sale_profit_ratio=round(sale_profit_ratio,1)
print("매출총이익률은 "+str(sale_profit_ratio)+"% 입니다")