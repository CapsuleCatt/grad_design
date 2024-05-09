import pandas as pd
import pymysql



def update_data_process():
    connection = pymysql.connect(
    host="121.4.116.90",
    port=3306,
    user="root",
    password="@Cyy4510471",
    database="hopital_system",
    )
    cursor = connection.cursor()

    cursor.execute("select * from patient_info")
    result = cursor.fetchall()
    columns = [field[0] for field in cursor.description]
    patient_info = pd.DataFrame(columns=columns, data=result)
    # connection.close()
    cursor.execute("select * from operation_form")
    result = cursor.fetchall()
    columns = [field[0] for field in cursor.description]
    operation_form = pd.DataFrame(columns=columns, data=result)

    x_data = pd.DataFrame()
    # 把patient_info中的分类变量转换为数值变量
    x_data['性别'] = patient_info['性别'].apply(lambda x: 1 if x == '男' else 0)
    # 计算一共有多少种诊断代码，然后转换为数值变量
    # len(set(patient_info['诊断代码']))
    x_data['诊断代码'] = pd.Categorical(patient_info['诊断代码'])
    x_data['诊断代码'] = x_data['诊断代码'].cat.codes
    # 计算一共有几个主刀医生工号，然后转换为数值变量
    # print(len(set(patient_info['主刀医生工号'])))
    x_data['主刀医生工号'] = pd.Categorical(patient_info['主刀医生工号'])
    x_data['主刀医生工号'] = x_data['主刀医生工号'].cat.codes
    # 把过敏史转换为数值变量
    x_data['过敏史'] = patient_info['过敏史'].apply(lambda x: 1 if x == '有' else 0)
    # 把心律转换为数值变量
    x_data['心律'] = patient_info['心律'].apply(lambda x: 1 if x == '不齐' else 0)
    # 把手术等级转换为数值变量
    x_data['sq手术等级'] = pd.Categorical(patient_info['sq手术等级'])
    x_data['sq手术等级'] = x_data['sq手术等级'].cat.codes
    # 把sq麻醉方式转换为数值变量
    x_data['sq麻醉方式'] = pd.Categorical(patient_info['sq麻醉方式'])
    x_data['sq麻醉方式'] = x_data['sq麻醉方式'].cat.codes
    # 把sq手术部位转换为数值变量
    x_data['sq手术部位'] = pd.Categorical(patient_info['sq手术部位'])
    x_data['sq手术部位'] = x_data['sq手术部位'].cat.codes
    # 把operation_form中的分类变量转换为数值变量
    x_data['operation_num'] = pd.Categorical(operation_form['operation_num'])
    x_data['operation_num'] = x_data['operation_num'].cat.codes
    # 把CT转换为数值变量
    x_data['CT'] = operation_form['CT']
    x_data['operation_room_num'] = operation_form['operation_room_num']
    x_data['SYXH'] = operation_form['SYXH']
    #y
    y_data = pd.DataFrame()
    cursor.execute("select bracelet_data.SYXH, bracelet_data.`sCT开始的时间`, bracelet_data.`sCT结束的时间`, bracelet_data.`sCT等候时间（分）`,bracelet_data.`s进入手术室时间`, bracelet_data.`s出外科手术室时间`, bracelet_data.`s进手术机房时间`, bracelet_data.`s出手术机房时间`,bracelet_data.`s进出手术机房时长（分）`, bracelet_data.`s进出手术室时长（分）`, bracelet_data.`s入苏醒室的时间` ,bracelet_data.`s出苏醒室的时间` from bracelet_data")
    result = cursor.fetchall()
    columns = [field[0] for field in cursor.description]
    bracelet_data = pd.DataFrame(columns=columns, data=result)
    # 计算进出苏醒室的时长
    bracelet_data['s进出苏醒室时长（分）'] = bracelet_data['s出苏醒室的时间'] - bracelet_data['s入苏醒室的时间']
    # 转换为分钟
    bracelet_data['s进出苏醒室时长（分）'] = bracelet_data['s进出苏醒室时长（分）'].apply(lambda x: x.total_seconds() / 60)
    bracelet_data['进出CT室时长（分）'] = bracelet_data['sCT结束的时间'] - bracelet_data['sCT开始的时间']
    bracelet_data['进出CT室时长（分）'] = bracelet_data['进出CT室时长（分）'].apply(lambda x: x.total_seconds() / 60)
    bracelet_data['进出手术机房时长（分）'] = bracelet_data['s出手术机房时间'] - bracelet_data['s进手术机房时间']
    bracelet_data['进出手术机房时长（分）'] = bracelet_data['进出手术机房时长（分）'].apply(lambda x: x.total_seconds() / 60)
    bracelet_data['进出手术室时长（分）'] = bracelet_data['s出外科手术室时间'] - bracelet_data['s进入手术室时间']
    bracelet_data['进出手术室时长（分）'] = bracelet_data['进出手术室时长（分）'].apply(lambda x: x.total_seconds() / 60)
    y_data = bracelet_data[['SYXH','进出CT室时长（分）', '进出手术机房时长（分）', '进出手术室时长（分）', 's进出苏醒室时长（分）']]
    # merge x_data and y_data
    data = pd.merge(x_data, y_data, on='SYXH', how='inner')
    # 去掉苏醒室时长为空的数据
    data = data.dropna(subset=['s进出苏醒室时长（分）'])
    # 去除异常值
    # data = data[data['进出CT室时长（分）'] > 0]
    # data = data[data['进出手术机房时长（分）'] > 0]
    # data = data[data['进出手术室时长（分）'] > 0]
    # data = data[data['s进出苏醒室时长（分）'] > 0]
    # data = data[data['进出CT室时长（分）'] < 300]
    # data = data[data['进出手术机房时长（分）'] < 300]
    # data = data[data['进出手术室时长（分）'] < 300]
    # data = data[data['s进出苏醒室时长（分）'] < 300]
    cursor.close()
    connection.close()
    return data


def get_data_for_ct(data):
    """
    获取用于预测CT室的数据
    """
    data_ct = data[data['CT'] != 0]
    y_ct = data_ct['进出CT室时长（分）']
    y_ct = y_ct.astype(float)
    x_data_ct = data_ct.drop(['SYXH', '进出CT室时长（分）'], axis=1)
    x_data_ct[['性别', '过敏史', '心律', '诊断代码', '主刀医生工号', 'sq手术等级', 'sq麻醉方式', 'sq手术部位', 'operation_num', 'CT', 'operation_room_num']]= x_data_ct[['性别', '过敏史', '心律', '诊断代码', '主刀医生工号', 'sq手术等级', 'sq麻醉方式', 'sq手术部位', 'operation_num', 'CT', 'operation_room_num']].astype(str)
    x_data_ct[['进出手术机房时长（分）', '进出手术室时长（分）', 's进出苏醒室时长（分）']] = x_data_ct[['进出手术机房时长（分）', '进出手术室时长（分）', 's进出苏醒室时长（分）']].astype(float)
    x_data_ct_dummies = pd.get_dummies(x_data_ct)
    return x_data_ct_dummies, y_ct


def get_data_for_not_ct(data):
    """
    获取用于预测非CT室的数据
    """
    # y_ct = data['进出CT室时长（分）']
    # print(1)
    # print(data)
    y_operation_room = data['进出手术机房时长（分）']
    y_operation = data['进出手术室时长（分）']
    y_recovery = data['s进出苏醒室时长（分）']
    y_operation_room = y_operation_room.astype(float)
    y_operation = y_operation.astype(float)
    y_recovery = y_recovery.astype(float)
    x_data = data
    x_data.index = data['SYXH'] 
    x_data[['性别', '过敏史', '心律', '诊断代码', '主刀医生工号', 'sq手术等级', 'sq麻醉方式', 'sq手术部位', 'operation_num', 'CT', 'operation_room_num']]= x_data[['性别', '过敏史', '心律', '诊断代码', '主刀医生工号', 'sq手术等级', 'sq麻醉方式', 'sq手术部位', 'operation_num', 'CT', 'operation_room_num']].astype(str)
    x_data[['进出手术机房时长（分）', '进出手术室时长（分）', 's进出苏醒室时长（分）']] = x_data[['进出手术机房时长（分）', '进出手术室时长（分）', 's进出苏醒室时长（分）']].astype(float)
    x_data_operation_room = x_data.drop(['进出手术机房时长（分）'], axis=1)
    x_data_operation = x_data.drop(['进出手术室时长（分）'], axis=1)
    x_data_recovery = x_data.drop(['s进出苏醒室时长（分）'], axis=1)
    print(x_data_operation)
    x_data_operation_room_dummies = pd.get_dummies(x_data_operation_room)
    x_data_operation_dummies = pd.get_dummies(x_data_operation)
    x_data_recovery_dummies = pd.get_dummies(x_data_recovery)
    print(x_data_operation_room_dummies.columns)
    return x_data_operation_room_dummies, y_operation_room, x_data_operation_dummies, y_operation, x_data_recovery_dummies, y_recovery


def save_to_database(data):
    connection = pymysql.connect(
    host="121.4.116.90",
    port=3306,
    user="root",
    password="@Cyy4510471",
    database="hopital_system",
    )
    cursor = connection.cursor()
    # 存入training_data_set表格
    cursor.execute("truncate table training_data_set_ct")
    cursor.execute("truncate table training_data_set_not_ct")
    connection.commit()
    # data存入数据库
    try:
        data_copy = data.copy()
        data_ct = data[data['CT'] == 1]
        data_not_ct = data_copy.drop(['进出CT室时长（分）'], axis=1)
        # df = pd.read_csv('data_all.csv')
        # df.to_sql('training_data_set', connection, if_exists='append', index=False)
        for i in range(data_ct.shape[0]):
            # 假如插入的数据中有空值，插入空值None
            cursor.execute("insert into training_data_set_ct values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", tuple(data_ct.iloc[i, :]))
                
            connection.commit()
        for j in range(data_not_ct.shape[0]):
            # 假如插入的数据中有空值，插入空值None
            cursor.execute("insert into training_data_set_not_ct values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", tuple(data_not_ct.iloc[j, :]))
            connection.commit()
        return '数据存入成功'
    except:
        return '数据存入失败'
    


def get_data_from_database():
    connection = pymysql.connect(
    host="121.4.116.90",
    port=3306,
    user="root",
    password="@Cyy4510471",
    database="hopital_system",
    )
    cursor = connection.cursor()
    cursor.execute("select * from training_data_set_ct")
    result_ct = cursor.fetchall()
    columns = [field[0] for field in cursor.description]
    data_ct = pd.DataFrame(columns=columns, data=result_ct)
    cursor.execute("select * from training_data_set_not_ct")
    result_not_ct = cursor.fetchall()
    columns = [field[0] for field in cursor.description]
    data_not_ct = pd.DataFrame(columns=columns, data=result_not_ct)
    cursor.close()
    connection.close()
    return data_ct, data_not_ct

