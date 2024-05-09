import streamlit as st
from streamlit_option_menu import option_menu
from sql_data_base import inquire_mysql ,execute_mysql
import pandas as pd
from pyecharts.charts import Funnel ,Bar ,Radar ,Line
from pyecharts import options as opts
import re
from datetime import date
import numpy as np

def pychart_show():
    if st.session_state [ 'user_info' ]['username'] == "admin":
        st.title('手术室流程时长预测')
        # 分割线
        st.markdown('***')
        sql_ope_room = "SELECT operation_room_num, operation_room_name FROM ope_room;"
        ope_room_info = inquire_mysql(sql_ope_room, output_format='DataFrame')
        # print(ope_room_info)
        options = ope_room_info['operation_room_name'].tolist()
        options = sorted(options,key = lambda i:int(re.match(r'(\d+)',i).group()))
        selected_option = st.selectbox("手术室", options)
        # date_show = date.strftime("%Y-%m-%d")
        # st.write('当前日期：',date_show)
        sql_all_ope_date = "SELECT operation_date FROM anesthesia_form;"
        ope_date_all = inquire_mysql(sql_all_ope_date, output_format='DataFrame')
        ope_date_list_all = list(set(ope_date_all['operation_date'].to_list()))
        options_date = sorted(ope_date_list_all,key = lambda i:i.date())
        options_date = [i.strftime("%Y-%m-%d") for i in options_date]
        selected_date = st.selectbox("当前日期", options_date)
        sql_operation = f"SELECT operation_name, doctor_num, operation_form.SYXH FROM operation_form, anesthesia_form WHERE anesthesia_form.operation_date='{selected_date}' AND anesthesia_form.SYXH=operation_form.SYXH AND operation_room_name='{selected_option}';"
        operation_info = inquire_mysql(sql_operation, output_format='DataFrame')
        for i in range(len(operation_info)):
            # 把dataframe每一行加起来成一个字符串作为选项
            operation_info.iloc[i] = operation_info.iloc[i].apply(str)
            # 第一项是手术名称，第二项是医生工号，第三项是患者SYXH
            operation_info_operation = operation_info.iloc[i][0]
            operation_info_doctor_num = operation_info.iloc[i][1]
            operation_info_SYXH = operation_info.iloc[i][2]
            # 选项是手术名称+医生工号+患者SYXH
            operation_info.iloc[i] = '手术名: '+operation_info_operation + ' | 医生工号: ' + operation_info_doctor_num + ' | 患者SYXH: ' + operation_info_SYXH
        selected_operation = st.selectbox("手术", operation_info['operation_name'].tolist())
        selected_operation_row = operation_info[operation_info['operation_name'] == selected_operation]
        selected_operation_row = selected_operation_row.iloc[0]
        # if st.button('查询'):
        #     # 查询当前患者信息
        #     # 取选项SYXH: 后面的SYXH
        selected_operation_row_SYXH = selected_operation_row['operation_name'].split('SYXH: ')[1]
        sql_patient = f"SELECT * FROM patient_info WHERE SYXH='{selected_operation_row_SYXH}';"
        patient_info = inquire_mysql(sql_patient, output_format='DataFrame')
        with st.container():
            st.write('患者信息')
            st.write('住院号:', patient_info['SYXH'].iloc[0])
            st.write('性别:', patient_info['性别'].iloc[0])
            st.write('诊断:', patient_info['诊断名称'].iloc[0])
            st.write('过敏史:', patient_info['过敏史'].iloc[0])
            st.write('心律:', patient_info['心律'].iloc[0])
            st.write('心脏不适:', patient_info['心脏不适'].iloc[0])
            # st.write('既往史:', patient_info['既往史'].iloc[0])
        # 获取预测结果
        # 分为四栏
        st.markdown('***')
        col1, col2, col3 = st.columns(3)
        with col1:
            # print(1)
            sql_predict_ct = f"SELECT * FROM y_pred_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            predict_ct = inquire_mysql(sql_predict_ct, output_format='DataFrame')
            if predict_ct.empty:
                st.write('CT室时长预测结果: ')
                st.write('当前患者没有被安排CT检查')
            else:
                st.write('CT室时长预测结果: ')
                sql_predict_ct = f"SELECT * FROM y_pred_ct WHERE SYXH='{selected_operation_row_SYXH}';"
                predict_ct = inquire_mysql(sql_predict_ct, output_format='DataFrame')
                st.write('预测平均值:', predict_ct['0.5'].iloc[0], '分钟')
                predict_ct = predict_ct.iloc[0].drop(['SYXH'])
                predict_ct.rename(index={'0.25': '25%', '0.5': '50%', '0.75': '75%'}, inplace=True)
                st.write('不同分位数的预测值: ')
                # 画图，画出不同分位数的预测值，横轴是25%,50%,75%，纵轴是预测值
                st.bar_chart(predict_ct, use_container_width=True)
        with col2:
            st.write('手术室时长预测结果: ')
            sql_predict_op_room = f"SELECT * FROM y_pred_operation_room WHERE SYXH='{selected_operation_row_SYXH}';"
            predict_op_room = inquire_mysql(sql_predict_op_room, output_format='DataFrame')
            st.write('预测平均值:', predict_op_room['0.5'].iloc[0], '分钟')
            # sql_real_op_room = f"SELECT `s进出手术机房时长（分）` FROM training_data_set_not_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            # real_op_room = inquire_mysql(sql_real_op_room, output_format='DataFrame')
            # st.write('实际值:', real_op_room['s进出手术机房时长（分）'].iloc[0], '分钟')
            predict_op_room = predict_op_room.iloc[0].drop(['SYXH'])
            predict_op_room.rename(index={'0.25': '25%', '0.5': '50%', '0.75': '75%'}, inplace=True)
            # predict_op = pd.DataFrame(predict_op, columns=['25%', '50%', '75%'])
            st.write('不同分位数的预测值: ')
            # 画图，画出不同分位数的预测值，横轴是25%,50%,75%，纵轴是预测值
            st.bar_chart(predict_op_room, use_container_width=True)


        with col3:
            sql_predict_recovery = f"SELECT * FROM y_pred_recovery WHERE SYXH='{selected_operation_row_SYXH}';"
            predict_re = inquire_mysql(sql_predict_recovery, output_format='DataFrame')
            st.write('苏醒室时长预测结果: ')
            st.write('预测平均值:', predict_re['0.5'].iloc[0], '分钟')
            # sql_real_recovery = f"SELECT `s进出苏醒室时长（分）` FROM training_data_set_not_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            # print(sql_real_recovery)
            # real_recovery = inquire_mysql(sql_real_recovery, output_format='DataFrame')
            # st.write('实际值:', real_reco very['s进出苏醒室时长（分）'].iloc[0], '分钟')
            predict_re = predict_re.iloc[0].drop(['SYXH'])
            predict_re.rename(index={'0.25': '25%', '0.5': '50%', '0.75': '75%'}, inplace=True)
            st.write('不同分位数的预测值: ')
            # 画图，画出不同分位数的预测值，横轴是25%,50%,75%，纵轴是预测值
            st.bar_chart(predict_re, use_container_width=True)
        st.markdown('***')
        sql_predict_operation = f"SELECT * FROM y_pred_operation WHERE SYXH='{selected_operation_row_SYXH}';"
        predict_op = inquire_mysql(sql_predict_operation, output_format='DataFrame')
        st.write('手术全程时长预测结果: ')
        st.write('预测平均值:', predict_op['0.5'].iloc[0], '分钟')
        predict_op = predict_op.iloc[0].drop(['SYXH'])
        predict_op.rename(index={'0.25': '25%', '0.5': '50%', '0.75': '75%'}, inplace=True)
        st.write('不同分位数的预测值: ')
        # 画图，画出不同分位数的预测值，横轴是25%,50%,75%，纵轴是预测值
        st.bar_chart(predict_op, use_container_width=True)
    elif st.session_state [ 'user_info' ]['username'] == "ct_room":
        st.title('手术室流程时长预测')
        # 分割线
        st.markdown('***')
        sql_ope_room = "SELECT operation_room_num, operation_room_name FROM ope_room;"
        ope_room_info = inquire_mysql(sql_ope_room, output_format='DataFrame')
        # print(ope_room_info)
        options = ope_room_info['operation_room_name'].tolist()
        options = sorted(options,key = lambda i:int(re.match(r'(\d+)',i).group()))
        selected_option = st.selectbox("手术室", options)
        # date_show = date.strftime("%Y-%m-%d")
        # st.write('当前日期：',date_show)
        sql_all_ope_date = "SELECT operation_date FROM anesthesia_form;"
        ope_date_all = inquire_mysql(sql_all_ope_date, output_format='DataFrame')
        ope_date_list_all = list(set(ope_date_all['operation_date'].to_list()))
        options_date = sorted(ope_date_list_all,key = lambda i:i.date())
        options_date = [i.strftime("%Y-%m-%d") for i in options_date]
        selected_date = st.selectbox("当前日期", options_date)
        sql_operation = f"SELECT operation_name, doctor_num, operation_form.SYXH FROM operation_form, anesthesia_form WHERE anesthesia_form.operation_date='{selected_date}' AND anesthesia_form.SYXH=operation_form.SYXH AND operation_room_name='{selected_option}';"
        operation_info = inquire_mysql(sql_operation, output_format='DataFrame')
        for i in range(len(operation_info)):
            # 把dataframe每一行加起来成一个字符串作为选项
            operation_info.iloc[i] = operation_info.iloc[i].apply(str)
            # 第一项是手术名称，第二项是医生工号，第三项是患者SYXH
            operation_info_operation = operation_info.iloc[i][0]
            operation_info_doctor_num = operation_info.iloc[i][1]
            operation_info_SYXH = operation_info.iloc[i][2]
            # 选项是手术名称+医生工号+患者SYXH
            operation_info.iloc[i] = '手术名: '+operation_info_operation + ' | 医生工号: ' + operation_info_doctor_num + ' | 患者SYXH: ' + operation_info_SYXH
        selected_operation = st.selectbox("手术", operation_info['operation_name'].tolist())
        selected_operation_row = operation_info[operation_info['operation_name'] == selected_operation]
        selected_operation_row = selected_operation_row.iloc[0]
        # if st.button('查询'):
        #     # 查询当前患者信息
        #     # 取选项SYXH: 后面的SYXH
        selected_operation_row_SYXH = selected_operation_row['operation_name'].split('SYXH: ')[1]
        sql_patient = f"SELECT * FROM patient_info WHERE SYXH='{selected_operation_row_SYXH}';"
        patient_info = inquire_mysql(sql_patient, output_format='DataFrame')
        with st.container():
            st.write('患者信息')
            st.write('住院号:', patient_info['SYXH'].iloc[0])
            st.write('性别:', patient_info['性别'].iloc[0])
            st.write('诊断:', patient_info['诊断名称'].iloc[0])
            st.write('过敏史:', patient_info['过敏史'].iloc[0])
            st.write('心律:', patient_info['心律'].iloc[0])
            st.write('心脏不适:', patient_info['心脏不适'].iloc[0])
            # st.write('既往史:', patient_info['既往史'].iloc[0])
        # 获取预测结果
        # 分为四栏
        st.markdown('***')
        col1, col2, col3 = st.columns(3)
        with col1:
            # print(1)
            sql_predict_ct = f"SELECT * FROM y_pred_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            predict_ct = inquire_mysql(sql_predict_ct, output_format='DataFrame')
            if predict_ct.empty:
                st.write('CT室时长预测结果: ')
                st.write('当前患者没有被安排CT检查')
            else:
                st.write('CT室时长预测结果: ')
                sql_predict_ct = f"SELECT * FROM y_pred_ct WHERE SYXH='{selected_operation_row_SYXH}';"
                predict_ct = inquire_mysql(sql_predict_ct, output_format='DataFrame')
                st.write('预测平均值:', predict_ct['0.5'].iloc[0], '分钟')
                predict_ct = predict_ct.iloc[0].drop(['SYXH'])
                predict_ct.rename(index={'0.25': '25%', '0.5': '50%', '0.75': '75%'}, inplace=True)
                st.write('不同分位数的预测值: ')
                # 画图，画出不同分位数的预测值，横轴是25%,50%,75%，纵轴是预测值
                st.bar_chart(predict_ct, use_container_width=True)
        with col2:
            pass


        with col3:
            pass
        st.markdown('***')
        sql_predict_operation = f"SELECT * FROM y_pred_operation WHERE SYXH='{selected_operation_row_SYXH}';"
        predict_op = inquire_mysql(sql_predict_operation, output_format='DataFrame')
        st.write('手术全程时长预测结果: ')
        st.write('预测平均值:', predict_op['0.5'].iloc[0], '分钟')
        predict_op = predict_op.iloc[0].drop(['SYXH'])
        predict_op.rename(index={'0.25': '25%', '0.5': '50%', '0.75': '75%'}, inplace=True)
        st.write('不同分位数的预测值: ')
        # 画图，画出不同分位数的预测值，横轴是25%,50%,75%，纵轴是预测值
        st.bar_chart(predict_op, use_container_width=True)
    elif st.session_state [ 'user_info' ]['username'] == "ope_room":
        st.title('手术室流程时长预测')
        # 分割线
        st.markdown('***')
        sql_ope_room = "SELECT operation_room_num, operation_room_name FROM ope_room;"
        ope_room_info = inquire_mysql(sql_ope_room, output_format='DataFrame')
        # print(ope_room_info)
        options = ope_room_info['operation_room_name'].tolist()
        options = sorted(options,key = lambda i:int(re.match(r'(\d+)',i).group()))
        selected_option = st.selectbox("手术室", options)
        # date_show = date.strftime("%Y-%m-%d")
        # st.write('当前日期：',date_show)
        sql_all_ope_date = "SELECT operation_date FROM anesthesia_form;"
        ope_date_all = inquire_mysql(sql_all_ope_date, output_format='DataFrame')
        ope_date_list_all = list(set(ope_date_all['operation_date'].to_list()))
        options_date = sorted(ope_date_list_all,key = lambda i:i.date())
        options_date = [i.strftime("%Y-%m-%d") for i in options_date]
        selected_date = st.selectbox("当前日期", options_date)
        sql_operation = f"SELECT operation_name, doctor_num, operation_form.SYXH FROM operation_form, anesthesia_form WHERE anesthesia_form.operation_date='{selected_date}' AND anesthesia_form.SYXH=operation_form.SYXH AND operation_room_name='{selected_option}';"
        operation_info = inquire_mysql(sql_operation, output_format='DataFrame')
        for i in range(len(operation_info)):
            # 把dataframe每一行加起来成一个字符串作为选项
            operation_info.iloc[i] = operation_info.iloc[i].apply(str)
            # 第一项是手术名称，第二项是医生工号，第三项是患者SYXH
            operation_info_operation = operation_info.iloc[i][0]
            operation_info_doctor_num = operation_info.iloc[i][1]
            operation_info_SYXH = operation_info.iloc[i][2]
            # 选项是手术名称+医生工号+患者SYXH
            operation_info.iloc[i] = '手术名: '+operation_info_operation + ' | 医生工号: ' + operation_info_doctor_num + ' | 患者SYXH: ' + operation_info_SYXH
        selected_operation = st.selectbox("手术", operation_info['operation_name'].tolist())
        selected_operation_row = operation_info[operation_info['operation_name'] == selected_operation]
        selected_operation_row = selected_operation_row.iloc[0]
        # if st.button('查询'):
        #     # 查询当前患者信息
        #     # 取选项SYXH: 后面的SYXH
        selected_operation_row_SYXH = selected_operation_row['operation_name'].split('SYXH: ')[1]
        sql_patient = f"SELECT * FROM patient_info WHERE SYXH='{selected_operation_row_SYXH}';"
        patient_info = inquire_mysql(sql_patient, output_format='DataFrame')
        with st.container():
            st.write('患者信息')
            st.write('住院号:', patient_info['SYXH'].iloc[0])
            st.write('性别:', patient_info['性别'].iloc[0])
            st.write('诊断:', patient_info['诊断名称'].iloc[0])
            st.write('过敏史:', patient_info['过敏史'].iloc[0])
            st.write('心律:', patient_info['心律'].iloc[0])
            st.write('心脏不适:', patient_info['心脏不适'].iloc[0])
            # st.write('既往史:', patient_info['既往史'].iloc[0])
        # 获取预测结果
        # 分为四栏
        st.markdown('***')
        col1, col2, col3 = st.columns(3)
        with col1:
            sql_ct_real = f"SELECT `进出CT室时长（分）` FROM training_data_set_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            print(sql_ct_real)
            real_ct = inquire_mysql(sql_ct_real, output_format='DataFrame')
            if real_ct.empty:
                st.write('CT室实际时长: ')
                st.write('当前患者没有被安排CT检查')
            else:
                st.write('CT室实际时长: ')
                st.write(real_ct['进出CT室时长（分）'].iloc[0], '分钟')
        with col2:
            st.write('手术室时长预测结果: ')
            sql_predict_op_room = f"SELECT * FROM y_pred_operation_room WHERE SYXH='{selected_operation_row_SYXH}';"
            predict_op_room = inquire_mysql(sql_predict_op_room, output_format='DataFrame')
            st.write('预测平均值:', predict_op_room['0.5'].iloc[0], '分钟')
            # sql_real_op_room = f"SELECT `s进出手术机房时长（分）` FROM training_data_set_not_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            # real_op_room = inquire_mysql(sql_real_op_room, output_format='DataFrame')
            # st.write('实际值:', real_op_room['s进出手术机房时长（分）'].iloc[0], '分钟')
            predict_op_room = predict_op_room.iloc[0].drop(['SYXH'])
            predict_op_room.rename(index={'0.25': '25%', '0.5': '50%', '0.75': '75%'}, inplace=True)
            # predict_op = pd.DataFrame(predict_op, columns=['25%', '50%', '75%'])
            st.write('不同分位数的预测值: ')
            # 画图，画出不同分位数的预测值，横轴是25%,50%,75%，纵轴是预测值
            st.bar_chart(predict_op_room, use_container_width=True)


        with col3:
            pass
        st.markdown('***')
        sql_predict_operation = f"SELECT * FROM y_pred_operation WHERE SYXH='{selected_operation_row_SYXH}';"
        predict_op = inquire_mysql(sql_predict_operation, output_format='DataFrame')
        st.write('手术全程时长预测结果: ')
        st.write('预测平均值:', predict_op['0.5'].iloc[0], '分钟')
        predict_op = predict_op.iloc[0].drop(['SYXH'])
        predict_op.rename(index={'0.25': '25%', '0.5': '50%', '0.75': '75%'}, inplace=True)
        st.write('不同分位数的预测值: ')
        # 画图，画出不同分位数的预测值，横轴是25%,50%,75%，纵轴是预测值
        st.bar_chart(predict_op, use_container_width=True)
    elif st.session_state [ 'user_info' ]['username'] == "pacu_room":
        st.title('手术室流程时长预测')
        # 分割线
        st.markdown('***')
        sql_ope_room = "SELECT operation_room_num, operation_room_name FROM ope_room;"
        ope_room_info = inquire_mysql(sql_ope_room, output_format='DataFrame')
        # print(ope_room_info)
        options = ope_room_info['operation_room_name'].tolist()
        options = sorted(options,key = lambda i:int(re.match(r'(\d+)',i).group()))
        selected_option = st.selectbox("手术室", options)
        # date_show = date.strftime("%Y-%m-%d")
        # st.write('当前日期：',date_show)
        sql_all_ope_date = "SELECT operation_date FROM anesthesia_form;"
        ope_date_all = inquire_mysql(sql_all_ope_date, output_format='DataFrame')
        ope_date_list_all = list(set(ope_date_all['operation_date'].to_list()))
        options_date = sorted(ope_date_list_all,key = lambda i:i.date())
        options_date = [i.strftime("%Y-%m-%d") for i in options_date]
        selected_date = st.selectbox("当前日期", options_date)
        sql_operation = f"SELECT operation_name, doctor_num, operation_form.SYXH FROM operation_form, anesthesia_form WHERE anesthesia_form.operation_date='{selected_date}' AND anesthesia_form.SYXH=operation_form.SYXH AND operation_room_name='{selected_option}';"
        operation_info = inquire_mysql(sql_operation, output_format='DataFrame')
        for i in range(len(operation_info)):
            # 把dataframe每一行加起来成一个字符串作为选项
            operation_info.iloc[i] = operation_info.iloc[i].apply(str)
            # 第一项是手术名称，第二项是医生工号，第三项是患者SYXH
            operation_info_operation = operation_info.iloc[i][0]
            operation_info_doctor_num = operation_info.iloc[i][1]
            operation_info_SYXH = operation_info.iloc[i][2]
            # 选项是手术名称+医生工号+患者SYXH
            operation_info.iloc[i] = '手术名: '+operation_info_operation + ' | 医生工号: ' + operation_info_doctor_num + ' | 患者SYXH: ' + operation_info_SYXH
        selected_operation = st.selectbox("手术", operation_info['operation_name'].tolist())
        selected_operation_row = operation_info[operation_info['operation_name'] == selected_operation]
        selected_operation_row = selected_operation_row.iloc[0]
        # if st.button('查询'):
        #     # 查询当前患者信息
        #     # 取选项SYXH: 后面的SYXH
        selected_operation_row_SYXH = selected_operation_row['operation_name'].split('SYXH: ')[1]
        sql_patient = f"SELECT * FROM patient_info WHERE SYXH='{selected_operation_row_SYXH}';"
        patient_info = inquire_mysql(sql_patient, output_format='DataFrame')
        with st.container():
            st.write('患者信息')
            st.write('住院号:', patient_info['SYXH'].iloc[0])
            st.write('性别:', patient_info['性别'].iloc[0])
            st.write('诊断:', patient_info['诊断名称'].iloc[0])
            st.write('过敏史:', patient_info['过敏史'].iloc[0])
            st.write('心律:', patient_info['心律'].iloc[0])
            st.write('心脏不适:', patient_info['心脏不适'].iloc[0])
            # st.write('既往史:', patient_info['既往史'].iloc[0])
        # 获取预测结果
        # 分为四栏
        st.markdown('***')
        col1, col2, col3 = st.columns(3)
        with col1:
            sql_ct_real = f"SELECT `进出CT室时长（分）` FROM training_data_set_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            print(sql_ct_real)
            real_ct = inquire_mysql(sql_ct_real, output_format='DataFrame')
            if real_ct.empty:
                st.write('CT室实际时长: ')
                st.write('当前患者没有被安排CT检查')
            else:
                st.write('CT室实际时长: ')
                st.write(real_ct['进出CT室时长（分）'].iloc[0], '分钟')
        with col2:
            st.write('手术室实际时长: ')
            sql_real_op_room = f"SELECT `进出手术机房时长（分）` FROM training_data_set_not_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            real_op_room = inquire_mysql(sql_real_op_room, output_format='DataFrame')
            st.write(real_op_room['进出手术机房时长（分）'].iloc[0], '分钟')

        with col3:
            sql_predict_recovery = f"SELECT * FROM y_pred_recovery WHERE SYXH='{selected_operation_row_SYXH}';"
            predict_re = inquire_mysql(sql_predict_recovery, output_format='DataFrame')
            st.write('苏醒室时长预测结果: ')
            st.write('预测平均值:', predict_re['0.5'].iloc[0], '分钟')
            # sql_real_recovery = f"SELECT `s进出苏醒室时长（分）` FROM training_data_set_not_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            # print(sql_real_recovery)
            # real_recovery = inquire_mysql(sql_real_recovery, output_format='DataFrame')
            # st.write('实际值:', real_reco very['s进出苏醒室时长（分）'].iloc[0], '分钟')
            predict_re = predict_re.iloc[0].drop(['SYXH'])
            predict_re.rename(index={'0.25': '25%', '0.5': '50%', '0.75': '75%'}, inplace=True)
            st.write('不同分位数的预测值: ')
            # 画图，画出不同分位数的预测值，横轴是25%,50%,75%，纵轴是预测值
            st.bar_chart(predict_re, use_container_width=True)
        st.markdown('***')
        sql_predict_operation = f"SELECT * FROM y_pred_operation WHERE SYXH='{selected_operation_row_SYXH}';"
        predict_op = inquire_mysql(sql_predict_operation, output_format='DataFrame')
        st.write('手术全程时长预测结果: ')
        st.write('预测平均值:', predict_op['0.5'].iloc[0], '分钟')
        predict_op = predict_op.iloc[0].drop(['SYXH'])
        predict_op.rename(index={'0.25': '25%', '0.5': '50%', '0.75': '75%'}, inplace=True)
        st.write('不同分位数的预测值: ')
        # 画图，画出不同分位数的预测值，横轴是25%,50%,75%，纵轴是预测值
        st.bar_chart(predict_op, use_container_width=True)