# References:
# https://zhuanlan.zhihu.com/p/42053431
# https://darktiantian.github.io/%E8%AE%B0%E4%B8%80%E6%AC%A1%E6%B7%98%E5%AE%9D%E6%8E%A5%E5%8F%A3sign%E7%AD%BE%E5%90%8D%E7%A0%B4%E8%A7%A3/
# https://onejane.github.io/2021/04/25/JS%E9%80%86%E5%90%91%E4%B9%8B%E6%B7%98%E5%AE%9Dh5%E8%A7%86%E9%A2%91sign%E7%A0%B4%E8%A7%A3/#%E5%88%86%E6%9E%90
# https://zhuanlan.zhihu.com/p/655304909
# http://t.csdnimg.cn/EKgSr
# https://github.com/xzh0723/Taobao/tree/master
# http://t.csdnimg.cn/8umoV
# Crawling is set to 20 pages
# If it can't run, it means the cookie has expired, reset it

# URL convert: https://tool.chinaz.com/tools/urlencode.aspx

import urllib.request
import urllib.parse
import json
from openpyxl import Workbook
import requests
import csv
import time
from bs4 import BeautifulSoup
import sqlite3
import time

# product_name = input("Please enter the product name you want to crawl: ")
# start_page = int(input("Start page: "))
# end_page = int(input("End page: "))
product_name = input("Please enter the content you want to crawl: ")
schema = input("Please enter the database table name: ")

# Establish database connection
conn = sqlite3.connect('douban_posts.db')
c = conn.cursor()

# Create table
sql_create = 'CREATE TABLE IF NOT EXISTS ' + schema + ' (id INTEGER PRIMARY KEY AUTOINCREMENT,\
            subject TEXT,\
            href TEXT,\
            time TEXT,\
            replies TEXT,\
            group_name TEXT)'
c.execute(sql_create)

conn.commit()

page_num = 0
while True:
    print(f'Fetching page {page_num + 1}')

    # https://www.douban.com/group/search?cat=1013&q=%E6%9D%8E%E4%BA%91%E8%BF%AA&sort=relevance
    url = 'https://www.douban.com/group/search?start=' + str(50 * int(page_num)) + '&cat=1013&q=' + urllib.parse.quote(product_name) + '&sort=relevance'
    
    # TODO: Cookie needs to be updated each time
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Cookie': '',
        'Host': 'www.douban.com', 
        'Referer': url,
        'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }

    # Wrap URL, headers
    request = urllib.request.Request(url=url, headers=headers)
    # Send request
    response = urllib.request.urlopen(request)
    # Read result
    content = response.read().decode('utf-8')

    soup = BeautifulSoup(content, 'html.parser')
    # Extract information from each post
    posts = []
    
    if len(soup.find_all('tr', class_='pl')) == 0:
        break

    for tr in soup.find_all('tr', class_='pl'):
        subject_tag = tr.find('td', class_='td-subject').find('a')
        subject = subject_tag.text.strip()
        href = subject_tag['href']
        post_time = tr.find('td', class_='td-time').text.strip()
        replies = tr.find('td', class_='td-reply').text.strip()
        group = tr.find('td').find_next_sibling().text.strip()

        # Insert data into database
        sql_insert = "INSERT INTO " + schema + " (subject, href, time, replies, group_name) VALUES (?, ?, ?, ?, ?)"
        c.execute(sql_insert, (subject, href, post_time, replies, group))

    page_num += 1
    # sleep for 5 seconds
    time.sleep(5)

conn.commit()
conn.close()
