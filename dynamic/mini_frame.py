#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实现功能:
实现日志记录
author:Jason
date:20200914
"""

import re
import urllib.parse
from pymysql import connect

from dynamic.logger import Log

URL_FUNC_DICT = dict()
a=Log()

def router(url, ):
    def set_func(func):
        URL_FUNC_DICT[url] = func

        def call_func(*args, **kwargs):
            return func(*args, **kwargs)

        return call_func

    return set_func


@router(r"/update/(\d+)\.html")
def show_update_info(ret):
    """
    :param ret:
    :return:
    """
    # 获取股票代码信息
    stock_id = ret.group(1)
    # 打开模板
    with open("./templates/update.html", encoding="utf-8") as f:
        content = f.read()

    # 创建Connection连接
    conn = connect(host="localhost", port=3306, user="root", password="123456", database="stock_db", charset="utf8")
    # 获得Cursor对象
    css = conn.cursor()
    sql = "select * from info where code =%s;"
    css.execute(sql, (stock_id,))
    result = css.fetchall()
    # 3.如果没有这个股票代码则认为是非法请求,关闭连接
    if not result:
        css.close()
        conn.close()
        return "request is error"
    # 执行sql语句
    sql2 = "select f.note_info from focus as f inner join info as i on i.id=f.info_id where i.code=%s;"
    css.execute(sql2, (stock_id,))
    # 获取sql执行后的数据
    stock_info = css.fetchone()
    # 关闭游标连接
    css.close()
    # 关闭连接连接
    conn.close()
    # 生成替换数据
    content = re.sub(r"\{%note_info%\}", stock_info[0], content)
    content = re.sub(r"\{%code%\}", stock_id, content)
    return content


@router(r"/update_info/(\d+)/(.{0,32})\.html")
def save_update_info(ret):
    stock_code = ret.group(1)
    comment = ret.group(2)
    comment = urllib.parse.unquote(comment)
    # 创建Connection连接
    conn = connect(host="localhost", port=3306, user="root", password="123456", database="stock_db", charset="utf8")
    # 获得Cursor对象
    css = conn.cursor()
    sql = """update focus set note_info=%s where info_id =(select id from info where code=%s)"""
    css.execute(sql, (comment, stock_code))
    conn.commit()
    css.close()
    conn.close()
    return "alter ok"


@router(r"/add/(\d+)\.html")
def add_focus(ret):
    # 1.获取股票代码
    stock_code = ret.group(1)
    # 2.判断是否是这个股票代码
    conn = connect(host="localhost", port=3306, user="root", password='123456', database='stock_db', charset='utf8')

    cs = conn.cursor()
    sql = "select * from info where code =%s;"
    cs.execute(sql, (stock_code,))
    result = cs.fetchall()
    # 3.如果没有这个股票代码则认为是非法请求,关闭连接
    if not result:
        cs.close()
        conn.close()
        return "request is error"
    # 4.否者判断是否关注过
    sql1 = "select * from info as i inner join focus as f on i.id=f.info_id where i.code=%s;"
    cs.execute(sql1, (stock_code,))
    # 5.如果关注过则返回请勿重复关注
    if cs.fetchone():
        cs.close()
        conn.close()
        return "it has been focus"

    # 6.添加关注
    sql2 = "insert into focus (info_id) select id from info where code=%s;"
    cs.execute(sql2, (stock_code,))
    conn.commit()
    cs.close()
    conn.close()
    return "focus success"


@router("/index.html")
def index(ret):
    with open("./templates/index.html", encoding="utf-8") as f:
        content = f.read()
    # 创建Connection连接
    conn = connect(host="localhost", port=3306, user="root", password="123456", database="stock_db", charset="utf8")
    # 获得Cursor对象
    css = conn.cursor()
    # 执行sql语句
    css.execute("select * from info;")
    # 获取sql执行后的数据
    stock_info = css.fetchall()
    # 关闭游标连接
    css.close()
    # 关闭连接连接
    conn.close()
    # 获取替换模板
    tr_template = """<tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>
                <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
            </td>
            </tr>
        """
    # 生成替换数据
    html = ""
    for line_info in stock_info:
        html += tr_template % (
            line_info[0], line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6],
            line_info[7], line_info[1])

    content = re.sub(r"\{%content%\}", html, content)
    return content


@router("/center.html")
def center(ret):
    with open("./templates/center.html", encoding="utf-8") as f:
        content = f.read()
    # 建立连接
    conn = connect(host="localhost", port=3306, user="root", password="123456", database="stock_db", charset="utf8")
    # 获取游标
    css = conn.cursor()
    # 执行sql
    css.execute(
        "select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i inner join focus as f on i.id=f.info_id;")
    # 获取sql执行数据
    stock_info = css.fetchall()
    # 关闭游标连接
    css.close()
    # 关闭数据库连接
    conn.close()
    # 获取模板数据
    tr_template = """
           <tr>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>
                   <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
               </td>
               <td>
                   <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
               </td>
           </tr>
       """
    html = ""
    for line_info in stock_info:
        html += tr_template % (
            line_info[0], line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6],
            line_info[0], line_info[0])
    content = re.sub(r"\{%content%\}", html, content)
    return content


def application(env, start_response):
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)
    file_name = env['PATH_INFO']
    a.info(file_name)
    try:
        for url, func in URL_FUNC_DICT.items():
            ret = re.match(url, file_name)
            if ret:
                return func(ret)
    except Exception as e:
        a.warning("not func")
        return "An exception is made %s" % e
