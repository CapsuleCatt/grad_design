import pymysql
import pandas as pd
import json
import re
from datetime import datetime as dt
import datetime

connection = pymysql.connect(
    host="121.4.116.90",
    port=3306,
    user="root",
    password="@Cyy4510471",
    database="hopital_system",
)


def execute_mysql(mysql_sql):
    """
    执行sql语句
    :param mysql_sql: MySQL语句
    :return: 执行之后的返回值
    """
    try:
        # 创建一个游标对象
        cursor = connection.cursor()
        # 执行SQL语句
        cursor.execute(mysql_sql)
        # 获取查询结果
        mysql_results = cursor.fetchall()
        # 提交事务并关闭连接
        connection.commit()
        return mysql_results

    except Exception as e:
        return str(e)


def json_serial(obj):
    """
    把JSON的时间格式序列化变成自定义格式
    """
    if isinstance(obj, dt):
        date_str = obj.strftime("%Y-%m-%d")  # 自定义日期格式
        time_str = obj.strftime("%H:%M:%S")  # 自定义时间格式
        return f"{date_str} {time_str}"
    raise TypeError("Type not serializable")


def inquire_mysql(sql_query, output_format="json"):
    """
    查询数据库 执行数据库语句注意只能满足以下的格式
    FROM+表名+WHERE/GROUP/LIMIT/TOP 代码自动识别表名，否则可能会报错
    :param sql_query: 数据库执行语句
    :param output_format: json 或者 DataFrame 或者 "tuple"（直接输出） ,默认是json
    :return: 查询数据库内容
    """
    # try:
    #     # 执行sql语句获得内容
    #     table_results = execute_mysql(sql_query)
    try:
        # 创建游标对象
        with connection.cursor() as cursor:
            # 执行SQL查询
            cursor.execute(sql_query)
            
            # 获取表头
            columns = [field[0] for field in cursor.description]
            # 获取查询结果
            table_results = cursor.fetchall()
            connection.commit()
    except Exception as e:
        return str(e)
        # 通过sql语句获得表名
        # match = re.search(
        #     r"FROM (.*?)(?: WHERE| GROUP| LIMIT| TOP|$)", sql_query, re.IGNORECASE
        # )
        # table_name = match.group(1)
        # 通过表名获取sql的表头 方便输出格式
        # columns_query = execute_mysql(f"DESCRIBE {table_name}")
        # columns = [column[0] for column in columns_query]
        # print(columns)
        # 输出格式的选择
    if output_format == "DataFrame":
        # 获取查询结果并将其转换为 DataFrame
        df = pd.DataFrame(table_results, columns=columns)
        return df
    elif output_format == "json":
        # 获取查询结果并将其转换为JSON
        json_result = [dict(zip(columns, row)) for row in table_results]
        return json.dumps(json_result, ensure_ascii=False, default=json_serial)

    elif output_format == "tuple":
        # 获取查询结果直接输出
        return table_results
    else:
        connection.close()
        return '切换请输入 "json" 或者 "DataFrame" 或者 "tuple"（直接输出） ,默认是json'

