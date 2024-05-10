import pandas as pd
import json
import data_process
import pymysql
import sql_data_base
from sklearn.model_selection import train_test_split
from quantile_forest import RandomForestQuantileRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Quantile Regression Forest
def grid_search_qrf(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)
    param_grid = {
    'n_estimators': [100, 200, 300, 400, 500],
    'max_depth': [5, 10, 15, 20, 25],
    'min_samples_split': [2, 5, 10, 15, 20],
    'min_samples_leaf': [1, 2, 4, 8, 16],
    # 'max_features': ['auto', 'sqrt', 'log2']
    }
    rfqr = RandomForestQuantileRegressor()
    grid_search = GridSearchCV(rfqr, param_grid, cv=5, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)
    print(grid_search.best_params_)
    rfqr.fit(X_train, y_train)
    y_pred_test = rfqr.predict(X_test, quantiles=[0.25, 0.5, 0.75])
    y_pred = rfqr.predict(X, quantiles=[0.25, 0.5, 0.75])
    y_pred_df = pd.DataFrame(y_pred, columns=['0.25', '0.5', '0.75'])
    # mse, mae, r2
    mse = mean_squared_error(y_test, y_pred_test)
    mae = mean_absolute_error(y_test, y_pred_test)
    r2 = r2_score(y_test, y_pred_test)
    return y_pred_df, mse, mae, r2

def get_data():
    data_ct, data_not_ct = data_process.get_data_from_database()
    # data_all = pd.concat([data_ct, data_not_ct])
    x_data_operation_room_dummies, y_operation_room, x_data_operation_dummies, y_operation, x_data_recovery_dummies, y_recovery = data_process.get_data_for_not_ct(data_not_ct)
    x_data_ct_dummies, y_ct = data_process.get_data_for_ct(data_ct)
    x_data_ct_dummies_i = x_data_ct_dummies[['主刀医生工号_51', 'operation_room_num_12', '主刀医生工号_11', '主刀医生工号_0','operation_num_11','sq手术等级_-1','主刀医生工号_65','operation_room_num_1']]
    x_data_operation_room_dummies_i = x_data_operation_room_dummies[['operation_num_24', 'operation_num_21', 'operation_num_0', '诊断代码_42', 'operation_room_num_20', 'operation_num_14', 'operation_num_9', 'operation_num_44', 'operation_room_num_18', '诊断代码_43']]
    x_data_operation_dummies_i = x_data_operation_dummies[['进出手术机房时长（分）', 's进出苏醒室时长（分）']]
    x_data_recovery_dummies_i = x_data_recovery_dummies[['进出手术机房时长（分）']]
    return x_data_operation_room_dummies_i, y_operation_room, x_data_operation_dummies_i, y_operation, x_data_recovery_dummies_i, y_recovery, x_data_ct_dummies_i, y_ct

def predict_ct_gs(x_data_ct_dummies, y_ct):
    y_pred_ct, mse_ct, mae_ct, r2_ct = grid_search_qrf(x_data_ct_dummies, y_ct)
    return y_pred_ct, mse_ct, mae_ct, r2_ct

def predict_not_ct_gs(x_data_operation_room_dummies, y_operation_room, x_data_operation_dummies, y_operation, x_data_recovery_dummies, y_recovery):
    y_pred_operation_room, mse_operation_room, mae_operation_room, r2_operation_room = grid_search_qrf(x_data_operation_room_dummies, y_operation_room)
    y_pred_operation, mse_operation, mae_operation, r2_operation = grid_search_qrf(x_data_operation_dummies, y_operation)
    y_pred_recovery, mse_recovery, mae_recovery, r2_recovery = grid_search_qrf(x_data_recovery_dummies, y_recovery)
    return y_pred_operation_room, mse_operation_room, mae_operation_room, r2_operation_room, y_pred_operation, mse_operation, mae_operation, r2_operation, y_pred_recovery, mse_recovery, mae_recovery, r2_recovery

def get_syxh():
    data_ct, data_not_ct = data_process.get_data_from_database()
    syxh_ct = data_ct['SYXH']
    syxh_not_ct = data_not_ct['SYXH']
    return syxh_ct, syxh_not_ct

def concat_syxh_and_pred(syxh, y_pred):
    y_pred['SYXH'] = syxh
    return y_pred

def save_to_database(y_pred_ct, y_pred_operation_room, y_pred_operation, y_pred_recovery):
    syxh_ct, syxh_not_ct = get_syxh()
    y_pred_ct = concat_syxh_and_pred(syxh_ct, y_pred_ct)
    y_pred_operation_room = concat_syxh_and_pred(syxh_not_ct, y_pred_operation_room)
    y_pred_operation = concat_syxh_and_pred(syxh_not_ct, y_pred_operation)
    y_pred_recovery = concat_syxh_and_pred(syxh_not_ct, y_pred_recovery)
    connection = pymysql.connect(
    host="121.4.116.90",
    port=3306,
    user="root",
    password="@Cyy4510471",
    database="hopital_system",
    )
    cursor = connection.cursor()
    cursor.execute("truncate table prediction_result")
    connection.commit()
    y_pred_ct.to_sql('y_pred_ct', connection, if_exists='append', index=False)
    y_pred_operation_room.to_sql('y_pred_operation_room', connection, if_exists='append', index=False)
    y_pred_operation.to_sql('y_pred_operation', connection, if_exists='append', index=False)
    y_pred_recovery.to_sql('y_pred_recovery', connection, if_exists='append', index=False)
    cursor.close()
    connection.close()

def save_performance_to_database(mse_ct, mae_ct, r2_ct, mse_operation_room, mae_operation_room, r2_operation_room, mse_operation, mae_operation, r2_operation, mse_recovery, mae_recovery, r2_recovery):
    connection = pymysql.connect(
    host="121.4.116.90",
    port=3306,
    user="root",
    password="@Cyy4510471",
    database="hopital_system",
    )
    cursor = connection.cursor()
    # 更新operation_room performance
    cursor.execute("update table performance where prediction='operation_room' set mse=%s, mae=%s, r2=%s", (mse_operation_room, mae_operation_room, r2_operation_room))
    # 更新operation performance
    cursor.execute("update table performance where prediction='operation' set mse=%s, mae=%s, r2=%s", (mse_operation, mae_operation, r2_operation))
    # 更新recovery performance
    cursor.execute("update table performance where prediction='recovery' set mse=%s, mae=%s, r2=%s", (mse_recovery, mae_recovery, r2_recovery))
    # 更新ct performance
    cursor.execute("update table performance where prediction='ct' set mse=%s, mae=%s, r2=%s", (mse_ct, mae_ct, r2_ct))
    connection.commit()
    cursor.close()
    connection.close()
    return '更新performance成功'