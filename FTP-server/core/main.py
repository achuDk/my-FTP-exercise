import os,sys,time
import optparse
# print(sys.path)
from core import server
import socketserver
from conf import settings
# print(settings.IP)


# 实现ftp-server端的接收命令参数功能
class ArgvHandler():
    def __init__(self):
        self.opt = optparse.OptionParser()

        self.opt.add_option('-s','--server',dest='server')
        self.opt.add_option('-P','--port',dest='port')
        self.opt.add_option('-u','--user',dest='user')
        self.opt.add_option('-p','--password',dest='password')

        options,args = self.opt.parse_args()

        # print(options.server)
        # print(options.port)
        # print(options.user)
        # print(options.password)
        # print(args)

        self.verifyargs(options,args)

    def verifyargs(self,options,args):
        cmd = args[0]
        if hasattr(self,cmd):
            func = getattr(self,cmd)
            func()

    #定义start、stop、help等功能函数
    def start(self):
        print('server is running ......')

        #启动socketserver接收通信
        s = socketserver.ThreadingTCPServer((settings.IP,settings.PORT),server.ServerHanlder)
        s.serve_forever()

    def stop(self):
        print('server is stopping ......')

    def help(self):
        print('following manual...')
        print(settings.IP)
        print(settings.PORT)

