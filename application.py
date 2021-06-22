from flask import *
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
app = Flask(__name__)
app.secret_key=str(random.randrange(999999999999999))
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
app.permant_session_lifetime =datetime.timedelta(minutes=20)
tz_jst = datetime.timezone(datetime.timedelta(hours=9))
# APIの読み込み
import api
app.register_blueprint(api.app)
# favicon設定
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, "img"), "favicon.ico", mimetype='image/vnd.microsoft.icon')

# CSS設定
@app.route('/css/default.css')
def default_css():
    return send_file("templates/static/css/default.css")
# システム開始日←本番運用開始日を登録すること
sysstart=datetime.datetime(2021,4,10)
# 変数定義
now = datetime.datetime.now()
today = now.strftime("%Y-%m-%d ")
reportable = [str(today)+"06:30:00",str(today)+"08:30:00",str(today)+"16:00:00",str(today)+"20:15:00"]
reqdate = [str(today)+"06:30:00",str(today)+"08:30:00"]
reportabletime=""
datelist=[]#sysstart.strftime("%Y-%m-%d ")]
datelistdt=[]
def daychange():
    global datelist
    global reportable
    global reportabletime
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d ")
    # 土日を休日として扱う
    if datetime.date.today().weekday()>=5:
        holiday=1
    else:
        holiday=0

    # その他休日の有無をDBから取得
    sql="SELECT holiday FROM holiday WHERE date BETWEEN ? AND ? "
    #sql="SELECT date FROM holiday WHERE date "
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    cursor=cnxn.cursor()
    cursor.execute(sql,today,today)
    result= cursor.fetchall()
    print(result)
    # 休日の値を取得
    if len(result)>0:
        result1=int(result[0][0])
    else:
        result1=0
    # 休日の判断
    # DB登録データ
    # 1:月～金の一部日が休日(祝日など) 2:土日が授業日(授業参観など) 0:平日(登録不要)
    if result1==1:
        reportable=[str(today)+"06:30:00",str(today)+"12:00:00",str(today)+"16:00:00",str(today)+"20:15:00"]
        reportabletime="6:30~12:00,16:00~20:15"
        print("今日は休日です")
    elif result1==2 and holiday==1:
        reportable=[str(today)+"06:30:00",str(today)+"08:30:00",str(today)+"16:00:00",str(today)+"20:15:00"]
        reportabletime="6:30~12:00,16:00~20:15"
        print("今日は平日です")
    elif holiday==1:
        reportable=[str(today)+"06:30:00",str(today)+"12:00:00",str(today)+"16:00:00",str(today)+"20:15:00"]
        reportabletime="6:30~12:00,16:00~20:15"
        print("今日は休日です")
    else:
        reportable=[str(today)+"06:30:00",str(today)+"08:30:00",str(today)+"16:00:00",str(today)+"20:15:00"]
        reportabletime="06:30~08:30,16:00~20:15"
        print("今日は平日です")

def datelistadd():
    global datelist
    global datelistdt
    global reportable
    global reportabletime
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d ")
    # システム開始日からリストスタート
    date=sysstart
#    # その他休日の有無をDBから取得
#    sql="SELECT date,holiday FROM holiday WHERE date BETWEEN ? AND ? "
#    #sql="SELECT date FROM holiday WHERE date "
#    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
#    cursor=cnxn.cursor()
#    cursor.execute(sql,sysstart.strftime("%Y-%m-%d"),today)
#    result= cursor.fetchall()
#    print(result)

    # リスト生成(平日はシステム側で8:30に締め出すので休日判定なし)
    while datetime.date.today()+datetime.timedelta(days=1) != date:
#        # 土日を休日として扱う
#        if datetime.date.today().weekday()>=5:
#            holiday=1
#        else:
#            holiday=0
#    
#        # 休日の値を取得
#        if len(result)>0:
#            for i in range(0,len(result)):
#                result1=int(result[i][1])
#                if result1==1:
#                    datelist+=[str(result[i][0].strftime("%Y-%m-%d "))+"06:30:00",str(result[i][0].strftime("%Y-%m-%d "))+"12:00:00",str(result[i][0].strftime("%Y-%m-%d "))+"16:00:00",str(result[i][0].strftime("%Y-%m-%d "))+"20:15:00"]
#        else:
#            result1=0
#        # 休日の判断
#        if result1==1:
#            datelist+=[str(date)+"06:30:00",str(date)+"12:00:00",str(date)+"16:00:00",str(date)+"20:15:00"]
#        elif result1==2 and holiday==1:
#            datelist+=[str(date)+"06:30:00",str(date)+"08:30:00",str(date)+"16:00:00",str(date)+"20:15:00"]
#        elif holiday==1:
#            datelist+=[str(date)+"06:30:00",str(date)+"12:00:00",str(date)+"16:00:00",str(date)+"20:15:00"]
#        else:
#            datelist+=[str(date)+"06:30:00",str(date)+"08:30:00",str(date)+"16:00:00",str(date)+"22:15:00"]
        # 当日の朝の点呼に対応させる処理
        if datetime.date.today() == date and datetime.datetime(date.year,date.month,date.day,now.hour,now.minute) <= datetime.datetime(now.year,now.month,now.day,16,0,0):
            datelist+=[str(date.strftime("%Y-%m-%d "))+"06:30:00",str(date.strftime("%Y-%m-%d "))+"12:00:00"]
        else:
            datelist+=[str(date.strftime("%Y-%m-%d "))+"06:30:00",str(date.strftime("%Y-%m-%d "))+"12:00:00",str(date.strftime("%Y-%m-%d "))+"16:00:00",str(date.strftime("%Y-%m-%d "))+"20:15:00"]
        datelistdt+=[datetime.datetime(date.year,date.month,date.day,6,30),datetime.datetime(date.year,date.month,date.day,12,0),datetime.datetime(date.year,date.month,date.day,16,0),datetime.datetime(date.year,date.month,date.day,20,15)]
        # 月変更の処理
        if date.day==calendar.monthrange(date.year,date.month)[1]:
            date=datetime.date(date.year,date.month+1,1)
        else:
            date=datetime.date(date.year,date.month,date.day+1)

# ログインページへ遷移
@app.route("/",methods=["GET","POST"])
def hello():
    daychange()
    print(reportable)
    now = datetime.datetime.now()
    today = now.strftime("%Y_%m_%d ")
    nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
    i=0
    if reportable[0]<=nowtime<=reportable[1]:
        return render_template("index.html",Error=0)
    elif reportable[2]<=nowtime<=reportable[3]:
        return render_template("index.html",Error=0)
    else:
        return render_template("outofservice.html",reportable_date=reportabletime)

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
         # DBから報告済みか取得
         now = datetime.datetime.now(tz_jst)
         today =now.strftime("%Y-%m-%d ")
         print(reportable)
         i=0
         if reportable[0]<=nowtime<=reportable[1]:
             i=0
         elif reportable[2]<=nowtime<=reportable[3]:
             i=2
         else:
             print(reportable)
             return render_template("outofservice.html",reportable_date=str(reportable))
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
    daychange()

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
    daychange()
    now = datetime.datetime.now()
    today = now.strftime("%Y_%m_%d ")
    nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
    datelistadd()
    print(datelist)
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
             return render_template("index2.html",Error=1)
         elif result == None:
             return render_template("index2.html",Error=4)
         elif result[0] != userpassword:
             return render_template("index2.html",Error=2)
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

             # 表に表示する情報をDBから取得
             #sql="SELECT userid,dormitory_type,room,body_temp,condition,date FROM report WHERE date BETWEEN ? AND ? ORDER BY condition DESC,room,dormitory_type "
             sql="SELECT userid,dormitory_type,room,body_temp,condition,date FROM report WHERE date BETWEEN ? AND ? ORDER BY room,dormitory_type "
             reqdate=request.form.get('date-select')
             print(reqdate)
#             if reqdate == None:
#                 None
#             elif reqdate[0]==reportable[i]:
#                 cursor.execute(sql,reportable[i],reportable[i+1])
#             else:
#                 cursor.execute(sql,reqdate[0],reportable[1])
             cursor.execute(sql,reportable[i],reportable[i+1])
             result= cursor.fetchall()
             #print(result)
             j=0
             # 表に表示する情報を配列に格納
             # 変数の宣言
             uid = [""for j in range(0,len(result))]
             dorm = [""for j in range(0,len(result))]
             droom = [""for j in range(0,len(result))]
             btemp = [""for j in range(0,len(result))]
             cond = [""for j in range(0,len(result))]
             dt = [""for j in range(0,len(result))]
             taion = [float()for j in range(0,len(result))]
             i=0
             arr = [[0 for i in range(0,5)] for j in range(0,len(result))]
             with open("data/temp/report.csv","w") as f:
                 writer = csv.writer(f)
                 writer.writerow(["userid","dormitory_type","room","temperature","condition","datetime"])
             #use=request.form.get(use)
             #print(airr)
             # 格納処理
             for j in range(0,len(result)):
                uid[j]=str(result[j][0])
                dorm[j]=str(result[j][1])
                droom[j]=str(result[j][2])
                btemp[j]=str(result[j][3])
                cond[j]=str(result[j][4])
                dt[j]=str(result[j][5])
                taion[i]=float(result[j][3])
                # 結果をcsvに
                with open("data/temp/report.csv","a") as f:
                    print("writing")
                    writer = csv.writer(f)
                    #if j==0:
                    #    writer.writerow("userid","dormitory_type","room","temperature","condition","datetime")
                    writer.writerow([uid[j],dorm[j],droom[j],btemp[j],cond[j],dt[j]])
                use = None
                print(result[j])
             #返却処理
             session['userid']=userid
             session['login_flag']=True
             print(len(datelist))

             #rend=render_template("checker.html",desired_time=1,userid=userid)
             rend=make_response(render_template("checker.1.html",today=now.strftime("%m/%d") ,userid=uid, date=dt, dormitory_type=dorm, room=droom, temp=btemp,taion=taion, condition=cond,uid_len=len(result),user=userid,datelist=datelist,date_len=int(len(datelist)),datelistdt=datelistdt))
             return rend
@app.route("/checkerdl",methods=["GET","POST"])
def checkerdl():
     now = datetime.datetime.now()
     today = now.strftime("%Y_%m_%d ")
     nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
     cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
     cursor=cnxn.cursor()
     # ユーザID取得
     if session['login_flag']:
         userid = session['userid']
         print(request)
         if userid=="btcheck":
             return send_file("data/temp/report.csv", as_attachment = True, attachment_filename = "data/temp/report.csv", mimetype = "text/csv")

@app.route("/checker_chdate",methods=["GET","POST"])
def checker_chdate():
     now = datetime.datetime.now()
     today = now.strftime("%Y_%m_%d ")
     nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
     cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
     cursor=cnxn.cursor()
     # ユーザID取得
     if session['login_flag']:
         userid = session['userid']
         print(request)
         if userid=="btcheck":
             # 表に表示する情報をDBから取得
             #sql="SELECT userid,dormitory_type,room,body_temp,condition,date FROM report WHERE date BETWEEN ? AND ? ORDER BY condition DESC,room,dormitory_type "
             sql="SELECT userid,dormitory_type,room,body_temp,condition,date FROM report WHERE date BETWEEN ? AND ? ORDER BY room,dormitory_type "
             reqdate=request.form.get('date-select')
             print(reqdate)
             cursor.execute(sql,datelist[int(reqdate)],datelist[int(reqdate)+1])
             print(datelist[int(reqdate)])
             print(datelist[int(reqdate)+1])
             result= cursor.fetchall()
             print(result)
             j=0
             # 表に表示する情報を配列に格納
             # 変数の宣言
             uid = [""for j in range(0,len(result))]
             dorm = [""for j in range(0,len(result))]
             droom = [""for j in range(0,len(result))]
             btemp = [""for j in range(0,len(result))]
             cond = [""for j in range(0,len(result))]
             dt = [""for j in range(0,len(result))]
             taion = [float()for j in range(0,len(result))]
             i=0
             arr = [[0 for i in range(0,5)] for j in range(0,len(result))]
             with open("data/temp/report.csv","w") as f:
                 writer = csv.writer(f)
                 writer.writerow(["userid","dormitory_type","room","temperature","condition","datetime"])
             #use=request.form.get(use)
             #print(airr)
             # 格納処理
             for j in range(0,len(result)):
                uid[j]=str(result[j][0])
                dorm[j]=str(result[j][1])
                droom[j]=str(result[j][2])
                btemp[j]=str(result[j][3])
                cond[j]=str(result[j][4])
                dt[j]=str(result[j][5])
                taion[i]=float(result[j][3])
                # 結果をcsvに
                with open("data/temp/report.csv","a") as f:
                    print("writing")
                    writer = csv.writer(f)
                    #if j==0:
                    #    writer.writerow("userid","dormitory_type","room","temperature","condition","datetime")
                    writer.writerow([uid[j],dorm[j],droom[j],btemp[j],cond[j],dt[j]])
                use = None
                print(result[j])
             #返却処理
             session['userid']=userid
             session['login_flag']=True
             print(len(datelist))

             #rend=render_template("checker.html",desired_time=1,userid=userid)
             rend=make_response(render_template("checker.1.html",today=datelist[int(reqdate)] ,userid=uid, date=dt, dormitory_type=dorm, room=droom, temp=btemp,taion=taion, condition=cond,uid_len=len(result),user=userid,datelist=datelist,date_len=int(len(datelist)),sel=int(reqdate)))
             return rend

@app.route("/checker_nocheck",methods=["GET","POST"])
def checker_nocheck():
     now = datetime.datetime.now()
     today = now.strftime("%Y_%m_%d ")
     nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
     cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
     cursor=cnxn.cursor()
     # ユーザID取得
     if session['login_flag']:
         userid = session['userid']
         print(request)
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
             # 最新の報告状況を取得
             sql="SELECT userid,dormitory_type,room FROM report WHERE date BETWEEN ? AND ? ORDER BY room,dormitory_type "
             # 名簿情報を取得
             sql1="SELECT userid,dormitory_type,room FROM users ORDER BY room,dormitory_type "
             cursor.execute(sql,reportable[i],reportable[i+1])
             result= cursor.fetchall()
             cursor.execute(sql1)
             result1=cursor.fetchall()
             print(result)
             # 提出者のIDと名簿の差分を算出
             r=["" for j in range(0,len(result))]
             r1=["" for j in range(0,len(result1))]
             for j in range(0,len(result)):
                 r[j]=result[j][0]
             for j in range(0,len(result1)):
                 r1[j]=result1[j][0]

             nocheck_l=set(r1) - set(r)
             nocheck_l=list(nocheck_l)
             nocheck=list()
             #nocheck=["" for j in range(0,len(nocheck_l))]
             # 未提出者のIDから部屋番号,寮を取得
             sql="SELECT userid,dormitory_type,room FROM users WHERE userid= ? ORDER BY room,dormitory_type "
             for j in range(0,len(nocheck_l)):
                cursor.execute(sql,nocheck_l[j])
                nocheck=nocheck+cursor.fetchall()
             print(nocheck_l)
             ## 型変換
             #r = [[""]*3 for j in range(0,len(result))]
             #r1 =[[""]*3 for j in range(0,len(result1))]
             #
             #for j in range(0,len(result)):
             #    for k in range(0,2):
             #        r[j][k]=str(result[j][k])
             #for j in range(0,len(result1)):
             #    for k in range(0,2):
             #        r1[j][k]=str(result1[j][k])
             ##r=list(result)
             ##r1=list(result1)
             #nocheck=set(r1)-set(r)

             j=0
             # 表に表示する情報を配列に格納
             # 変数の宣言
             uid = [""for j in range(0,len(nocheck))]
             dorm = [""for j in range(0,len(nocheck))]
             droom = [""for j in range(0,len(nocheck))]
             i=0
             arr = [[0 for i in range(0,5)] for j in range(0,len(result))]
             with open("data/temp/noreport.csv","w") as f:
                 writer = csv.writer(f)
                 writer.writerow(["userid","dormitory_type","room"])
             #use=request.form.get(use)
             print(nocheck)
             nocheck_l=list(nocheck)
             # 格納処理
             for j in range(0,len(nocheck)):
                uid[j]=str(nocheck[j][0])
                dorm[j]=str(nocheck[j][1])
                droom[j]=str(nocheck[j][2])
                # 結果をcsvに
                with open("data/temp/noreport.csv","a") as f:
                    print("writing")
                    writer = csv.writer(f)
                    #if j==0:
                    #    writer.writerow("userid","dormitory_type","room","temperature","condition","datetime")
                    writer.writerow([uid[j],dorm[j],droom[j]])
                use = None
             print(nocheck)
             return render_template("checker.2.html",today=now.strftime("%m/%d") ,userid=uid, dormitory_type=dorm, room=droom ,user=userid, uid_len=len(uid))
@app.route("/nocheckerdl",methods=["GET","POST"])
def nocheckerdl():
     now = datetime.datetime.now()
     today = now.strftime("%Y_%m_%d ")
     nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
     cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
     cursor=cnxn.cursor()
     # ユーザID取得
     if session['login_flag']:
         userid = session['userid']
         print(request)
         if userid=="btcheck":
             return send_file("data/temp/noreport.csv", as_attachment = True, attachment_filename = "data/temp/noreport.csv", mimetype = "text/csv")
if __name__ =="__main__":
    app.run(debug=False,host="0.0.0.0",port=5000,threaded=True)

