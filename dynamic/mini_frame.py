import re

from pymysql import connect

URL_FUNC_DICT = dict()


def route(file_name):
    def set_func(func):
        URL_FUNC_DICT[file_name] = func

        def call_func(*args, **kwargs):
            func(*args, **kwargs)

        return call_func()

    return set_func


@route("index.html")
def index():
    file_con = ""
    with open("./templates/index.html", "r", encoding="utf-8") as f:
        file_con = f.read()

    conn = connect(host="localhost", port=3306, user="root", password="123456", database="stock_db", charset="utf8")
    cs = conn.cursor()

    cs.execute("select * from info")
    stock_infos = cs.fetchall()

    cs.close()
    conn.close()
    tr_template = """
            <tr>
                <td>%s</td>             
                <td>%s</td>             
                <td>%s</td>             
                <td>%s</td>             
                <td>%s</td>             
                <td>%s</td>             
                <td>%s</td>             
                <td>%s</td>
                <td>
                    <input type="button" value="添加" id="toAdd" name="toAdd" systemidvalue="000007" />
                </td>             
            </tr>
        """
    html = ""
    for line in stock_infos:
        html += tr_template % (line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7])

    return re.sub(r"\{%content%\}", html, file_con)


def center():
    return "来自于center方法中的数据"


def application(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/html;charset=utf-8")])
    method_name = environ["PATH_INFO"]
    return URL_FUNC_DICT[method_name]()
