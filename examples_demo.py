from wsgiref import simple_server
from web import MyWeb, dict2obj

# 第一级，分别实例化自己
idx = MyWeb.Router()  # index
py = MyWeb.Router('/python')
ja = MyWeb.Router('/java')

# 把第一级 route 注册到 MyWeb 类上
MyWeb.register_router(idx)
MyWeb.register_router(py)
MyWeb.register_router(ja)


# 注册 Route 级别的 request 拦截器
@py.reg_preinterceptor
def show_prefix(ctx: dict2obj.NestedContext, request: MyWeb.Request) -> MyWeb.Request:
    print(ctx.route.prefix)
    return request


# 注册 Route 级别的 response 拦截器。
@py.reg_postinterceptor
def show_prefix(ctx: dict2obj.NestedContext, request: MyWeb.Request, response: MyWeb.Response) -> MyWeb.Request:
    body = response.body

    # 如果数据是字典，就把数据 json 化
    if isinstance(body, dict):
        return MyWeb.jsonify(body)
    else:
        return response


# 注册 MyWeb 全局级别的 response 拦截器。
@MyWeb.reg_postinterceptor
def show_user_agent(ctx: dict2obj.Context, request: MyWeb.Request, response: MyWeb.Response) -> MyWeb.Response:
    print(ctx)
    print(request.user_agent)
    return response


# 注册全局扩展插件到 MyWeb 的字典 ctx
@MyWeb.reg_extend('add')
def add():
    print('im extend_add')


# 注册 router 自己分类下的路由
@idx.route(r'^/?$')
def root(request: MyWeb.Request) -> MyWeb.Response:
    html = r""" 
    <h1>python: /python/{people_name:any}/{user_id:int}<h1><p>
    <h1>java:   /java/{app:word}/{version:float}/download<h1>
    """
    return MyWeb.Response(html)


@py.route(r'^/?$', 'GET')
def python_root(request: MyWeb.Request) -> MyWeb.Response:
    userlist = {
        'tom': 20,
        'jerry': 16,
        'sam': 23,
        'kevin': 18
    }
    return MyWeb.Response(userlist)


@py.route(r'/{people_name:any}/{user_id:int}')
def python_devops(request: MyWeb.Request) -> MyWeb.Response:
    html = f'<h1>You Access web is [people: {request.vars.people_name}] and [user_id: {request.vars.user_id}]<h1>'
    return MyWeb.Response(html)


@ja.route(r'/{app:word}/{version:float}/download')
def java(request: MyWeb.Request) -> MyWeb.Response:
    html = f'<h1>You Access web is [app: {request.vars.app}] and [float: {request.vars.version}]<h1>'
    return MyWeb.Response(html)


if __name__ == '__main__':
    server = simple_server.make_server('127.0.0.1', 9999, MyWeb())
    server.serve_forever()
