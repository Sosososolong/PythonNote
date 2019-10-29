import logging
import re
import urllib.parse

from pymysql import connect

URL_FUNC_DICT = dict()


def route(file_name):
    def set_func(func):
        URL_FUNC_DICT[file_name] = func

        def call_func(*args, **kwargs):
            return func(*args, **kwargs)

        return call_func

    return set_func


@route("index.html")
def index():
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
                    <input type="button" value="添加" id="toAdd" name="toAdd" systemIdVaule="%s" />
                </td>             
            </tr>
        """
    html = ""
    for line in stock_infos:
        html += tr_template % (line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[1])

    return re.sub(r"\{%content%\}", html, file_con)


@route("center.html")
def center():
    with open("./templates/center.html", "r", encoding="utf-8") as f:
        file_con = f.read()

    conn = connect(host="localhost", port=3306, user="root", password="123456", database="stock_db", charset="utf8")
    cs = conn.cursor()

    cs.execute("select i.code, i.short, i.chg, i.turnover, i.price, i.highs, f.note_info from info as i inner join focus as f on i.id=f.info_id;")
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
            <td>
                <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
            </td>
            <td>
                <input type="button" value="删除" id="toDel" name="toDel" systemIdVaule="%s">
            </td>
        </tr>
        """
    html = ""
    for line in stock_infos:
        html += tr_template % (line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[0], line[0])

    return re.sub(r"\{%content%\}", html, file_con)


@route(r"add/(\d+)\.html")
def add(ret):
    stock_code = ret.group(1)
    conn = connect(host="localhost", port=3306, user="root", password="123456", database="stock_db", charset="utf8")
    cs = conn.cursor()
    # 判断是否有这一支股票
    cs.execute("select * from info where code=%s", (stock_code,))
    if not cs.fetchone():
        cs.close()
        conn.close()
        return "没有这一支股票"

    # 判断是否已经关注过当前股票
    cs.execute("select * from info as i inner join focus as f on i.id=f.info_id where i.code=%s", (stock_code,))
    if cs.fetchone():
        cs.close()
        conn.close()
        return "已经关注过，请勿重复关注"

    # 添加关注
    cs.execute("insert into focus (info_id) select id from info where code=%s", (stock_code,))
    conn.commit()
    cs.close()
    conn.close()

    return "关注成功"


@route(r"del/(\d+)\.html")
def del_focus(ret):
    stock_code = ret.group(1)
    conn = connect(host="localhost", port=3306, user="root", password="123456", database="stock_db", charset="utf8")
    cs = conn.cursor()
    # 判断是否有这一支股票
    cs.execute("select * from info where code=%s", (stock_code,))
    if not cs.fetchone():
        cs.close()
        conn.close()
        return "没有这一支股票"

    # 判断是否已经关注过当前股票
    cs.execute("select * from info as i inner join focus as f on i.id=f.info_id where i.code=%s", (stock_code,))
    if not cs.fetchone():
        cs.close()
        conn.close()
        return "您还没有关注过该股票"

    # 取消关注
    cs.execute("delete from focus where info_id=(select id from info where code=%s)", (stock_code,))
    conn.commit()
    cs.close()
    conn.close()

    return "取消关注成功"


@route(r"update/(\d+)\.html")
def update_page(ret):
    stock_code = ret.group(1)
    with open("./templates/update.html", "r", encoding="utf-8") as f:
        file_con = f.read()

    conn = connect(host="localhost", port=3306, user="root", password="123456", database="stock_db", charset="utf8")
    cs = conn.cursor()

    cs.execute("select f.id, f.note_info, f.info_id, i.code from focus as f inner join info as i on f.info_id=i.id where i.code=%s", (stock_code,))
    stock_info = cs.fetchone()
    if not stock_info:
        cs.close()
        conn.close()
        return "没有此股票"

    cs.close()
    conn.close()

    result = re.sub(r"\{%code%\}", str(stock_info[3]), file_con)
    result = re.sub(r"\{%note_info%\}", stock_info[1], result)
    return result


@route(r"update/(\d+)/(.*)\.html")
def do_update(ret):
    stock_code = ret.group(1)
    stock_note = ret.group(2)
    stock_note = urllib.parse.unquote(stock_note)

    conn = connect(host="localhost", port=3306, user="root", password="123456", database="stock_db", charset="utf8")
    cs = conn.cursor()
    cs.execute("select * from info where code=%s", (stock_code,))
    if not cs.fetchone():
        cs.close()
        conn.close()
        return "没有此股票"

    cs.execute("update focus set note_info=%s where info_id=(select id from info where code=%s)", (stock_note, stock_code))
    conn.commit()
    cs.close()
    conn.close()

    return "修改成功"


def application(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/html;charset=utf-8")])
    method_name = environ["PATH_INFO"]

    # logging基本设置
    # logging.basicConfig(level=logging.INFO,
    #                     filename='./log.txt',
    #                     filemode='a',
    #                     format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # 1.创建一个logger对象, 使用logger对象更加精细地处理日志
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # 2.创建一个handler，用于写入日志文件
    logFile = './log.txt'
    fh = logging.FileHandler(logFile, mode='w', encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    # 3.创建一个handler，用于输出日志到控制台
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.WARNING)
    # 4.定义handler输出格式
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    # ch.setFormatter(formatter)
    # 5.将logger 和 handler 关联
    logger.addHandler(fh)
    # logger.addHandler(ch)

    logger.info("访问的是：%s" % method_name)

    for regular_str, func in URL_FUNC_DICT.items():
        ret = re.match(regular_str, method_name)
        if ret:
            if ret.groups():
                return func(ret)
            else:
                return func()

    logger.warning("没有对应的函数！！")
    return "没有对应的函数！！"
