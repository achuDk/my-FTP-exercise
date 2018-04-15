import socketserver
import json
import pymysql


# 定义状态码字典
STATUS_CODE = {

}

class ServerHanlder(socketserver.BaseRequestHandler):
    print('ServerHandler 类开始实例化...')

    def handle(self):
        print('handler 函数开始执行...')

        # 定义链接循环
        while True:
            data = self.request.recv(1024).strip()
            data = json.loads(data.decode("utf8"))

            # 通信body样例
            """
                data = {
                    "action":"auth",
                    "user":"test",
                    "pwd":123
                }
            """

            # 验证 action 不能为空
            if data.get("action"):
                if hasattr(self,data.get("action")):
                    func = getattr(self,data.get("action"))
                    # print(data.get("action"))
                    # print("data",data)
                    func(data)
                else:
                    print("没有这个命令，请重新开始。")
            else:
                print("命令不能为空! 请重新开始。")


    # auth 登录验证功能
    def auth(self,data):
        user = data["user"]
        pwd = data["pwd"]
        print('data:',data)
        print('user:',user)
        print('pwd:',pwd)
        print("接收到用户名和密码，开始验证")
        # 调用验证功能
        self.authenticate(user,pwd)

    def send_response(self,status_code):
        response = {
            "status_code":status_code,
        }
        # 详见状态码字典 STATUS_CODE

    # 定义验证功能
    def authenticate(self,user,pwd):
        username = self.connect_mysql(user,pwd)
        # 如果username不为空，则通过，否则失败
        if username:
            print("验证通过！")
            self.send_response()
        else:
            print("验证失败！")


    # 定义查询mysql数据库函数
    def connect_mysql(self,loginname,pwd):
        conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="123456", db="pymysql_python")
        # 定义cursor 接收的结果为字典形式
        cursor = conn.cursors(cursor=pymysql.cursors.DictCursor)
        # 定义 SQL 语句
        # sql = "CREATE TABLE  IF NOT EXISTS user (id INT PRIMARY KEY AUTO_INCREMENT,username VARCHAR(30) NOT NULL UNIQUE ,passwd VARCHAR(255));"

        cursor.execute("SELECT password from user WHERE user=%s",(loginname,))
        db_passwd = cursor.fetchall()
        print(db_passwd)
        if pwd == db_passwd:
            return loginname

        conn.commit()
        cursor.close()
        conn.close()
