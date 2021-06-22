import datetime
import pyodbc
from my_server_setting import server,database,username,password,driver

class ReportData():

    def __init__(self, userid, reportTime, dormitoryType, roomNumber, bodyTemp, condition):
        # ユーザ情報取得
        self.userid         = userid
        self.reportTime     = reportTime
        self.dormitoryType  = dormitoryType
        self.roomNumber     = roomNumber
        self.bodyTemp       = bodyTemp
        self.condition      = condition
        self.genDateTimeStr
    
    def genDateTimeStr(self):
        self.str_reportDate     = self.reportTime.strftime("%Y_%m_%d ")
        self.str_reportTime     = datetime.datetime.strptime(self.reportTime.strftime("%H:%M"),"%H:%M")
        self.str_reportDateTime = self.reportTime.strftime("%Y-%m-%d %H:%M:%S")

    def report(self):
        cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+password)
        cursor = cnxn.cursor()
        sql="INSERT INTO report VALUES(?,?,?,?,?,?)"
        cursor.execute(sql,self.userid,self.bodyTemp,self.dormitoryType,self.roomNumber,self.condition,self.str_reportDateTime)
        cnxn.commit()
        cursor.close()
        cnxn.close()
        return 
