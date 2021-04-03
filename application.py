from flask import *
import datetime
import hashlib
import pyodbc
import random
import json
import os
import numpy as np
from my_server_setting import server,database,username,password,driver
app = Flask(__name__)
app.secret_key=str(random.randrange(999999999999999))
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
app.permant_session_lifetime =datetime.timedelta(minutes=20)
tz_jst = datetime.timezone(datetime.timedelta(hours=9))
# favicon設定
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, "img"), "favicon.ico", mimetype='image/vnd.microsoft.icon')

# CSS設定
@app.route('/css/default.css')
def default_css():
    return send_file("templates/static/css/default.css")

#体温報告可能時間
now = datetime.datetime.now()
today = now.strftime("%Y-%m-%d ")
reportable=[str(today)+"06:30:00",str(today)+"08:30:00",str(today)+"16:00:00",str(today)+"20:15:00"]

# ログインページへ遷移
@app.route("/",methods=["GET","POST"])
def hello():
    now = datetime.datetime.now()
    today = now.strftime("%Y_%m_%d ")
    nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
    i=0
    if reportable[0]<=nowtime<=reportable[1]:
        return render_template("index.html",Error=0)
    elif reportable[2]<=nowtime<=reportable[3]:
        return render_template("index.html",Error=0)
    else:
        return render_template("outofservice.html")

# 報告画面へ遷移
@app.route("/report",methods=["GET","POST"])
def login_manager():
     now = datetime.datetime.now()
     today = now.strftime("%Y_%m_%d ")
     nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
     cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
     cursor=cnxn.cursor()
     # ユーザID取得
     try:
         if session['login_flag']:
             userid = session['userid']
             dormitory_type = session['dormitory_type']
             room=session['room']
             pass
     except Exception as KeyError:
         print(request)
         userid=request.form["userid"]
         userpassword=request.form["password"]
         # DBからパスワード取得
         sql="SELECT userpassword FROM users WHERE userid = ?"
         cursor.execute(sql,userid)
         result=cursor.fetchone()
         # 認証
         i=0
         while i<10:
             userpassword = hashlib.sha256(userpassword.encode()).hexdigest()
             i+=1
         if userid == "" or userpassword == "":
             return render_template("index.html",Error=1)
         elif result == None:
             return render_template("index.html",Error=4)
         elif result[0] != userpassword:
             return render_template("index.html",Error=2)
         # 寮棟取得
         sql = "SELECT dormitory_type FROM users WHERE userid = ?"
         cursor.execute(sql,userid)
         result= cursor.fetchone()
         dormitory_type=result[0]
         # 寮部屋取得
         sql1= "SELECT room FROM users WHERE userid = ?"
         cursor.execute(sql1,userid)
         result=cursor.fetchone()
         room=result[0]
         rend=render_template("report.html",desired_time=1,userid=userid)
         # DBから報告済みか取得(不具合発生するかもしれない)
         now = datetime.datetime.now(tz_jst)
         today =now.strftime("%Y-%m-%d ")
         print(reportable)
         i=0
         if reportable[0]<=nowtime<=reportable[1]:
             i=0
         elif reportable[2]<=nowtime<=reportable[3]:
             i=2
         else:
             return render_template("outofservice.html")
         # 報告状況の取得
        #sql = "SELECT date FROM reports WHERE userid = ? BETWEEN ? AND ?"
        #sql = "SELECT userid=? FROM report WHERE date BETWEEN ? AND ?"
         sql = "SELECT * FROM report WHERE userid=? AND date BETWEEN ? AND ?"
         print(i)
         cursor.execute(sql,userid,reportable[i],reportable[i+1])
         print(reportable[i])
         result = cursor.fetchone()
         print(result)
         if result == None:
             i=i
         elif result[0] == userid:
             return render_template("index.html",Error=5)
         else:
             i=i
         # DB切断
         cursor.close()
         cnxn.close()
         # 返却処理
         session['userid']=userid
         session['login_flag']=True
         session['dormitory_type']=dormitory_type
         session['room']=room
         return rend

# 報告の実行,報告完了画面への遷移
@app.route("/report_register",methods=["GET","POST"])
def report_register():
    condtext=["異常なし","異常あり"]
    # ユーザ情報取得
    userid = session['userid']
    now = datetime.datetime.now()
    today = now.strftime("%Y_%m_%d ")
    nowtime = datetime.datetime.strptime(now.strftime("%H:%M"),"%H:%M")
    nowtime1 = now.strftime("%Y-%m-%d %H:%M:%S")
    dormitory_type = session['dormitory_type']
    room=session['room']
    body_temp = request.form["body_temp"]
    condition = request.form["condition"]
    # DB接続
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+password)
    cursor = cnxn.cursor()
    # セッション認証
    if session['login_flag']:
        # 体温が数値として入力されているか確認
        print(float(body_temp))
        #if body_temp.isnumeric():
        #DBに登録
        sql="INSERT INTO report VALUES(?,?,?,?,?,?)"
        cursor.execute(sql,session["userid"],str(body_temp),str(dormitory_type),str(room),str(condition),str(nowtime1))
        cnxn.commit()
        #else:
        #    render_template("report.html")
    else:
        render_template("index.html",Error=3)
    # DB切断
    cursor.close()
    cnxn.close()
    # 返却
    return render_template("report_success.html",desired_time=nowtime1,userid=userid,body_temp=body_temp,condtext=condtext[int(condition)])

@app.route("/logout")
def logout():
    session.pop('userid',None)
    session.pop('login_flag',None)
    session.pop('dormitory_type',None)
    session.pop('room',None)

    return render_template("index.html",Error=0)

# ユーザー登録への遷移
@app.route("/user_regist_form", methods=["GET", "POST"])
def user_regist_form():
    return render_template("user_regist_form.html")

# ユーザー登録の実行，登録完了画面への遷移
@app.route("/user_register", methods=["GET","POST"])
def user_resister():
    # ユーザ変数取得
    userid = request.form["userid"]
    userpassword = request.form["password"]
    # DB接続
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+password)
    cursor = cnxn.cursor()
    # DBに学籍番号の存在を問い合わせ
    sql = "SELECT userid FROM users WHERE userid=?"
    cursor.execute(sql, userid)
    result = cursor.fetchone()
    if(result == None):
        return render_template("user_regist_form.html", Error=1)
    # DBにパスワードがすでに登録されているかを確認
    sql = "SELECT userpassword FROM users WHERE userid=?"
    cursor.execute(sql, userid)
    result = cursor.fetchone()
    if(result[0] != ""):
        return render_template("user_regist_form.html", Error=2)
    # パスワードストレッチング
    i = 0
    while i<10:
        userpassword = hashlib.sha256(userpassword.encode()).hexdigest()
        i += 1
    # DBにパスワードを登録
    sql = "UPDATE users SET userpassword=? WHERE userid=?"
    cursor.execute(sql, userpassword, userid)
    cnxn.commit()
    # DB切断
    cursor.close()
    cnxn.close()
    # 返却処理
    return render_template("user_regist_success.html")

# 確認者用ログインページへ遷移
@app.route("/checkerlogin",methods=["GET","POST"])
def helloadmin():
    now = datetime.datetime.now()
    today = now.strftime("%Y_%m_%d ")
    nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
    i=0
    return render_template("index2.html",Error=0)

@app.route("/checker",methods=["GET","POST"])
def check():
     now = datetime.datetime.now()
     today = now.strftime("%Y_%m_%d ")
     nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
     cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
     cursor=cnxn.cursor()
     # ユーザID取得
     try:
         if session['login_flag']:
             userid = session['userid']
             dormitory_type = session['dormitory_type']
             room=session['room']
             pass
     except Exception as KeyError:
         print(request)
         userid=request.form["userid"]
         userpassword=request.form["password"]
         # DBからパスワード取得
         sql="SELECT userpassword FROM users WHERE userid = ?"
         cursor.execute(sql,userid)
         result=cursor.fetchone()
         # 認証
         i=0
         while i<10:
             userpassword = hashlib.sha256(userpassword.encode()).hexdigest()
             i+=1
         if userid == "" or userpassword == "":
             return render_template("index1.html",Error=1)
         elif result == None:
             return render_template("index1.html",Error=4)
         elif result[0] != userpassword:
             return render_template("index1.html",Error=2)
         if userid=="btcheck":
             # 時間帯制御
             if nowtime<=reportable[0]:
                 i=0
             elif reportable[0]<=nowtime<=reportable[1]:
                 i=0
             elif reportable[1]<=nowtime<=reportable[2]:
                 i=0
             elif reportable[2]<=nowtime<=reportable[3]:
                 i=2
             else:
                 i=2
             print(i)

             #sql="SELECT userid,dormitory_type,room,body_temp,condition,date FROM report WHERE date BETWEEN ? AND ? ORDER BY condition DESC,room,dormitory_type "
             sql="SELECT userid,dormitory_type,room,body_temp,condition,date FROM report WHERE date BETWEEN ? AND ? ORDER BY room,dormitory_type "
             cursor.execute(sql,reportable[i],reportable[i+1])
             result= cursor.fetchall()
             #print(result)
             j=0
             uid = [""for j in range(0,len(result))]
             dorm = [""for j in range(0,len(result))]
             droom = [""for j in range(0,len(result))]
             btemp = [""for j in range(0,len(result))]
             cond = [""for j in range(0,len(result))]
             dt = [""for j in range(0,len(result))]
             taion = [float()for j in range(0,len(result))]
             i=0
             arr = [[0 for i in range(0,5)] for j in range(0,len(result))]
             
             #print(airr)
             for j in range(0,len(result)):
                uid[j]=str(result[j][0])
                dorm[j]=str(result[j][1])
                droom[j]=str(result[j][2])
                btemp[j]=str(result[j][3])
                cond[j]=str(result[j][4])
                dt[j]=str(result[j][5])
                taion[i]=float(result[j][3])
                print(result[j])

             #rend=render_template("checker.html",desired_time=1,userid=userid)
             rend=make_response(render_template("checker.1.html",today=now.strftime("%m/%d") ,userid=uid, date=dt, dormitory_type=dorm, room=droom, temp=btemp,taion=taion, condition=cond,uid_len=len(result),user=userid))
             return rend
if __name__ =="__main__":
    app.run(debug=True,host="0.0.0.0",port=5000,threaded=True)

