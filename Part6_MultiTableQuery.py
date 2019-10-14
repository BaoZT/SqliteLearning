import sqlite3
import os
import time


'''
    该脚本用于验证从已有数据库（Part4创建）中查询指定的纪录消息
    查询条件：时间段+左右系+主备情况
'''

data_base = sqlite3.connect('CR400BF_5113_08_record_base')
cursor = data_base.cursor()

def record_db_query(start=int, stop=int, )