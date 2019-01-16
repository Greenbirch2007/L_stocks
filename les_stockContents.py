# -*- coding:utf-8 -*-
import datetime
import re
import time

from requests.exceptions import RequestException
import pymysql
import requests

from lxml import etree
from selenium import webdriver
#
# driver = webdriver.Chrome()
#
# def get_first_page(url):
#     driver.get(url)
#     html = driver.page_source
#     time.sleep(1)
#     return html
# 爬虫会有请求阻塞的问题！
# 也有可能是请求的页面是没有数据的！所以！即使收手！

def call_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None





# 可以尝试第二种解析方式，更加容易做计算
def parse_stock_note(html):
    big_list = []
    f_list  = []
    selector = etree.HTML(html)
    P_L = selector.xpath('//*[@id="pi-colonna1-display"]/div[2]/table/tbody/tr[3]/td/text()')
    industry= selector.xpath('//*[@id="pi-colonna2"]/div[6]/table/tbody/tr[3]/td[2]/text()')
    M_value = selector.xpath('//*[@id="pi-colonna2"]/div[10]/table/tbody/tr[11]/td[2]/text()')
    name = selector.xpath('/html/body/div[4]/div/div[3]/div[1]/div[1]/ol/li[4]/b/text()')
    for i1 in name:
        name_s = i1.split('\r\n')
        big_list.append(name_s[0])
    for i1 in P_L[1:]:
        i1_s = i1.split('\r\n')
        big_list.append(i1_s[1])
    for i1,i2 in zip(industry,M_value):
        big_list.append(i1)
        big_list.append(i2)
    b_l_t = tuple(big_list)
    f_list.append(b_l_t)
    return f_list


def insertDB(content):
    connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='lse_stock',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    cursor = connection.cursor()
    try:
        cursor.executemany('insert into les_stock_contents (name,d1,d2,d3,d4,d5,industry,m_value) values (%s,%s,%s,%s,%s,%s,%s,%s)', content)
        connection.commit()
        connection.close()
        print('向MySQL中添加数据成功！')
    except TypeError :
        pass


def Python_sel_Mysql():
    # 使用cursor()方法获取操作游标
    connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', db='lse_stock',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = connection.cursor()
    #sql 语句
    for i in range(2070,4736):
        sql = 'select link_finan from les_coding where id = %s ' % i
        # #执行sql语句
        cur.execute(sql)
        # #获取所有记录列表
        data = cur.fetchone()
        url = data['link_finan']
        yield url

if __name__ == '__main__':

    for url_str in Python_sel_Mysql():
        html = call_page(url_str)
        content = parse_stock_note(html)
        insertDB(content)
        print(datetime.datetime.now())




# #
# create table les_stock_contents(
# id int not null primary key auto_increment,
# name varchar(20),
# d1 varchar(10),
# d2 varchar(10),
# d3 varchar(10),
# d4 varchar(10),
# d5 varchar(10),
# industry varchar(100),
# m_value varchar(16)
# ) engine=InnoDB default charset=utf8;
# # #
# #
# drop table les_stock_contents;

