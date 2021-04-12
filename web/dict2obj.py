"""
将一个字典对象化，可以使用 . 点号访问元素，如同属性一样访问。
有三种实现，略微不同，各有各的用途
"""


class Dict2Obj:
    """包入一个字典并属性化，并且只能查看，不能动态修改字典"""

    def __init__(self, dic: dict):
        # 判断是否为字典，只为字典服务
        if isinstance(dic, (dict,)):
            self.__dict__['_dic'] = dic  # 这样写是防止赋值时递归调用 __setattr__
        else:
            self.__dict__['_dic'] = {}

        # 另一种实现，与实例的字典直接合并，但是有可能出现重名冲突
        # self.__dict__.update(dic if isinstance(dic, dict) else {})

    def __getattr__(self, item):
        try:
            return self._dic[item]
        except KeyError:
            raise AttributeError(f'Attribute {item} Not Found')

    # 明确禁止动态修改字典
    def __setattr__(self, key, value):
        raise NotImplementedError


class Context(dict):
    """上下文字典，本身是字典，把字典属性化
    这里提供给 Web 使用，用来保存全局参数"""

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError('Not Found AttributeError')

    def __setattr__(self, key, value):
        self[key] = value


class NestedContext(Context):
    """嵌套的上下文字典，实现先找自己，找不到就去 global_context 中找
    这里提供给 Route 实例用，用于保存自己实例的参数。当把 route.obj 注册到 App 时，应该将 App 的全局变量字典赋值给内部嵌套的字典 global_context
    """

    global_context: Context

    def __init__(self, global_context: Context = None):
        super().__init__()
        self.relate(global_context)

    def relate(self, global_context: Context = None):
        self.global_context = global_context

    def __getattr__(self, item):
        if item in self.keys():
            return self[item]
        return self.global_context[item]
