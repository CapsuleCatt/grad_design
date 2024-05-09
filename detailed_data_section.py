import os
import pandas as pd
import streamlit as st
import io
from sql_data_base import execute_mysql, inquire_mysql
from streamlit_option_menu import option_menu
import re
# SPATH = os.path.dirname(os.path.abspath(__file__))


def detailed_data():
    # print('detailed_data')
    if st.session_state['user_info']['username'] == "admin":
        st.title('详细数据')
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
        selected_operation_row_SYXH = selected_operation_row['operation_name'].split('SYXH: ')[1]
        sql_predict_ct = f"SELECT * FROM y_pred_ct WHERE SYXH='{selected_operation_row_SYXH}';"
        predict_ct = inquire_mysql(sql_predict_ct, output_format='DataFrame')
        if predict_ct.empty:
            print('predict_ct is empty')
            sql_detailed_data = f"SELECT SYXH, `进出手术机房时长（分）`, `进出手术室时长（分）`, `s进出苏醒室时长（分）` FROM training_data_set_not_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            sql_predict_ct = f"SELECT * FROM y_pred_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            sql_predict_op_room = f"SELECT * FROM y_pred_operation_room WHERE SYXH='{selected_operation_row_SYXH}';"
            sql_predict_recovery = f"SELECT * FROM y_pred_recovery WHERE SYXH='{selected_operation_row_SYXH}';"
            sql_predict_op = f"SELECT * FROM y_pred_operation WHERE SYXH='{selected_operation_row_SYXH}';"
            detailed_data = inquire_mysql(sql_detailed_data, output_format='DataFrame')
            # predict_ct = inquire_mysql(sql_predict_ct, output_format='DataFrame')
            # print('predict_ct:', predict_ct)
            predict_op_room = inquire_mysql(sql_predict_op_room, output_format='DataFrame')
            # print(predict_op_room)
            predict_op = inquire_mysql(sql_predict_op, output_format='DataFrame')
            # print(predict_op)
            predict_recovery = inquire_mysql(sql_predict_recovery, output_format='DataFrame')
            # print(predict_recovery)
            # 把detailed_data转置，operation, operation_room, recovery作为index, 实际时长，预测时长（25%，50%，75%）作为columns
            # detailed_data和predict_op_room,predict_recovery,predict_op拼起来
            detailed_data = detailed_data.T
            detailed_data.columns = ['实际时长']
            # predict_ct.rename(columns={'0.25': '预测分位数25%', '0.5': '预测分位数50%', '0.75': '预测分位数75%'}, inplace=True)
            # predict_ct.index = ['进出CT室时长（分）']
            # print(predict_ct)
            # predict_ct['实际时长'] = detailed_data.loc['进出CT室时长（分）', '实际时长']
            # print(predict_ct)
            predict_op_room.rename(columns={'0.25': '预测分位数25%', '0.5': '预测分位数50%', '0.75': '预测分位数75%'}, inplace=True)
            predict_op_room.index = ['进出手术机房时长（分）']
            predict_op_room['实际时长'] = detailed_data.loc['进出手术机房时长（分）', '实际时长']
            print(predict_op_room)
            predict_op.rename(columns={'0.25': '预测分位数25%', '0.5': '预测分位数50%', '0.75': '预测分位数75%'}, inplace=True)
            predict_op.index = ['进出手术室时长（分）']
            predict_op['实际时长'] = detailed_data.loc['进出手术室时长（分）', '实际时长']
            predict_recovery.rename(columns={'0.25': '预测分位数25%', '0.5': '预测分位数50%', '0.75': '预测分位数75%'}, inplace=True)
            predict_recovery.index = ['s进出苏醒室时长（分）']
            predict_recovery['实际时长'] = detailed_data.loc['s进出苏醒室时长（分）', '实际时长']
            detailed_table = pd.concat([predict_op_room, predict_op, predict_recovery], axis=0)
            print(detailed_table)
            st.table(detailed_table)
        else:
            # print('predict_ct is not empty')
            sql_detailed_data = f"SELECT SYXH, `进出手术机房时长（分）`, `进出手术室时长（分）`, `s进出苏醒室时长（分）`, `进出CT室时长（分）` FROM training_data_set_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            sql_predict_ct = f"SELECT * FROM y_pred_ct WHERE SYXH='{selected_operation_row_SYXH}';"
            sql_predict_op_room = f"SELECT * FROM y_pred_operation_room WHERE SYXH='{selected_operation_row_SYXH}';"
            sql_predict_recovery = f"SELECT * FROM y_pred_recovery WHERE SYXH='{selected_operation_row_SYXH}';"
            sql_predict_op = f"SELECT * FROM y_pred_operation WHERE SYXH='{selected_operation_row_SYXH}';"
            detailed_data = inquire_mysql(sql_detailed_data, output_format='DataFrame')
            predict_ct = inquire_mysql(sql_predict_ct, output_format='DataFrame')
            # print('predict_ct:', predict_ct)
            predict_op_room = inquire_mysql(sql_predict_op_room, output_format='DataFrame')
            # print(predict_op_room)
            predict_op = inquire_mysql(sql_predict_op, output_format='DataFrame')
            # print(predict_op)
            predict_recovery = inquire_mysql(sql_predict_recovery, output_format='DataFrame')
            # print(predict_recovery)
            # 把detailed_data转置，operation, operation_room, recovery作为index, 实际时长，预测时长（25%，50%，75%）作为columns
            # detailed_data和predict_op_room,predict_recovery,predict_op拼起来
            detailed_data = detailed_data.T
            detailed_data.columns = ['实际时长']
            predict_ct.rename(columns={'0.25': '预测分位数25%', '0.5': '预测分位数50%', '0.75': '预测分位数75%'}, inplace=True)
            predict_ct.index = ['进出CT室时长（分）']
            # print(predict_ct)
            predict_ct['实际时长'] = detailed_data.loc['进出CT室时长（分）', '实际时长']
            # print(predict_ct)
            predict_op_room.rename(columns={'0.25': '预测分位数25%', '0.5': '预测分位数50%', '0.75': '预测分位数75%'}, inplace=True)
            predict_op_room.index = ['进出手术机房时长（分）']
            predict_op_room['实际时长'] = detailed_data.loc['进出手术机房时长（分）', '实际时长']
            # print(predict_op_room)
            predict_op.rename(columns={'0.25': '预测分位数25%', '0.5': '预测分位数50%', '0.75': '预测分位数75%'}, inplace=True)
            predict_op.index = ['进出手术室时长（分）']
            predict_op['实际时长'] = detailed_data.loc['进出手术室时长（分）', '实际时长']
            predict_recovery.rename(columns={'0.25': '预测分位数25%', '0.5': '预测分位数50%', '0.75': '预测分位数75%'}, inplace=True)
            predict_recovery.index = ['s进出苏醒室时长（分）']
            predict_recovery['实际时长'] = detailed_data.loc['s进出苏醒室时长（分）', '实际时长']
            detailed_table = pd.concat([predict_ct, predict_op_room, predict_op, predict_recovery], axis=0)
            # print(detailed_table)
            st.table(detailed_table)
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
        sql_model_performance = f"SELECT * FROM performance;"
        model_performance = inquire_mysql(sql_model_performance, output_format='DataFrame')
        st.write('模型性能指标：')
        st.write(model_performance[['prediction', 'mse', 'mae']])
    else:
        st.error('您没有权限查看此页面')

   