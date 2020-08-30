#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

URL_FUNC_DICT = dict()


def router(url):
    def set_func(func):
        URL_FUNC_DICT[url] = func

        def call_func(*args, **kwargs):
            return func(*args, **kwargs)

        return call_func

    return set_func


@router("/index.py")
def index():
    with open("./templates/index.html", encoding="utf-8") as f:
        content = f.read()
    my_stock_info = "哈哈哈,这是你本月的名称"
    content = re.sub(r"\{%content%\}", my_stock_info, content)
    return content


@router("/center.py")
def center():
    with open("./templates/center.html", encoding="utf-8") as f:
        content = f.read()
    my_stock_info = "这是从mysql中查出的数据"
    content = re.sub(r"\{%content%\}", my_stock_info, content)
    return content


def application(env, start_response):
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)
    file_name = env['PATH_INFO']
    try:
        return URL_FUNC_DICT[file_name]()
    except Exception as KeyError:
        return "An exception is made"
