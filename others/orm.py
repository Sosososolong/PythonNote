class ModelMetaClass(type):
    """该类继承自元类type，那么该类也是一个元类，将生成User类的元类指定为该类
    所以当执行ModelMetaClass()的时候就应该会创建User类，所以只要在__new__()
    方法中实现创建User类即可，当__new__()被调用的时候，回传过来几个参数
    name：类名称，bases：父类(元组) attrs：当前类所有的属性(字典)"""
    def __new__(mcs, name, bases, attrs):
        mappings = {}
        for k, v in attrs.items():  # k-uid v-("id", "int unsigned")
            if isinstance(v, tuple):
                mappings[k] = v

        for k in mappings.keys():
            attrs.pop(k)

        attrs["__attr_field_mappings__"] = mappings
        attrs["__table__"] = name  # 假设表明和类名一致
        return type.__new__(mcs, name, bases, attrs)


class User(object, metaclass=ModelMetaClass):
    uid = ("id", "int unsigned")
    user_name = ("name", "varchar(50)")
    user_email = ("email", "varchar(50)")
    user_pwd = ("password", "varchar(50)")

    def __init__(self, **kwargs):  # (uid=123,name='Michael',...)
        fields = []
        args = []
        # 生成最终需要的字段集合和字段集合的值
        for arg_k, arg_v in kwargs.items():  # uid 123
            # for k, v in self.__attr_field_mappings__.items():
            fields.append(self.__attr_field_mappings__[arg_k][0])
            args.append(arg_v)

        self.fields = fields
        self.args = args

    def save(self):
        args_temp = []
        for temp in self.args:
            if isinstance(temp, int):
                args_temp.append(str(temp))
            else:  # 字符串类型的值要加上引号
                args_temp.append("""'%s'""" % temp)
        # insert into User (id, name, password) values (1, '张三', '123')
        sql = "insert into %s (%s) values (%s)" % (self.__table__, ",".join(self.fields), ",".join(args_temp))
        print(sql)


def main():
    """ 思路：在元类中, 通过"类属性" 和 "字段名称" 关联
        生成对象的时候，将"类属性" 和 字段值关联：User(uid=1, user_name="张三", user_pwd="123")
        通过一个 "类属性" 即可取出对应的字段名称 和 值
        属性->字段值         属性->(字段名称，。。。）
        uid->1              uid->("id", "int unsigned")
        user_name->"张三"   user_name->("name", "varchar(50)")
        user_pwd->"123"     ...
        遍历生成对象时的参数，即可确定 一个字段名称 和 该字段对应的值
    """
    user = User(uid=1, user_name="张三", user_pwd="123")
    user.save()


if __name__ == "__main__":
    main()
