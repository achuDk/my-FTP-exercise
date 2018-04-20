import socketserver
import json
import pymysql
import os
import sys


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

    800: "File exist,but not complete,continue ?",
    801 : "File already exist",
    802 : "Ready to recieve data",

    900 : "Md5 validate success"

}


class ServerHanlder(socketserver.BaseRequestHandler):
    print('ServerHandler 类开始实例化...')

    def handle(self):
        print('handler 函数开始执行...')
        # print("连接的实例对象",self.request)

        # 定义连接循环
        while self.request:
            data = self.request.recv(1024).strip()
            if data:
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
                        func(**data)
                    else:
                        print("没有这个命令，请重新开始。")
                else:
                    print("命令不能为空! 请重新开始。")


                print("\n################################################")
                continue

    # auth 登录验证功能
    def auth(self,**data):
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
        # sql = "CREATE TABLE  IF NOT EXISTS user (id INT PRIMARY KEY AUTO_INCREMENT,username VARCHAR(30) NOT NULL UNIQUE ,passwd VARCHAR(255));"
        # cursor.execute(sql)
        # cursor.execute("insert into user VALUES (1,'alex','123'),(2,'tom','123')")
        cursor.execute("SELECT passwd from user WHERE username=%s",(loginname,))
        db_passwd = cursor.fetchall()
        # print("========>",db_passwd,type(db_passwd))
        if db_passwd:
            if pwd == db_passwd[0]["passwd"]:
                # 如果验证通过，定义对象变量 user
                self.user = loginname
                self.main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                return loginname
        # 验证失败，返回空
        return

        conn.commit()
        cursor.close()
        conn.close()

    def put(self,**data):
        print("接受到来自客户端的 put 命令 : put")
        # print("data >>>",data,type(data))
        file_name = data.get("file_name")
        file_size = data.get("file_size")
        # 文件完整路径及文件名
        target_path = os.path.join(self.main_path,"home",self.user,data.get("target_path"))
        # print("target_path",target_path)
        abs_path = os.path.join(target_path,file_name)

        has_received = 0

        # 判断本地是否已经存在文件且文件是否完整
        if os.path.exists(abs_path):
            print("文件已存在！")
            # 判断文件是否完整，是否需要断点续传
            file_received_size = os.stat(abs_path).st_size
            if file_received_size < file_size:
                print("但是文件不完整，等待客户决定是否进行断点续传")
                # 断点续传
                self.request.sendall("800".encode("utf8"))
                # 接受客户是否进行断点续传的决定
                choice = self.request.recv(1024).decode("utf8")
                if choice == "N":
                    print("客户选择重新上传")
                    f = open(abs_path,"wb")
                else:
                    print("客户同意进行断点续传，续传中...")
                    # has_received = file_received_size
                    # 向客户端发送文件已上传部分的大小
                    self.request.sendall(str(file_received_size).encode("utf8"))
                    # 以追加模式继续写入文件
                    f = open(abs_path, "ab")
            else:
                # 文件存在且完整
                self.request.sendall("801".encode("utf8"))
                # 本次通信结束，返回None
                return
        else:
            # 文件不存在时
            self.request.sendall("802".encode("utf8"))
            f = open(abs_path, "wb")

        while has_received < file_size:
            data = self.request.recv(1024)
            f.write(data)
            has_received += len(data)
        print("【 %s 】文件上传完成" % file_name)
        f.close()

    def ls(self,**data):
        # print(self.main_path)
        file_list = os.listdir(os.path.join(self.main_path,"home",self.user))
        print(file_list)

        file_str = "\n".join(file_list)

        # 【注意】为防止目录为空导致程序阻塞
        if not file_list:
            file_str = "<Empty dir>\n"
        self.request.sendall(file_str.encode("utf*"))

    def cd(self,**data):
        pass