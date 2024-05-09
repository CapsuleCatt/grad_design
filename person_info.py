"""
医务信息管理
"""
import streamlit as st
from sql_data_base import inquire_mysql, execute_mysql
from login_config import login_out
import os
import time



def my_info():
    """
    直接大的用户信息函数 没有可拆分
    :return: None
    """
    st.title('医务信息管理')
    st.markdown('***')
    st.write('本页面用于查看、修改个人信息。')
    st.write('当前用户：', st.session_state [ 'user_info' ] [ 'name' ])
    st.write('当前用户ID：', st.session_state [ 'user_info' ] [ 'username' ])
    st.markdown('***')
    if st.button('退出登录'):
        login_out()
        st.rerun()
    st.markdown('***')
    if st.session_state [ 'user_info' ] [ 'username' ] == 'admin':
        st.write('所有用户信息：')
        sql_user_info = "SELECT * FROM users;"
        user_info = inquire_mysql(sql_user_info, output_format='DataFrame')
        st.write(user_info)
        st.markdown('***')
        st.write('修改密码')
        options_users = [i for i in inquire_mysql("SELECT username FROM users;", output_format='DataFrame')['username']]
        selected_user = st.selectbox('选择用户', options_users)
        new_password = st.text_input('新密码', type='password')
        new_password_confirm = st.text_input('确认新密码', type='password')
        if new_password != new_password_confirm:
            st.error('两次输入密码不一致')
        if st.button('确认修改'):
            if new_password == new_password_confirm:
                sql_update_password = f"UPDATE users SET password = '{new_password}' WHERE username = '{selected_user}';"
                execute_mysql(sql_update_password)
                st.success('密码修改成功')
    else:
        st.write('当前用户信息：')
        sql_user_info = f"SELECT * FROM users WHERE username = '{st.session_state [ 'user_info' ] [ 'username' ]}';"
        user_info = inquire_mysql(sql_user_info, output_format='DataFrame')
        st.write(user_info)
        st.markdown('***')
        st.write('修改密码')
        new_password = st.text_input('新密码', type='password')
        new_password_confirm = st.text_input('确认新密码', type='password')
        if new_password != new_password_confirm:
            st.error('两次输入密码不一致')
        if st.button('确认修改'):
            if new_password == new_password_confirm:
                sql_update_password = f"UPDATE users SET password = '{new_password}' WHERE username = '{st.session_state [ 'user_info' ] [ 'username' ]}';"
                execute_mysql(sql_update_password)
                st.success('密码修改成功')
                
