import sqlite3
import os
import time
from os import path
from RecordParser.MsgInfoAcquire import MsgProcess
from RecordParser.CommonParse import BytesProcessOutsideException
from RecordParser.MsgInfoAcquire import ErrorEscapeException

'''
    该脚本用于验证按照车组号创建多个数据库，不同于Part4固定创建
    注意：这里基本明确的数据库的创建基于NID_ENGINE的 “ 车组号+端号 ”，涉及到ATP-ATO的SP5包解析
'''

#  简单测试代码后期删除
msg_info = MsgProcess("7EC9175800000560000262F2E71020A1DCD6500000010104AD6000000000000000000000000000000010256B2ABFFFFFFFFFFFFFFFC0000000000000022B4580000000000000000001540002AAAA015400000000000000000000000000007F")
msg_info.msg_head_process()  # 解析出消息头(先反转义再解析)
# 选择相应的数据表
atp_pkt_dic = msg_info.get_atp_ato_dic_from_msg_pkt()
#


def create_database_by_nid_engine(log_path=str):
    """
    :param log: 文件路径字符串
    :return: 不返回任何，根据NID_ENGINE创建数据库
    """
    with open(log_path, mode='r', errors='ignore') as f:
        for line in f:
            try:
                l_stream = line.split()[0]
                msg_info = MsgProcess(l_stream)
                msg_info.msg_head_process()      # 解析出消息头(先反转义再解析)
                # 选择相应的数据表
                atp_pkt_dic = msg_info.get_atp_ato_dic_from_msg_pkt()
                if atp_pkt_dic.keys():
                    print(atp_pkt_dic)

            # 捕获转义异常
            except ErrorEscapeException as err:
                print(err)
            # 捕获字节流解析异常
            except BytesProcessOutsideException as err:
                print(err)
            # 捕获索引异常
            except IndexError as err:
                print(err)
                print('line: '+line)


# Create the database and table
data_base2 = sqlite3.connect('CR400BF_5113_01_record_base')
cursor2 = data_base2.cursor()

data_base = sqlite3.connect('CR400BF_5113_08_record_base')
cursor = data_base.cursor()


# 根据日志时间创建表
def create_table_in_month(cr, db, tbl_name):
    cr.execute('CREATE TABLE IF NOT EXISTS "%s" ('
                   'T_ATOUTC int,'         # UTC日历时间
                   'N_CYCLE int,'
                   'NID_MODLE int,'
                   'Q_HOT_STANDBY int,'
                   'T_ATO int,'
                   'M_POS int,'
                   'V_SPEED int,'
                   'M_ATOMODE int,'
                   'L_MESSAGE int,'
                   'MSG_CONTENT text,'
                   'PRIMARY KEY (T_ATOUTC, N_CYCLE, Q_HOT_STANDBY)'  # 考虑时间、周期、主备系作为主键
                   ')' % tbl_name)  # 占位符写在字符串中，最后再写变量

    db.commit()


# 获取当前路径下所有记录的纪录路径
def get_all_log_files(file_list=list, root_path=str):
    files = os.listdir(root_path)
    for fileName in files:

        full_path = path.join(root_path, fileName)
        if path.isdir(full_path):
            get_all_log_files(file_list, full_path)
        else:
            if '.txt' in full_path:
                file_list.append(full_path)
                print(full_path)
            else:
                pass
    return file_list


# 根据UTC时间获得表名，格式201905到月份
def get_tbl_name_by_utctime(utc_time=int):
    log_time = time.localtime(utc_time)
    if log_time.tm_mon < 10:
        return str(log_time.tm_year)+'0' + str(log_time.tm_mon)
    else:
        return str(log_time.tm_year) + str(log_time.tm_mon)


# 将指定路径下信息按照日期分类写入数据库
def insert_record_in_date(log_path=str):
    with open(log_path, mode='r', errors='ignore') as f:
        for line in f:
            try:
                l_stream = line.split()[0]
                msg_info = MsgProcess(l_stream)
                msg_info.msg_head_process()      # 解析出消息头(先反转义再解析)
                # 选择相应的数据表
                tbl_name = get_tbl_name_by_utctime(msg_info.t_atoutc)
                # 数据库插入变量按照 execute('INSERT INTO table_name('%d','%s')'%(var1,var2)) 字符串后结束语句再跟命令
                cursor.execute('INSERT OR IGNORE INTO "%s" VALUES  ("%d", "%d", "%d", "%d", "%d", "%d", "%d",'
                               ' "%d", "%d", "%s")' % (tbl_name, msg_info.t_atoutc, msg_info.n_cycle,
                                                       msg_info.nid_modle,msg_info.q_standby, msg_info.t_ato,
                                                       msg_info.m_pos, msg_info.v_speed, msg_info.m_atomode,
                                                       msg_info.l_message, msg_info.msg_content))
            # 捕获转义异常
            except ErrorEscapeException as err:
                print(err)
            # 捕获字节流解析异常
            except BytesProcessOutsideException as err:
                print(err)
            # 捕获索引异常
            except IndexError as err:
                print(err)
                print('line: '+line)

        data_base.commit()


# 创建存储表
for dt in ['201901', '201902', '201903', '201904', '201905', '201905',
           '201906', '201907', '201910', '201911', '201912']:
    create_table_in_month(cursor2, data_base2, dt)
    create_table_in_month(cursor, data_base, dt)


# 初始化路径
rootPath = os.getcwd()
print(rootPath)
fileArray = []


# 获取路径下所有记录并写入数据库
fileArray = get_all_log_files(fileArray, rootPath)
for f in fileArray:
    create_database_by_nid_engine(f)
    insert_record_in_date(f)
