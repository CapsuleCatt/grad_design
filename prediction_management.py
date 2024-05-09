import pandas as pd
import streamlit as st
import json
from sql_data_base import execute_mysql
import prediction
import data_process
import io


def predict_update():
    st.title('预测模型管理')
    st.write('本页面用于更新预测模型以及更新数据。更新模型涉及到网格搜索，需要较长时间（大约45min）。')
    st.markdown('***')
    if st.button('更新数据'):
        st.chat_message('数据更新中...')
        new_data = data_process.update_data_process()
        status_update = data_process.save_to_database(new_data)
        if status_update == '数据存入成功':
            st.success('数据更新成功')
        else:
            st.error('数据更新失败')
    if st.button('更新模型'):
        st.warning('更新模型可能需要一段时间（大约30min），请耐心等待...')
        st.chat_message('模型更新中...')
        y_pred_ct, mse_ct, mae_ct, r2_ct = prediction.predict_ct_gs()
        st.chat_message('CT时长预测完成')
        y_pred_operation_room, mse_operation_room, mae_operation_room, r2_operation_room, y_pred_operation, mse_operation, mae_operation, r2_operation, y_pred_recovery, mse_recovery, mae_recovery, r2_recovery = prediction.predict_not_ct_gs()
        st.chat_message('手术室、苏醒室、以及全流程时长预测完成')
        st.chat_message('开始存入数据库...')
        prediction.save_to_database(y_pred_ct, y_pred_operation_room, y_pred_operation, y_pred_recovery)
        prediction.save_performance_to_database(mse_ct, mae_ct, r2_ct, mse_operation_room, mae_operation_room, r2_operation_room, mse_operation, mae_operation, r2_operation, mse_recovery, mae_recovery, r2_recovery)
        st.success('模型更新成功')
