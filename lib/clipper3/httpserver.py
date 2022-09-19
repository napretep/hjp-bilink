# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'httpserver.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/9/18 9:23'
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from urllib.parse import unquote
import json
data = {'result': 'this is a test'}
host = ('localhost', 8888)
webroot = os.path.join(os.path.dirname(__file__),"web")
textFile=["txt","js","html","css"]

print(webroot)
class index:
    html = os.path.join(webroot,"index.html")
    js = os.path.join(webroot,"index.js")
#
# html = os.path.join(webroot,"index.html")

class Resquest(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "Apache"  # 设置服务器返回的的响应头

    def do_GET(self):
        if self.path == "/":
            requestPath = index.html
        else:
            requestPath = os.path.join(webroot, self.path[1:])
        print(requestPath)
        paths = unquote(self.path)
        path = str(paths)
        plist = path.split("/", 2)
        self.send_response(200)
        self.send_header("Content-type", "text/html")  # 设置服务器响应头
        self.send_header("test1", "This is test!")  # 设置服务器响应头
        self.end_headers()
        returnFile = "not found".encode()
        ext = os.path.splitext(requestPath)[-1]
        # if not os.path.exists(requestPath):
        #     returnFile = "not found".encode()
        # elif ext in textFile:
        if os.path.exists(requestPath):
            returnFile = open(requestPath,mode="rb").read()

        self.wfile.write(returnFile)
        # 里面需要传入二进制数据，用encode()函数转换为二进制数据   #设置响应body，即前端页面要展示的数据

    def do_POST(self):
        path = self.path



        print(self.headers)
        # 获取post提交的数据
        datas = self.rfile.read(int(self.headers['content-length']))  # 固定格式，获取表单提交的数据
        # datas = urllib.unquote(datas).decode("utf-8", 'ignore')
        print( json.loads(datas))
        self.send_response(200)
        self.send_header("Content-type", "text/html")  # 设置post时服务器的响应头
        self.send_header("test", "This is post!")
        self.end_headers()

        html = '''<!DOCTYPE HTML>
        <html>
            <head>
                <title>Post page</title>  
            </head>
            <body>
                Post Data:%s  <br />
                Path:%s
            </body>
        </html>''' % (datas, self.path)
        self.wfile.write(html.encode())  # 提交post数据时，服务器跳转并展示的页面内容
