#-*- coding:utf-8 -*-

import os.path
import datetime

# database
import sqlite3

# parser
import urllib.request
from bs4 import BeautifulSoup

def create_db (db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    create_table = '''CREATE TABLE mbp13 (name text, ram int, ssd int, updated text);'''
    c.execute(create_table)

    conn.commit()
    conn.close()

def check_exist_db (db_name):
    if os.path.exists(db_name):
        # exists database
        pass
    else:
        # create database
        create_db(db_name)

def update_db (db_name, product_name, ram, ssd):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    now = datetime.datetime.today()
    updated_time = now.strftime('%Y-%m-%d-%H')
    # Compare whether 'product_name' already exists in the 'mbp13.db'
    sql = 'insert into mbp13 (name, ram, ssd, updated) values (?,?,?,?)'
    user = (product_name, ram, ssd, updated_time)
    c.execute(sql, user)

    select_sql = 'select * from mbp13'
    for row in c.execute(select_sql):
        print(row)

    conn.close()

import re
if __name__ == '__main__':
    db_name = 'mbp13.db'

    check_exist_db (db_name)

    url = 'https://www.apple.com/jp/shop/browse/home/specialdeals/mac/macbook_pro/13'
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    # Get content in tag <div class="box-content">
    main_content = soup.find('div', class_='box-content')

    for content in main_content.find_all('table'):
        # Parse <table><h3><a> title_data </a></h3></table> 
        title_data = content.h3.a.string
        print (title_data)
    for content in main_content.find_all('td', class_='specs'):
        # Get list of items with GB at the end
        spec_data_list = content.find_all(text=re.compile("GB"))

        # Parse size of ram and ssd from spec_data(list)
        for spec_data in spec_data_list:
            print (spec_data.string)
            print (re.findall('[0-9]*GB' , spec_data.string)[0])
            
    update_db(db_name, "product_name2", 8, 256)
