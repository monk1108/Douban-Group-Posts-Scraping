from bs4 import BeautifulSoup
import sqlite3
import requests
import urllib.request
import urllib.parse
import json
import re
import time
import random


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
    'Cookie': '',
    'Host': 'www.douban.com', 
    'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}


# Parse HTML and extract necessary content
def extract_article(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Page count
    try:
        page_count = soup.find('span', class_='thispage')['data-total-page']
    except:
        page_count = 1
    page_count = int(page_count)

    # Extract article
    article = soup.find('script', type='application/ld+json')
    if article:
        article_str = article.string.strip()
        article_str = re.sub(r'\s+', '', article_str)
        # Title
        article_name = json.loads(article_str)['name']
        # Body
        article_text = json.loads(article_str)['text']
    else:
        article_text = None
    
    return article_name, article_text, page_count

# Define function to extract comments of one page
def extract_comments(html):
    soup = BeautifulSoup(html, 'html.parser')
    comments = []
    comment_items = soup.find_all('li', class_='comment-item')
    for item in comment_items:
        reply_content = item.find('p', class_='reply-content').text.replace('\n', ' ')
        comments.append(reply_content)
    return comments

# Define function to extract comments of all pages
def extract_all_comments(url, page_count):
    all_comments = []
    page = 1
    for page in range(1, page_count + 1):
        # Access page to get HTML content, the URL here needs to be constructed according to actual situation
        page_url = url + '?start=' + str((page - 1) * 100)

        # Wrap URL, headers
        request = urllib.request.Request(url=page_url, headers=headers)
        # Send request
        response = urllib.request.urlopen(request)
        time.sleep(5 + random.random() - 1)
        # Read result
        reply_content = response.read().decode('utf-8')

        comments = extract_comments(reply_content)
        all_comments.extend(comments)
        page += 1

    return all_comments


def insert_data(url, article, comments, replys, table_name):
    conn = sqlite3.connect('douban_posts.db')
    c = conn.cursor()
    
    # Create table
    c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 url TEXT,
                 article TEXT,
                 contents TEXT,
                 replys TEXT)''')
    
    # Convert comments and replies lists to JSON strings
    comments_json = json.dumps(comments, ensure_ascii=False)
    replys_json = json.dumps(replys, ensure_ascii=False)

    # Insert data
    # Construct SQL query
    sql = f"INSERT INTO {table_name} (url, article, contents, replys) VALUES (?, ?, ?, ?)"
    
    # Execute SQL query
    c.execute(sql, (url, article, comments_json, replys_json))

    conn.commit()
    conn.close()

# Process multiple HTML files 
def process_files_from_database(table_name, new_table_name):
    conn = sqlite3.connect('douban_posts.db')
    c = conn.cursor()
    c.execute(f"SELECT subject, href FROM {table_name}")
    rows = c.fetchall()

    num = 0
    for row in rows:
        print("Processing post number {}".format(num + 1))
        subject, url = row
        # Wrap URL, headers
        request = urllib.request.Request(url=url, headers=headers)
        # Send request
        response = urllib.request.urlopen(request)
        # sleep for about 5 seconds, random -1 ~ 1 second
        time.sleep(5 + random.random() - 1)
        
        # Read result
        html_content = response.read().decode('utf-8')

        article, comments, page_count = extract_article(html_content)  # Pass subject and link information
        replys = extract_all_comments(url, page_count)
        insert_data(url, article, comments, replys, new_table_name)

        num += 1
    

# Specify table name
table_name = input("Please enter the database table name: ")
new_table_name = table_name + '_content'

# Process multiple HTML files and insert data into the database
process_files_from_database(table_name, new_table_name)
