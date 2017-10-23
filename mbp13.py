#-*- coding:utf-8 -*-

import os.path
import datetime

# database
import sqlite3

# parser
import urllib.request
from bs4 import BeautifulSoup
import re

def create_db (db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    create_table_old = '''CREATE TABLE mbp13_old (name text, release text, ram int, ssd int, updated text);'''
    create_table_now = '''CREATE TABLE mbp13_now (name text, release text, ram int, ssd int, updated text);'''
    c.execute(create_table_old)
    c.execute(create_table_now)

    conn.commit()
    conn.close()

def delete_table (db_name, table_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    delete_sql = 'drop table ' + table_name
    c.execute(delete_sql)
    create_table_now = '''CREATE TABLE mbp13_now (name text, release text, ram int, ssd int, updated text);'''
    c.execute(create_table_now)

    conn.commit()
    conn.close()

def check_exist_db (db_name):
    if os.path.exists(db_name):
        delete_table(db_name, 'mbp13_now')
    else:
        # create database
        create_db(db_name)

def update_db (db_name, product_name, release, ram, ssd):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    now = datetime.datetime.today()
    updated_time = now.strftime('%Y-%m-%d-%H-%S')

    # Compare whether 'product_name' already exists in the 'mbp13.db'
    sql = 'insert into mbp13_now (name, release, ram, ssd, updated) values (?,?,?,?,?)'
    product_data = (product_name, release, ram, ssd, updated_time)
    c.execute(sql, product_data)

    # print(product_name)

    conn.commit()
    conn.close()

def duplicate_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # delete old table
    delete_sql = 'drop table mbp13_old'
    c.execute(delete_sql)
    # duplicate mbp13_now
    duplicate_sql = 'create table mbp13_old as select * from mbp13_now'
    c.execute(duplicate_sql)

    conn.commit()
    conn.close()

def compare_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    print ('old')
    list_sql = 'select * from mbp13_old'
    for row in c.execute(list_sql):
        print(row)
    print ('\nnow')
    list_sql = 'select * from mbp13_now'
    for row in c.execute(list_sql):
        print(row)

    print('\ncompare')
    # Show list of Out of stock from last time
    compare_sql = 'select * from mbp13_now where updated <> (select updated from mbp13_old limit 1)'
    for row in c.execute(compare_sql):
        print(row)

    conn.close()

if __name__ == '__main__':
    db_name = 'mbp13.db'

    check_exist_db (db_name)

    url = 'https://www.apple.com/jp/shop/browse/home/specialdeals/mac/macbook_pro/13'
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    # Get content in tag <div class="box-content">
    main_content = soup.find('div', class_='box-content')

    duplicate_db(db_name)

    for content in main_content.find_all('td', class_='specs'):
        # Get product name and list of ram and ssd size
        # strip() remove space, tab and new line
        # &nbsp translated '\xa0'. replace to ' '
        product_name = content.h3.a.string.strip().replace('\xa0', ' ')
        release_date = content.find_all(text=re.compile("年"))[0].strip()
        spec_data_list = content.find_all(text=re.compile("GB"))

        # Parse size of ram and ssd from spec_data_list
        ram_and_ssd_size = ''
        for spec_data in spec_data_list:
            ram_and_ssd_size += re.findall('[0-9]*GB' , spec_data.string)[0] + ','

        ram_and_ssd_size = ram_and_ssd_size.split(',')
        get_only_numeral_pattern = '([+-]?[0-9]+\.?[0-9]*)'

        # re.findall() return list of string. To get Integer 'int(re.finadll(...)[0])'
        ram_size = int(re.findall(get_only_numeral_pattern , ram_and_ssd_size[0])[0])
        ssd_size = int(re.findall(get_only_numeral_pattern , ram_and_ssd_size[1])[0])

        update_db(db_name, product_name, release_date, ram_size, ssd_size)

    compare_db(db_name)
