def index():
    return "来自于index方法中的数据"


def center():
    return "来自于center方法中的数据"


def profile():
    return "来自于profile方法中的数据"


URL_FUNC_DICT = dict


def application(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/html;charset=utf-8")])
    method_name = environ["PATH_INFO"]
    return
