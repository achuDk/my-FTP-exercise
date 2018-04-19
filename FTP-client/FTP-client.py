import optparse
import socket
import json
import os

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

    800 : "File exist,but not complete,continue? [ Y/n ]",
    801 : "File exist",
    802 : "Ready to recieve data",

    900 : "Md5 validate success"

}

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
        self.main_path = os.path.dirname(os.path.abspath(__file__))


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
        print("与服务端连接成功，请执行命令：")
        # 用户密码登录验证
        if self.authenticate():
            # 用户执行cmd
            cmd = input("[ %s ]# "%self.user).strip()
            # 接收参数列表
            cmd_list = cmd.split(" ")
            if hasattr(self,cmd_list[0]):
                func = getattr(self,cmd_list[0])
                func(*cmd_list)


    def put(self,*cmd_list):
        print("执行命令 : put")
        # print(*cmd_list)
        # put , 123.png , image
        action,local_path,target_path = cmd_list
        print("执行 put 的目标路径：", target_path)
        local_path = os.path.join(self.main_path,local_path)
        print("文件绝对路径及文件名:", local_path)
        # 文件名
        file_name = os.path.basename(local_path)
        # print("file_name", file_name)
        # 文件大小
        file_size = os.stat(local_path).st_size
        print("执行 put 的文件大小:", file_size)
        # 定义通信内容
        data = {
            "action\t\t":"put",
            "file_name\t":file_name,
            "file_seze\t":file_size,
            "target_path\t":target_path
        }

        # 发送通信内容
        self.socket.send(json.dumps(data).encode("utf8"))

        # 接受服务端的响应，服务端要判断put的文件是否存在以及是否完整
        is_exists = self.socket.recv(1024).decode("utf8")

        # 根据服务器返回的响应码，做出对应动作
        has_sent = 0
        if is_exists == 800:
            # 断点续传
            choice = input(STATUS_CODE[800])
            self.socket.sendall(choice.upper().encode("utf9"))
            if choice == "n" or choice == "N":
                # 客户选择重新上传
                print("即将重新上传文件")
                pass
            else:
                # 进行断点续传
                pass


        elif is_exists == 801:
            print(STATUS_CODE[is_exists])
            # 服务器端文件存在且完整，继续交互，返回None
            return
        elif is_exists == 802:
            print(STATUS_CODE[is_exists])
            # 上传文件
        else:
            print("未知错误！请重试 ")
            return
        ###########################################

        f = open(local_path, "rb")
        while has_sent < file_size:
            data = f.read(1024)
            self.socket.send(data)
            has_sent += len(data)
        f.close()
        print("文件上传完毕！")





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
            print(STATUS_CODE[254])
            return True
        else:
            print(STATUS_CODE[response["status_code"]])
            









if __name__ == '__main__':
    client = ClientHandler()
    client.interactive()