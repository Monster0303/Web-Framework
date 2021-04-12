import re, json
from webob import dec, exc, Request, Response
from . import regex2simple, dict2obj


# App 用字典，保存全局参数
# Route 用字典，保存自己实例的参数。在把 route 注册到 App 时，应该将 App 的全局变量字典赋值给内部嵌套的字典 global_context

def jsonify(arg):
    """将数据 json 化"""
    ret = json.dumps(arg)
    return MyWeb.Response(body=ret, status='200', content_type='application/json', charset='utf-8')


class _Router:
    """使用此类实例化一级目录，指定 prefix，比如 /python /java 等，"""

    def __init__(self, prefix: re.compile = ''):
        self.prefix = prefix.rstrip('/\\')  # 自己的一级目录名，去掉最右边可能出现的符号 / 和 \
        self.__route_table = []  # 各个二级目录自己的 path 和 handler 路由表
        self.ctx = dict2obj.NestedContext()  # 初始化 Route 字典，用于保存实例自己的变量
        self.preinterceptor = []  # Route 内的 request 拦截器
        self.postinteceptor = []  # Route 内的 response 拦截器

    def reg_preinterceptor(self, fn):
        """注册 request 拦截器的装饰器"""
        self.preinterceptor.append(fn)
        return fn

    def reg_postinterceptor(self, fn):
        """注册 response 拦截器的装饰器"""
        self.postinteceptor.append(fn)
        return fn

    def route(self, rule: str, *methods):
        """使用此函数注册自己内部的细 path，比如 /python/devops /python/bigdata 等。
        使用方法：带参装饰器"""

        def _wrapper(handler):
            pattern, type = regex2simple.parse(rule)  # 返回 2 元组，把用户输入的简化正则，解析为标准正则，和对应的类型
            self.__route_table.append(
                (methods, re.compile(pattern), type, handler))  # 把请求方法、正则预编译、用户指定的类型、对应的 handler 放到一个四元组中
            return handler

        return _wrapper

    @dec.wsgify
    def route_match(self, request: Request) -> Response:
        """匹配自己管理的"""
        # 必须先匹配前缀
        if not request.path.startswith(self.prefix):
            return None

        # request 拦截器
        for fn in self.preinterceptor:
            request = fn(self.ctx, request)

        # 前缀匹配，说明就必须是这个 Router 实例处理，如后续匹配不上，依然返回None
        for methods, pattern_obj, type, handler in self.__route_table:
            # 匹配请求方法是否合规
            # 这里对业务的理解是，如果没定义 methods 的话，就默认全支持。
            # methods 没定义即等效 false，再 not，代表 methods 是空就为 True，支持所有方法
            if not methods or request.method.upper() in methods:
                # 前提已经是以 prefix 开头了，可以把 prefix 去掉，，去掉 prefix 剩下的才是正则表达式需要匹配的路
                # /python/devops -> /devops
                matcher = pattern_obj.match(request.path.replace(self.prefix, ''))
                # 正则匹配
                if matcher:
                    # 动态为 request 增加属性，实现用户输入 request.vars.name 直接返回 str(hello) 或 int(123)
                    new_dict = {}
                    for k, v in matcher.groupdict().items():
                        new_dict[k] = type[k](v)  # 等于 new_dict[name/id/float/...] = str(v) 或 int(v) 或 float(v)
                    request.vars = dict2obj.Dict2Obj(new_dict)  # 字典对象化，并动态添加到 request 中

                    response = handler(request)

                    # response 拦截器
                    for fn in self.postinteceptor:
                        response = fn(self.ctx, request, response)  # 把 request 也传入，万一要用时方便获取

                    return response


class MyWeb:
    '''
    使用方法：
    MyWeb() 实例化一个 App，应只有一个
    @MyWeb.reg_preinterceptor         注册全局 request 拦截器
    @MyWeb.reg_postinterceptor        注册全局 response 拦截器
    MyWeb.register_router(<router>)             把一级 route 对象注册到 MyWeb 上

    MyWeb.route(<'/path'>)              实例化一级路由
    @route_obj.route(<'/{name:type}/{name:type}/'>)    注册自己内部子类，支持简化的匹配格式
        type 支持：
            'str': str,
            'word': str,
            'int': int,
            'float': float,
            'any': str

    @route_obj.reg_preinterceptor   注册 route 自己的 request 拦截器
    @route_obj.reg_postinterceptor  注册 route 自己的 response 拦截器

    Myweb.jsonify   将 response 数据 json 化
    @Myweb.reg_extend    为 Myweb 添加扩展插件
    '''

    # 以后通过 MyWeb 就可以使用这些
    Request = Request
    Response = Response
    Router = _Router
    jsonify = jsonify

    # 已注册的一级 route 列表
    _ROUTE = []
    ctx = dict2obj.Context()  # 初始化字典，用于保存 App 中全局的变量

    PREINTERCEPTOR = []  # App 内的 request 拦截器
    POSTINTECEPTOR = []  # App 内的 response 拦截器

    @classmethod
    def reg_preinterceptor(cls, fn):
        """注册 request 拦截器的装饰器 """
        cls.PREINTERCEPTOR.append(fn)
        return fn

    @classmethod
    def reg_postinterceptor(cls, fn):
        """注册 response 拦截器的装饰器"""
        cls.POSTINTECEPTOR.append(fn)
        return fn

    @classmethod
    def register_router(cls, route: Router):
        """这是一个用来注册 route 对象的装饰器"""
        cls._ROUTE.append(route)
        route.ctx.route = route  # 在 Route 实例自己的字典中添加一个 Route 自己，如果以后需要用到，方便调用
        route.ctx.relate(cls.ctx)  # 把 App 的全局变量字典赋值到 Route 实例自己的字典中

    @classmethod
    def reg_extend(cls, name):
        """提供类似插件的扩展能力"""

        def _wrapper(extend):
            cls.ctx[name] = extend
            return extend

        return _wrapper

    @dec.wsgify
    def __call__(self, request: Request) -> Response:
        """判断请求中的一级目录，是否已注册，并分配"""

        # request 拦截器
        for fn in self.PREINTERCEPTOR:
            request = fn(self.ctx, request)

        # 把注册的 Route 依次拉出来
        for router in self._ROUTE:
            response = router.route_match(request)

            if response:
                # response 拦截器
                for fn in self.POSTINTECEPTOR:
                    response = fn(self.ctx, request, response)  # 把 request 也传入，万一要用时方便获取

                return response

        raise exc.HTTPNotFound('404 sorry~~ 你 XX')  # 内置的 404 异常，会被 @wsgify 捕获到，做相应的处理
