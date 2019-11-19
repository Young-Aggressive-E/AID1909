"""
ftp 服务器 服务端
env  python3.6
多线程并发 ,socket ,文件IO
"""
from socket import *
from threading import Thread
from time import sleep
import sys, os

# 全局变量
HOST = '0.0.0.0'
PORT = 8080
ADDR = (HOST, PORT)
FTP = "/home/tarena/1909/month02/ftp/"  # 文件库位置

# 文件处理功能
class FTPServer(Thread):

    def __init__(self, connfd):
        self.connfd = connfd
        super().__init__()

    # 文件列表发送
    def do_list(self):
        # 获取文件列表
        files = os.listdir(FTP)
        if not files:
            self.connfd.send("文件库为空".encode())
            return
        else:
            self.connfd.send(b"OK")
            sleep(0.1)  # 防止粘包
        # 发送文件列表
        filelist = "\n".join(files)
        self.connfd.send(filelist.encode())

    # 下载文件
    def do_get(self, filename):
        try:
            f = open(FTP + filename, "rb")
        except Exception:
            # 文件不存在
            self.connfd.send("无法下载文件".encode())
            return
        else:
            self.connfd.send(b"OK")
            sleep(0.1)
        # 发送文件
        while True:
            data = f.read(1024)
            if not data:
                sleep(0.1)
                self.connfd.send(b"##")
                break
            self.connfd.send(data)
        f.close()

    # 上传文件
    def do_put(self,filename):
        if os.path.exists(FTP+filename):
            self.connfd.send("文件已经存在".encode())
            return
        else:
            self.connfd.send(b"OK")

        #接收文件
        f = open(FTP+filename, "wb")
        # 循环接收内容写入文件
        while True:
            data = self.connfd.recv(1024)
            if data == b"##":
                break
            f.write(data)
        f.close()

    # 控制函数，任务分发
    def run(self):
        while True:
            # 接收客户端具体请求（LIST,PUT,GET,EXIT）
            data = self.connfd.recv(1024).decode()
            if not data or data =="EXIT":
                return
            elif data == "LIST":
                self.do_list()
            elif data[:3] == "GET":
                filename = data.split(" ")[-1]
                self.do_get(filename)
            elif data[:3] == "PUT":
                filename = data.split(" ")[-1]
                self.do_put(filename)

# 网络搭建 (多线程并发网络)
def main():
    # 创建套接字
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sockfd.bind(ADDR)
    sockfd.listen(3)

    print("Listen the port 8080...")

    while True:
        try:
            connfd, addr = sockfd.accept()
            print("Counect from", addr)
        except KeyboardInterrupt:
            sockfd.close()
            sys.exit("服务退出")
        except Exception as e:
            print(e)
            continue

        # 创建线程处理客户端请求
        t = FTPServer(connfd)  # 使用自定义线程类生成线程对象
        t.setDaemon(True)  # 主线程服务结束,分支线程也退出服务
        t.start()


if __name__ == '__main__':
    main()
