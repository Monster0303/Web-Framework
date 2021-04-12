# Web-Framework

一个类似于 Flask 的轻量级 Web 框架

使用 webob 库解析 environ

支持：

- 通过装饰器注册路由
- 自定义分组路由
- 正则匹配
- 简化正则表达式
- 请求方法过滤
- 自定义拦截器
- 自定义插件

# 框架处理流程

1. 先通过装饰器注册路由，注册的规则会被装饰器转换成命名分组的正则表达式；
2. 当客户端发来 HTTP 请求，被 WSGI 服务器处理后传递给 App 的 `__call__`；
3. App 中遍历已注册的 Routers，Routers 的 match 通过前缀匹配来判断是不是自己能处理；
4. 如果由某一个注册的正则表达式匹配，就把获取的参数放到 request 中，并调用注册时映射的 handler 给它传入 request；
5. handler 处理后，返回 response。App 中拿到这个 response 的数据，返回给最初的 wsgi。

# 使用方法

## 一级路由注册

```python
# 导入 app
from web import MyWeb, dict2obj

# 1.注册一级路由，先实例化
idx = MyWeb.Router()  # index
py = MyWeb.Router('/python')
ja = MyWeb.Router('/java')

# 2.再把第一级 route 注册到 MyWeb 类上
MyWeb.register_router(idx)
MyWeb.register_router(py)
MyWeb.register_router(ja)
```

## 内部路由注册

### 分组路由

使用 `{people_name:any}` 进行分组。

- `people_name`：指定分组名，之后通过 `request.vars.people_name` 属性可直接提取匹配部分
- `any`：当前分组允许的数据类型，支持
    - `any`: .*
    - `str`: str,
    - `word`: str,
    - `int`: int,
    - `float`: float,

示例：

```python
@py.route(r'/{people_name:any}/{user_id:int}')
def python_devops(request: MyWeb.Request) -> MyWeb.Response:
    html = f'<h1>You Access web is [people: {request.vars.people_name}] and [user_id: {request.vars.user_id}]<h1>'
    return MyWeb.Response(html)
```

### 过滤请求方法

`r'^/?$', 'GET'` 代表只允许 GET 请求。

示例：

```python
@py.route(r'^/?$', 'GET')
def python_root(request: MyWeb.Request) -> MyWeb.Response:
    test = 'test'
    return MyWeb.Response(test)
```

## 拦截器

根据拦截点不同，分为：

1. 请求时拦截
2. 响应时拦截

根据影响面分为：

1. 全局拦截，在 App 中拦截；
2. 局部拦截，在 Router 中拦截。

### 全局级别拦截器

```python
# request
@MyWeb.reg_preinterceptor
def show_user_agent(ctx: dict2obj.Context, request: MyWeb.Request, response: MyWeb.Response) -> MyWeb.Response:
    return response


# response
@MyWeb.reg_postinterceptor
def show_user_agent(ctx: dict2obj.Context, request: MyWeb.Request, response: MyWeb.Response) -> MyWeb.Response:
    return response
```

### Route 级别拦截器

```python
# request 
@py.reg_preinterceptor
def show_prefix(ctx: dict2obj.NestedContext, request: MyWeb.Request) -> MyWeb.Request:
    return request


# response
@py.reg_postinterceptor
def show_prefix(ctx: dict2obj.NestedContext, request: MyWeb.Request, response: MyWeb.Response) -> MyWeb.Request:
    body = response.body
```

## 插件注册

注册全局扩展插件到 MyWeb 的字典 ctx。

示例：

```python
@MyWeb.reg_extend('add')
def add():
    print('im extend_add')
```

## 本地测试

```python
if __name__ == '__main__':
    server = simple_server.make_server('127.0.0.1', 9999, MyWeb())
    server.serve_forever()
```