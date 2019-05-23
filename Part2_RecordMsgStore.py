import sqlite3
data_base = sqlite3.connect('c3ato_record_base')
cursor = data_base.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS msg_table('
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
# 增加数据
cursor.execute('INSERT INTO msg_table VALUES (1558420351, 15649, 2, 1, 1575619, 1005395587, 2222, 2, 148, "7EC9'
               '20980001E8F000C05612E71CDBF1DF68F418422B3200C8198074002408A100200A50500020955BAAA500000000000000'
               '0000AA0000000204AADD50004218AFFFFFFFF817D000000001A02DBFFFFFFFFFFFFFFFFFFFFFFFCEFE20EA0EFE20EA06C'
               '107094B094B7C00002270EFB626C00000000000000000000525C20DCEFE235B007F")')
# 清空数据表
# cursor.execute('DELETE FROM msg_table ')
data_base.commit()
