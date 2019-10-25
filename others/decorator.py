# 如果装饰器需要参数》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》
def set_level(level_num):
    def set_func(func):
        def call_func(*args, **kwargs):
            if level_num == 1:
                print("--权限级别1，验证。。。--")
            elif level_num == 2:
                print("--权限级别2，验证。。。--")
            else:
                print("--通用级别验证，验证。。。--")

            func(*args, **kwargs)
        return call_func

    return set_func


@set_level(0)
def do_something():
    print("do something...")


@set_level(1)
def do_something1():
    print("do something1...")


@set_level(2)
def do_something2():
    print("do something2...")


do_something()
do_something1()
do_something2()


exit()


# 用类装饰函数》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》
class Decoration():
    def __init__(self, func, *args, **kwargs):
        self.func = func

    def __call__(self, *args, **kwargs):
        print("这里是装饰器功能。。。")
        return self.func()


@Decoration  # 相当于get_str = Decoration(get_str), get_str此时是Decoration实例，此时调用get_str()相当于调用__call__方法
def get_str():
    return "hahaha"


print(get_str())

exit()


# 多个装饰器装饰同一个函数》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》》
def set_fun(func):
    print("开始装饰1")

    def call_fun(*args, **kwargs):
        print("------权限验证1------")
        print("------权限验证2------")
        # func(args, kwargs)  # 相当于传递了两个参数，一个元组，一个字典
        return func(*args, **kwargs)  # 这里加*的作用是拆包，加上return对没有返回值的函数也没有影响
    return call_fun


def set_fun2(func2):
    print("开始装饰2")

    def call_fun(*args, **kwargs):
        print("这里是装饰器2")
        return func2(*args, **kwargs)
    return call_fun


# 需求：想扩展一下此函数的功能，使调用此函数前要经过一些权限验证，那么上面的装饰器应运而生
@set_fun  # 等价于test1 = set_fun(test1), 让test1指向新的函数，而新的函数内部可以访问到func(原来test1的引用)
@set_fun2
def test1(*args, **kwargs):
    print("----test1----")


test1()
# 开始装饰2
# 开始装饰1
# ------权限验证1------
# ------权限验证2------
# 这里是装饰器2
# ----test1----
test1()
# ------权限验证1------
# ------权限验证2------
# 这里是装饰器2
# ----test1----
exit()
