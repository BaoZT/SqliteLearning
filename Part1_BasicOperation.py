import sqlite3
data_base = sqlite3.connect('data_base_name')
cursor = data_base.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS table_name(name text,age int,info text)')
data_base.commit()

# # 数据增加
# cursor.execute('INSERT INTO table_name VALUES ("python",29,"最好的语言")')
# cursor.execute('INSERT INTO table_name VALUES ("java",27,"最好用的语言")')
# cursor.execute('INSERT INTO table_name VALUES ("C++",39,"最基础的语言")')
# cursor.execute('INSERT INTO table_name VALUES ("php",24,"最时尚的语言")')
# data_base.commit()
#
# # 数据修改
# cursor.execute('UPDATE table_name SET name="C++",age=33 WHERE name="python"')
# cursor.execute('UPDATE table_name SET name="C++",age=33 WHERE age=29')
# data_base.commit()
#
# # 根据条件删除
cursor.execute('DELETE FROM table_name WHERE name="C"')
data_base.commit()


cursor.execute('SELECT * FROM table_name')
result = cursor.fetchall()
print(result)

cursor.execute('SELECT * FROM table_name WHERE age=39')
result = cursor.fetchall()
print(result)

cursor.execute('SELECT * FROM table_name WHERE name LIKE "C%"')
result = cursor.fetchall()
print(result)

cursor.execute('SELECT * FROM table_name WHERE name LIKE "%h%"')
result = cursor.fetchall()
print(result)