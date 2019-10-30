# type是一个类，可以用来创建一个类 type(类名，父类，类属性)
Test = type("Test", (), {"num": 100, "num2": 200})

# 创建类Test2，继承自Test
Test2 = type("Test2", (Test,), {})

# 创建类Test3，并指定一个 实例方法


def test_func1(self):
    pass


Test3 = type("Test3", (), {"func1": test_func1})

# 创建类Test4，并指定一个 类方法
@classmethod
def test_func2(cls):
    print("这是一个类方法")


Test4 = type("Test4", (), {"func1": test_func2})

# 创建类Test5，并指定一个 静态方法
@staticmethod
def test_func3():
    pass


Test5 = type("Test5", (), {"func1": test_func3})

# 当定义了一个类的时候，程序其实就是执行默认的type()方法创建类对象
# 如果想修改默认type()中的逻辑，需求：将类的小写属性名都改成大写的，看下面的栗子


def upper_str(class_name, class_parents, class_attr):
    # 遍历属性字典，把不是__开头的属性名字变为大写
    new_attr = {}
    for name, value in class_attr.items():
        if not name.startswith("__"):
            new_attr[name.upper()] = value

    # 调用type来创建一个类
    return type(class_name, class_parents, new_attr)


class UpperAttrMetaClass(type):
    def __new__(mcs, class_name, class_parents, class_attr):
        new_attr = {}
        for name, value in class_attr.items():
            if not name.startswith("__"):
                new_attr[name.upper()] = value

        return type(class_name, class_parents, new_attr)


# class Foo(object, metaclass=upper_str):
class Foo(object, metaclass=UpperAttrMetaClass):
    bar = 'bip'


print(hasattr(Foo, 'bar'))  # False
print(hasattr(Foo, 'BAR'))  # True

foo = Foo()
print(foo.BAR)  # bip
