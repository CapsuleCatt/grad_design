import streamlit as st
from sql_data_base import inquire_mysql,execute_mysql
import datetime
import re
import numpy as np
import pandas as pd
import json




def home(date):

    if st.session_state [ 'user_info' ]['username'] != "admin":
        st.title('主页')
        st.write('本系统基于机器学习算法进行手术室关键时长预测。用于机器学习模型训练的历史数据经过去标识化处理以及匿名化处理。')
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
        selected_date = st.selectbox("日期", options_date)
        # print(selected_option)
        date_sql = date.strftime("%Y-%m-%d %H:%M:%S")
        sql_operation = f"SELECT operation_name, doctor_num, operation_form.SYXH FROM operation_form, anesthesia_form WHERE anesthesia_form.operation_date='{selected_date}' AND anesthesia_form.SYXH=operation_form.SYXH AND operation_room_name='{selected_option}';"
        # print(inquire_mysql(sql_operation, output_format='DataFrame'))
        # print(sql_operation)
        # json to dataframe
        operation_info = inquire_mysql(sql_operation, output_format='DataFrame')
        operation_info = operation_info[['operation_name', 'doctor_num', 'SYXH']]
        operation_info['doctor_num'] = operation_info['doctor_num'].astype(str)
        if operation_info.empty:
            st.write('当前手术室无手术')
            return
        else:
            operation_info.columns = ['手术名称', '主刀医师', '病人识别号']
            # set form width
            st.markdown('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
            st.markdown('<style>div.Widget.row-widget.stRadio > div > label{padding:10px 20px;}</style>', unsafe_allow_html=True)
            # print(operation_info)
            
            # print(ope_date_list_all)
            st.write(operation_info)
    else:
        # date = get_date()
        st.title('主页')
        st.write('本系统基于机器学习算法进行手术室关键时长预测。用于机器学习模型训练的历史数据经过去标识化处理以及匿名化处理。')
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
        selected_date = st.selectbox("日期", options_date)
        # print(selected_option)
        date_sql = date.strftime("%Y-%m-%d %H:%M:%S")
        sql_operation = f"SELECT operation_name, doctor_num, operation_form.SYXH FROM operation_form, anesthesia_form WHERE anesthesia_form.operation_date='{selected_date}' AND anesthesia_form.SYXH=operation_form.SYXH AND operation_room_name='{selected_option}';"
        # print(inquire_mysql(sql_operation, output_format='DataFrame'))
        # print(sql_operation)
        # json to dataframe
        operation_info = inquire_mysql(sql_operation, output_format='DataFrame')
        operation_info = operation_info[['operation_name', 'doctor_num', 'SYXH']]
        operation_info['doctor_num'] = operation_info['doctor_num'].astype(str)
        col1, col2= st.columns([3,2])
        with col1:
            if operation_info.empty:
                st.write('当前手术室无手术')
                return
            else:
                operation_info.columns = ['手术名称', '主刀医师', '病人识别号']
                # set form width
                st.markdown('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                st.markdown('<style>div.Widget.row-widget.stRadio > div > label{padding:10px 20px;}</style>', unsafe_allow_html=True)
                # print(operation_info)
                
                # print(ope_date_list_all)
                st.write(operation_info)
        with col2:
            sql_model_performance = f"SELECT * FROM performance;"
            model_performance = inquire_mysql(sql_model_performance, output_format='DataFrame')
            st.write('模型性能指标：')
            st.write(model_performance[['prediction', 'mse', 'mae']])


       