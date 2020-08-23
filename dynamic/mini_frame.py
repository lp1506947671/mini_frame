#!/usr/bin/env python
# -*- coding: utf-8 -*-


def index():
    with open("./templates/index.html", encoding="utf-8") as f:
        content = f.read()
    return content


def center():
    with open("./templates/center.html", encoding="utf-8") as f:
        return f.read()


def application(env, start_response):
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)
    file_name = env['PATH_INFO']
    # file_name = "/index.py"

    if file_name == "/index.py":
        return index().encode('utf-8')
    elif file_name == "/center.py":
        return center().encode('utf-8')
    else:
        return 'Hello World! 我爱你中国....'.encode("gbk")
