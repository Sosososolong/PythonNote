import socket
import re
import sys

import gevent
from gevent import monkey

monkey.patch_all()


class WSGIServer(object):
    def __init__(self, port, app, static_path):
        self.application = app
        self.static_path = static_path
        # 1.创建套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 2.绑定端口
        self.tcp_server_socket.bind(("", port))

        # 3.变为监听套接字
        self.tcp_server_socket.listen(128)

    def service_client(self, new_socket):
        # 1.等待并接收用户发送的数据, 即一个HTTP请求
        # GET / HTTP/1.1
        # ...
        request = new_socket.recv(1024).decode("utf-8")
        request_lines = request.splitlines()
        # print("")
        # print(">" * 20)
        # print(request_lines)

        # GET /index.html HTTP/1.1
        file_name = ""
        ret = re.match(r"[^/]+/([^ ]*)", request_lines[0])
        if ret:
            file_name = ret.group(1)
            if not file_name:
                file_name = "index.html"

        # 2 返回http格式的数据给浏览器
        # 2.1 如果请求的资源不是以.py结尾，那么就认为是静态资源
        if not file_name.endswith('.html'):
            try:
                f = open(self.static_path + file_name, "rb")
            except:
                response = "HTTP/1.1 404 NOT FOUND\r\n"
                response += "\r\n"
                response += "-------file not found-------"
                new_socket.send(response.encode("utf-8"))
            else:
                html_content = f.read()
                f.close()

                # 2.返回HTTP格式的数据给浏览器
                # 2.1 准备发送给浏览器的数据 -- header
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                # 2.2 准备发送给浏览器的数据 -- body

                # 将response header发送给浏览器
                new_socket.send(response.encode("utf-8"))
                # 将response body发送给浏览器
                new_socket.send(html_content)
        else:
            # 2.2 如果文件名后缀是.py，那么就认为是动态资源的请求
            env = dict()
            env["PATH_INFO"] = file_name
            body = self.application(env, self.set_response_header)
            header = 'HTTP/1.1 %s\r\n' % self.status
            for temp in self.headers:
                header += "%s:%s\r\n" % (temp[0], temp[1])
            header += '\r\n'

            response = header + body
            new_socket.send(response.encode('utf-8'))

        # 关闭套接字
        new_socket.close()

    def set_response_header(self, status, headers):
        self.status = status
        self.headers = [("server", "mini_http_server")]
        self.headers += headers

    def run_forever(self):
        """HTTP 服务器的整体控制"""
        while True:
            # 4.等待客户端的链接
            new_socket, client_addr = self.tcp_server_socket.accept()

            # 5.为这个客户端服务 多进程实现多任务
            gevent.spawn(self.service_client, new_socket)

        # 关闭监听套接字
        tcp_server_socket.close()


def main():
    """控制整体，创建一个web服务器对象，然后调用这个对象的run_forever方法运行web服务"""
    # sys.argv是一个列表，里面是运行python3.exe 后面跟上的参数['http_server.py', '7890', 'mini_frame:application']
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[1])  # 7890
            frame_app_name = sys.argv[2]  # mini_frame:application
        except Exception as ret:
            print("端口输入错误。。。。。。")
            return
    else:
        print("请按照以下格式运行web服务器：")
        print("python3 xxx.py 7890 mini_frame:application")
        return

    # mini_frame:application
    ret = re.match(r"([^:]+):(.*)", frame_app_name)
    if ret:
        frame_name = ret.group(1)  # mini_frame
        app_name = ret.group(2)  # application
    else:
        print("请按照以下格式运行web服务器：")
        print("python3 xxx.py 7890 mini_frame:application")
        return

    with open("./http_server.cnf") as f:
        conf_info = eval(f.read())

    # 导入web框架模块
    # from dynamic import frame_name # 不会frame_name当做变量，回去找frame_name.py模块
    sys.path.append(conf_info["dynamic_path"])
    frame = __import__(frame_name)  # 返回值标记着 导入的这个模块
    app = getattr(frame, app_name)  # 此时app就指向了 dynamic/mini_frame模块中的application这个函数

    wsgi_server = WSGIServer(port, app, conf_info["static_path"])
    wsgi_server.run_forever()


if __name__ == "__main__":
    main()
