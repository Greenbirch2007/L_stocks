
# ! -*- coding:utf-8 -*-

# 2019.1.23  模型重新梳理，一次PL汇率换算，加上了手数的因素

import time
import re
import pymysql
import requests
from lxml import etree
from selenium import webdriver
# 还是要用PhantomJS
import datetime
import string

from math import floor


# 暂时没有找到洲际交易所的FTFE100好的数据源，官网行不通．所以这里直接用lse的官网的
# 的股票指数代替,这样在windows下也可以去跑脚本了
# 数据延迟，糟心！　算了就做一个定向统计即可
# 欧洲股票本来成交就相当的清淡,所以30秒钟请求一次即可!

# 测试3万美元
total_Cash = 30000 #初始资金是3完美元
index_Cash = (0.3) * total_Cash # index部位直接是美元，计算手数时不用进行汇率换算
stock_Cash = (0.6) *total_Cash
FX_price = 1.2856
index_Future_N =  floor(index_Cash/3587) # 向下取整
index_cost = 6830
stock_cost = 2550

# 2019.1.17  个股——————FTFE100指数模型测试


def get_index_PL():
    try :

        driver = webdriver.Chrome()
        url = 'http://quote.eastmoney.com/gb/zsFTSE.html'
        # driver = webdriver.PhantomJS(service_args=SERVICE_ARGS)
        driver.set_window_size(38, 12)  # 设置窗口大小
        driver.get(url)
        # time.sleep(1)
        html = driver.page_source
        patt = re.compile('<strong class=".*?" style="">(.*?)</strong>', re.S)
        items = re.findall(patt, html)
        for item in items:
            items_float = float(item)
            indexF_PL = (index_cost-items_float)*10*FX_price*index_Future_N # 点差，乘以每点10英镑，再乘以汇率换算成美元，再乘以手数
            indexF_PL_2 = round(indexF_PL,2)
            big_list.append(str(indexF_PL_2))
            driver.quit()
    except ValueError as e:
        pass


# CRANEWARE
def get_stocks_PL():
    url = 'https://www.londonstockexchange.com/exchange/prices-and-markets/stocks/summary/company-summary/GB00B2425G68GBGBXASQ1.html'
    headers = {'Useragent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0'}
    response = requests.get(url, headers=headers)
    content = response.text
    selector = etree.HTML(content)
    price = selector.xpath('//*[@id="pi-colonna1-display"]/div[1]/table/tbody/tr[1]/td[2]/text()')
    for items in price:  # 要把2,66.0的价格进行一次分隔然后拼接
        f_price = "".join(items.split(','))
        stock_PL = ((float(f_price) -stock_cost) /stock_cost) * stock_Cash # 直接用股价算出盈亏比率,然后直接套用股票总资金即可，还是美元

        stock_PL_2 = round(stock_PL, 2)
        big_list.append(stock_PL_2)


def profilo_PL():
    try:
        A = big_list[0]
        B = big_list[1]
        profilo_PL = float(B) + float(A)
        profilo_PL_2 = round(profilo_PL, 2)
        big_list.append(profilo_PL_2)
        total_profit_R = profilo_PL_2 / total_Cash
        total_profit_R_100 = total_profit_R *100 # 先换算成100进制
        total_profit_R_3 = round(total_profit_R_100, 3)   # 再保留3位数

        big_list.append(total_profit_R_3)

    except IndexError as e:
        print(e)


def insertDB(content):
    connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='web_monitor',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    # 这里是判断big_list的长度，不是content字符的长度
    if len(big_list) == 4:
        cursor.executemany(
            'insert into oneStock_FTSE100_PL (index_PL,stock_PL,profilo_PL,profilo_PL_R) values (%s,%s,%s,%s)', content)
        connection.commit()
        connection.close()
        print('向MySQL中添加数据成功！')
    else:
        print('出列啦')


# #
if __name__ == '__main__':
    i = 0
    while True:
        i += 1
        print(i)
        big_list = []
        get_index_PL()
        get_stocks_PL()
        profilo_PL()
        l_tuple = tuple(big_list)
        content = []
        content.append(l_tuple)
        insertDB(content)
        time.sleep(3)
#
# create table oneStock_FTSE100_PL(
# id int not null primary key auto_increment,
# index_PL varchar(10),
# stock_PL varchar(10),
# profilo_PL varchar(10),
# profilo_PL_R varchar(10)
# ) engine=InnoDB  charset=utf8;

# drop table oneStock_FTSE100_PL;
