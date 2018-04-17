import socketserver
import json
import pymysql


# 定义状态码字典
STATUS_CODE = {
    250 : "Invalid cmd format, e.g : {'action':'put','filename':'test.py','size':344}",
    251 : "Invalid cmd",
    252 : "Invalid auth data",
    253 : "Wrong username or password",
    254 : "Passed authentication",
    255 : "Filename doesn't provided",
    256 : "File doesn't exist on server",
    257 : "Ready to send file",
    258 : "Md5 verification",

    800 : "File exist,but not complete,continue?",
    801 : "File exist",
    802 : "Ready to recieve data",

    900 : "Md5 validate success"

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
        username = self.authenticate(user,pwd)
        if username:
            self.send_response(254)
        else:
            self.send_response(253)

    def send_response(self,status_code):

        # 详见状态码字典 STATUS_CODE
        response = {
            "status_code":status_code,
            "status_msg":STATUS_CODE[status_code]
        }
        print("response",response)

        # 发送响应信息
        self.request.sendall(json.dumps(response).encode("utf8"))

    # 定义验证功能
    def authenticate(self,user,pwd):
        username = self.connect_mysql(user,pwd)
        # 如果username不为空，则通过，否则失败
        return username

    # 定义查询mysql数据库函数
    def connect_mysql(self,loginname,pwd):
        conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="123456", db="pymysql_python")
        # 定义cursor 接收的结果为字典形式
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # 定义 SQL 语句
        sql = "CREATE TABLE  IF NOT EXISTS user (id INT PRIMARY KEY AUTO_INCREMENT,username VARCHAR(30) NOT NULL UNIQUE ,passwd VARCHAR(255));"
        cursor.execute(sql)
        # cursor.execute("insert into user VALUES (1,'alex','123'),(2,'obama','123')")
        cursor.execute("SELECT passwd from user WHERE username=%s",(loginname,))
        db_passwd = cursor.fetchall()
        # print("========>",db_passwd,type(db_passwd))
        if pwd == db_passwd[0]["passwd"]:
            # 如果验证通过，定义对象变量 user
            self.user = loginname
            return loginname

        conn.commit()
        cursor.close()
        conn.close()
