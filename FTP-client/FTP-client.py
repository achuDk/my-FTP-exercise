import optparse
import socket
import json

class ClientHandler():
    def __init__(self):
        self.opt=optparse.OptionParser()

        self.opt.add_option("-s","--server",dest="server")
        self.opt.add_option("-P","--port",dest="port")
        self.opt.add_option("-u","--user",dest="user")
        self.opt.add_option('-p', '--password', dest='password')

        self.options,self.args = self.opt.parse_args()

        self.verify_args(self.options,self.args)
        self.connect(self.options)

    # 参数校验
    def verify_args(self,options,args):
        server = options.server
        port = options.port

        # user = options.user
        # password = options.password

        # 端口校验
        if int(port) > 0 and int(port) <65535:
            return True
        else:
            exit("端口错误，端口需要为整数且大于零小于65535。")

        # 校验非空
        if not server and not port:
            return True
        else:
            exit("server | port 不能为空！")

        # args 参数校验
        if hasattr(self,args):
            func = getattr(self,args[0])
            func()
        else:
            exit("没有 %s 这个参数" %args[0])

    # 定义连接函数
    def connect(self,options):
        server = options.server
        port = int(options.port)
        self.socket = socket.socket()
        self.socket.connect((server,port))

    # 交互函数
    def interactive(self):

        # 用户密码登录验证
        self.authenticate()

    # 登录验证函数
    def authenticate(self):
        user = self.options.user
        password = self.options.password
        if user is None or password is None:
            print("user | password 不能为空！")
            user = input("输入用户名>>> ")
            password = input("输入密码>>> ")
            return self.get_auth_result(user,password)
        return self.get_auth_result(self.options.user,self.options.password)


    # 定义接收信息函数
    def response(self):
        data = self.socket.recv(1024).decode("utf8")
        data = json.loads(data)
        return data


    def get_auth_result(self,user,password):

        #与服务端建立连接后，第一次通信的内容固定为  身份验证
        data = {
            "action":"auth",
            "user":user,
            "pwd":password
        }

        # 发送验证信息
        self.socket.send(json.dumps(data).encode("utf8"))
        response = self.response()
        print("response:",response)
        print("response",response["status_code"])

        if response["status_code"] == 254:
            self.user = user
            









if __name__ == '__main__':
    client = ClientHandler()
    client.interactive()