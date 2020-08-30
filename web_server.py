#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实现功能:
为min_frame添加路由功能
author:Jason
date:20200830
"""
import configparser
import os
import socket
import re
import multiprocessing
import sys

# 读取配置文件
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config.read(config_path, encoding='utf-8')
# 获取mini_frame.py路径
dynamic_path = config["FILEPATH"]["dynamic_path"]
# 获取静态文件路径
static_path = config["FILEPATH"]["static_path"]
# 将mini_frame.py添加到模块搜索路径当中
sys.path.append(dynamic_path)


class WSGIServer(object):
    def __init__(self, port, app):
        # 1. 创建套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 2. 绑定
        self.tcp_server_socket.bind(("", port))
        # 3. 变为监听套接字
        self.tcp_server_socket.listen(128)
        self.application = app

    def service_client(self, new_socket):
        """为这个客户端返回数据"""

        # 1. 接收浏览器发送过来的请求 ，即http请求  
        # GET / HTTP/1.1
        request = new_socket.recv(1024).decode("utf-8")
        request_lines = request.splitlines()
        print("" + "\n" + ">" * 20 + "\n", request_lines)
        # GET /index.html HTTP/1.1
        # get post put del
        file_name = ""
        ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
        if ret:
            file_name = ret.group(1)
            print("*" * 50, file_name)
            if file_name == "/":
                file_name = "/index.html"

        # 2. 返回http格式的数据，给浏览器
        if not file_name.endswith(".html"):
            try:
                f = open(static_path + file_name, "rb")
            except:
                response = "HTTP/1.1 404 NOT FOUND\r\n"
                response += "\r\n"
                response += "------file not found-----"
                new_socket.send(response.encode("utf-8"))
            else:
                html_content = f.read()
                f.close()
                # 2.1 准备发送给浏览器的数据---header
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                # 将response header发送给浏览器
                new_socket.send(response.encode("utf-8"))
                # 将response body发送给浏览器
                new_socket.send(html_content)
        else:
            # 2.2 如果是以.py结尾，那么就认为是动态资源的请求
            # 这个字典中存放的是web服务器要传递给 web框架的数据信息
            env = {'PATH_INFO': file_name}
            # {"PATH_INFO": "/index.py"}
            body = self.application(env, self.set_response_header)
            header = "HTTP/1.1 %s\r\n" % self.status
            for temp in self.headers:
                header += "%s:%s\r\n" % (temp[0], temp[1])

            header += "\r\n"
            response = header + body
            # 发送response给浏览器
            new_socket.send(response.encode('utf-8'))
        # 关闭套接
        new_socket.close()

    def set_response_header(self, status, headers):
        self.status = status
        self.headers = [("server", "mini_web v8.8")]
        self.headers += headers

    def run_forever(self):
        """用来完成整体的控制"""

        while True:
            # 4. 等待新客户端的链接
            new_socket, client_addr = self.tcp_server_socket.accept()

            # 5. 为这个客户端服务
            p = multiprocessing.Process(target=self.service_client, args=(new_socket,))
            p.start()
            new_socket.close()

        # 关闭监听套接字
        self.tcp_server_socket.close()


def initial_check():
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[1])
            frame_app_name = sys.argv[2]
        except Exception as e:
            raise ValueError("port is error")
    else:
        raise ValueError(" Incorrect format and correct format is python3 xxxx.py 7890 mini_frame:application")

    # 处理mini_frame:application
    ret = re.match(r"([^:]+):(.*)", frame_app_name)
    if ret:
        frame_name = ret.group(1)  # mini_frame
        app_name = ret.group(2)  # application
    else:
        raise ValueError(" Incorrect format and correct format is python web_server.py 7890 mini_frame:application")
    frame = __import__(frame_name)
    app = getattr(frame, app_name)
    return port, app


def main():
    port1, app1 = initial_check()
    wsgi_server = WSGIServer(port1, app1)
    wsgi_server.run_forever()


if __name__ == "__main__":
    main()
