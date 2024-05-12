import streamlit as st
from streamlit_option_menu import option_menu

# """自己写的函数分割线"""
from login_config import login_in ,init_login ,login_out
from person_info import my_info
from prediction_management import predict_update
import numpy as np
from detailed_data_section import detailed_data
from sql_data_base import inquire_mysql
from ope_prediction import pychart_show
from notice_home import home

init_login ()
login_code = login_in ()
# print(st.session_state [ 'user_info' ])


def get_date():
    """
    获取日期
    :return: 日期
    """
    sql_ope_date_all = "SELECT operation_date FROM anesthesia_form;"
    ope_date_all = inquire_mysql(sql_ope_date_all, output_format='DataFrame')
    # ope_date_all = json.loads(ope_date_all)
    # ope_date_all = pd.DataFrame(ope_date_all)
    print(ope_date_all)
    ope_date_list_all = ope_date_all['operation_date'].to_list()
    # print(ope_date_list_all)
    ope_date_list_all = sorted(ope_date_list_all,key = lambda i:i.date())
    # only show the date
    # ope_date_list_all_converted = [i.split(' ')[0] for i in ope_date_list_all]
    date = np.random.choice(ope_date_list_all)
    return date


if st.session_state [ 'user_info' ]:
    date = get_date()
    if st.session_state [ 'user_info' ]['username']== "admin":
        options = [ "主页" ,'手术室流程时长预测' ,'手术室详细数据' ,'预测模型管理' ,'医务信息管理' ,'退出登录' ]
        icons = [ 'house' ,'hourglass-split' ,'journal-text' ,'clipboard-plus' ,'gear' ,'box-arrow-up-right' ]
    else:
        options = ["主页" ,'手术室流程时长预测' ,'手术室详细数据','医务信息管理', '退出登录' ]
        icons = [ 'house' ,'hourglass-split' ,'journal-text','gear' ,'box-arrow-up-right' ]

    with st.sidebar:
        selected = option_menu ( f'{st.session_state [ "user_info" ] [ "name" ]} 你好' ,options ,icons = icons ,
                                 menu_icon = "cast" ,default_index = 0 )

    if selected == '主页':
        home (date)
    elif selected == '手术室流程时长预测':
        try:
            pychart_show ()
        except:
            pass
    elif selected == '手术室详细数据':
        try:
            detailed_data ()
        except:
            pass

    elif selected == '预测模型管理':
        try:
            predict_update ()
        except:
            pass
    elif selected == '医务信息管理':
        try:
            my_info ()
        except:
            pass
    elif selected == '退出登录':
        login_out ()
        st.rerun ()
