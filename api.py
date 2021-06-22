from types import MethodType
from data.reportData import ReportData
from flask import Blueprint, request
import datetime
import hashlib
import pyodbc
import random
import json
import os
import numpy as np
from my_server_setting import server,database,username,password,driver
import calendar
import csv
from data.reportData import ReportData
# Blueprintのオブジェクトを生成する
app = Blueprint('api', __name__, root_path="/api")

HTTP_OK              = 201
HTTP_UNAUTHORIZED    = 401
HTTP_INVALID_REQUEST = 400

@app.route('/api/report',methods=['POST'])
def reportApi():
    # レポートデータの読み込み
    report = ReportData(
        userid          = request.form["userid"],
        reportTime      = datetime.datetime.now(),
        dormitoryType   = request.form["dormitory_type"],
        roomNumber      = request.form["room_number"],
        bodyTemp        = request.form["body_temp"],
        condition       = request.form["condition"]
    )
    userpassword=request.form["password"]
    # ユーザ認証
    authResult = authorization(report.userid,userpassword)
    if (authResult[1] == HTTP_OK):
        # 認証に成功した場合、レポート
        report.report()
        return "reported", 201
    else:
        # 失敗した場合、失敗を結果として出力
        return authResult[0], authResult[1]

def authorization(userid,userpassword):
    # DBからパスワード取得
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    cursor=cnxn.cursor()
    sql="SELECT userpassword FROM users WHERE userid = ?"
    cursor.execute(sql,userid)
    result=cursor.fetchone()     
    cursor.close()
    cnxn.close()
    # 認証
    i=0
    while i<10:
        userpassword = hashlib.sha256(userpassword.encode()).hexdigest()
        i+=1
    if userid == "" or userpassword == "":
        return "Unauthorized", HTTP_UNAUTHORIZED
    elif result == None:
        return "Invalid Username or Password", HTTP_INVALID_REQUEST
    elif result[0] != userpassword:
        return "Invalid Username or Password", HTTP_INVALID_REQUEST
    else:
        return "logged in", HTTP_OK
