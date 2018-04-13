import optparse
import socket

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
        user = options.user
        password = options.password

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

    # 链接函数
    def connect(self,options):
        server = options.server
        port = options.port
        self.socket = socket.socket()
        self.socket.connect((server,port))

    # 交互函数
    def interactive(self):

        # 用户密码登录验证
        if self.authenticate():
            pass
        else:
            print("用户名或密码有误，登录失败！ ")

    # 登录验证函数
    def authenticate(self):
        if user is None or password is None:
            print("user | password 不能为空！")
            user = input("输入用户名>>> ")
            password = input("输入密码>>> ")
            return get_auth_result(user,password)
        return get_auth_result(self.options.user,self.options.password)


    def get_auth_result(self,user,password):
        pass







if __name__ == '__main__':
    client = ClientHandler()
    client.interactive()