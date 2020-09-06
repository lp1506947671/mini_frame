#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from pymysql import connect

URL_FUNC_DICT = dict()


def router(url):
    def set_func(func):
        URL_FUNC_DICT[url] = func

        def call_func(*args, **kwargs):
            return func(*args, **kwargs)

        return call_func

    return set_func


@router("/index.html")
def index():
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
                <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="000007">
            </td>
            </tr>
        """
    # 生成替换数据
    html = ""
    for line_info in stock_info:
        html += tr_template % (
            line_info[0], line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6],
            line_info[7])

    content = re.sub(r"\{%content%\}", html, content)
    return content


@router("/center.html")
def center():
    with open("./templates/center.html", encoding="utf-8") as f:
        content = f.read()
    # 建立连接
    conn = connect(host="localhost", port=3306, user="root", password="123456",database="stock_db", charset="utf8")
    # 获取游标
    css = conn.cursor()
    # 执行sql
    css.execute("select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i inner join focus as f on i.id=f.info_id;")
    # 获取sql执行数据
    stock_info=css.fetchall()
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
                   <a type="button" class="btn btn-default btn-xs" href="/update/300268.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
               </td>
               <td>
                   <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="300268">
               </td>
           </tr>
       """
    html=""
    for line_info in stock_info:
        html+=tr_template % (line_info[0],line_info[1],line_info[2],line_info[3],line_info[4],line_info[5],line_info[6],)
    content = re.sub(r"\{%content%\}", html, content)
    return content


def application(env, start_response):
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)
    file_name = env['PATH_INFO']
    try:
        return URL_FUNC_DICT[file_name]()
    except Exception as e:
        return "An exception is made%s"%e
