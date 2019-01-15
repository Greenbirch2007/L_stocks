# -*- coding:utf-8 -*-
import datetime
import re
import time

from requests.exceptions import RequestException
import pymysql
import requests

from lxml import etree
from selenium import webdriver

# driver = webdriver.Chrome()


def call_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

# def get_first_page(url):
#     driver.get(url)
#     html = driver.page_source
#     time.sleep(1)
#     return html


# 可以尝试第二种解析方式，更加容易做计算
def parse_stock_note(html):
    big_list = []
    base_url_finan = 'https://www.londonstockexchange.com/exchange/prices/stocks/summary/fundamentals.html?fourWayKey='
    base_url_value = 'https://www.londonstockexchange.com/exchange/prices-and-markets/stocks/exchange-insight/news-analysis.html?fourWayKey='
    selector = etree.HTML(html)
    code = selector.xpath('//*[@id="fullcontainer"]/div[1]/table/tbody/tr/td[1]/text()')
    name= selector.xpath('//*[@id="fullcontainer"]/div[1]/table/tbody/tr/td[2]/a/text()')
    link_s = selector.xpath('//*[@id="fullcontainer"]/div[1]/table/tbody/tr/td[2]/a/@href')
    cur= selector.xpath('//*[@id="fullcontainer"]/div[1]/table/tbody/tr/td[3]/text()')
    price= selector.xpath('//*[@id="fullcontainer"]/div[1]/table/tbody/tr/td[4]/text()')
    for i1,i2,i3,i4,i5 in zip(code,name,link_s,cur,price):
        keyway = i3[-26:-5]
        finan_url = base_url_finan+str(keyway)
        value_url = base_url_value+ str(keyway)
        big_tuple = (i1,i2,finan_url,value_url,i4,i5)
        big_list.append(big_tuple)
    return big_list









# def Python_sel_Mysql():
#     # 使用cursor()方法获取操作游标
#     connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='lse_stock',
#                                  charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
#     cur = connection.cursor()
#     #sql 语句
#     for i in range(1,2481):
#         sql = 'select code from hk_stock where id = %s ' % i
#         # #执行sql语句
#         cur.execute(sql)
#         # #获取所有记录列表
#         data = cur.fetchone()
#         num = data['code']
#         url = 'http://stock.finance.sina.com.cn/hkstock/finance/' + str(num) + '.html#a4'
#         yield url



def insertDB(content):
    connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='lse_stock',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    cursor = connection.cursor()
    try:
        cursor.executemany('insert into les_coding (code,name,link_finan,link_value,cur,price) values (%s,%s,%s,%s,%s,%s)', content)
        connection.commit()
        connection.close()
        print('向MySQL中添加数据成功！')
    except TypeError :
        pass



if __name__ == '__main__':
    for num in range(1,238):
        url = 'https://www.londonstockexchange.com/exchange/prices-and-markets/stocks/main-market/main-market.html?&page=' + str(num)
        html = call_page(url)
        content = parse_stock_note(html)
        insertDB(content)

        time.sleep(1)






#
# create table les_coding(
# id int not null primary key auto_increment,
# code varchar(16),
# name varchar(30),
# link_finan varchar(150),
# link_value varchar(150),
# cur varchar(10),
# price varchar(16)
# ) engine=InnoDB default charset=utf8;
# #
# #
# drop table les_coding;

