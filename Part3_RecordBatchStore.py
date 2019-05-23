import sqlite3
from RecordParser.MsgAcquire import MsgProcess
from RecordParser.CommonParse import BytesProcessOutsideException
from RecordParser.MsgAcquire import ErrorEscapeException

class MsgParseHeadException(Exception):
    """This Exception is use for msg head parse"""
    def __init__(self, error='Record msg parse err!'):
        super(__class__, self).__init__(error)


# Create the database and table
data_base = sqlite3.connect('c3ato_record_base')
cursor = data_base.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS record_table('
               'T_ATOUTC int,'         # UTC日历时间
               'N_CYCLE int,'
               'NID_MODLE int,'
               'Q_HOT_STANDBY int,'
               'T_ATO int,'
               'M_POS int,'
               'V_SPEED int,'
               'M_ATOMODE int,'
               'L_MESSAGE int,'
               'MSG_CONTENT text'
               ')')

data_base.commit()

# 清空数据表
cursor.execute('DELETE FROM record_table ')
data_base.commit()

with open('DataFiles\L_can_log.txt', mode='r', errors='ignore') as f:
    for line in f:
        try:
            l_stream = line.split()[0]
            msg_info = MsgProcess(l_stream)
            msg_info.msg_head_process()
            # 数据库插入变量按照 execute('INSERT INTO table_name('%d','%s')'%(var1,var2)) 字符串后结束语句再跟命令
            cursor.execute('INSERT INTO record_table VALUES  ("%d", "%d", "%d", "%d", "%d", "%d", "%d",'
                           ' "%d", "%d", "%s")'%(msg_info.t_atoutc, msg_info.n_cycle, msg_info.nid_modle,
                                                 msg_info.q_standby, msg_info.t_ato, msg_info.m_pos,
                                                 msg_info.v_speed,msg_info.m_atomode, msg_info.l_message,
                                                 msg_info.msg_content))
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
