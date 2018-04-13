import socketserver
import json


class ServerHanlder(socketserver.BaseRequestHandler):
    print('ServerHandler 类开始实例化...')

    def handle(self):
        print('handler 函数开始执行...')

        # 定义链接循环
        while True:
            data = self.request.recv(1024).strip()
            data = json.loads(data.decode("utf8"))
            """
                data = {
                    "action":"auth",
                    "user":"test",
                    "pwd":123
                }
            """
            # action不能为空
            if data.get("action"):
                if hasattr(self,data.get("action")):
                    func = getattr(self,data.get("action"))
                    func(**data)
                else:
                    print("没有这个命令，请重新开始。")
            else:
                print("命令不能为空! 请重新开始。")


    # auth 登录验证功能
    def auth(self,data):
        user = data["user"]
        pwd = data["pwd"]
