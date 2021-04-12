"""
模块功能：
    可以接受一个 url，使用简单的匹配模式，并指定要匹配的数据类型，最后返回 Pcre 类型的 regex。
比如：
    /student/{name:str}/xxx/{id:int} -> /student/(?P<name>[^/]+)/xxx/(?P<id>[+-]?\\d+)
"""

import re

# 通过用户指定的类型，映射到正则表达式
TYPE_PATTERNS = {
    'str': r'[^/]+',
    'word': r'\w+',
    'int': r'[+-]?\d+',
    'float': r'[+-]?\d+\.\d+',  # 严苛的要求必须是 15.6这样的形式
    'any': r'.+'
}

# 通过用户指定的类型，映射到 Python 类型
TYPECAST = {
    'str': str,
    'word': str,
    'int': int,
    'float': float,
    'any': str
}

regex = re.compile(r"/({[^{}:]+:?[^{}:]*})")


def tran_from(matcher: re.match):
    """将用户输入的简化正则，转换成标准正则
    {name:str}   -->   (?P<name>\\w+), name, <class 'str'>"""
    name, _, type = matcher.group(1).strip('{}').partition(':')  # 分成 name，type 两段
    type_patterns = TYPE_PATTERNS.get(type, r"\w+")  # 返回 pattern
    type = TYPECAST.get(type, str)  # 返回 type
    return f'/(?P<{name}>{type_patterns})', name, type  # 返回三元组，('(?P<name>\\w+)', 'name', <class 'str'>)最后一个翻译为对应的类型


def parse(src: str):
    """src = /student/{name:str}/xxx/{id:int}
                       ↓
     ('/student/(?P<name>[^/]+)/xxx/(?P<id>[+-]?\\d+)', {'name': <class 'str'>, 'id': <class 'str'>})"""
    translator = {}
    start = 0  # 指针
    result = ''
    while True:
        matcher = regex.search(src, start)
        if matcher:
            result += matcher.string[start:matcher.start()]  # 取前半段 url /student/
            a = tran_from(matcher)  # 函数 tran_from 会返回三元组， '(?P<name>\\w+)', 'name', <class 'str'>
            result += a[0]  # 在 url 上追加翻译好的 /student/ + pattern
            translator[a[1]] = a[2]  # 类型字典 {'name': <class 'str'>, 'id': <class 'str'>}
            start = matcher.end()  # 移动指针
        else:
            result += src[start:]
            break
    return result, translator  # 返回二元组 ('/student/(?P<name>[^/]+)/xxx/(?P<id>[+-]?\\d+)', {'name': <class 'str'>, 'id': <class 'str'>})


if __name__ == '__main__':
    # 用户输入 -> /student/(?P<name>[^/]+)/xxx/(?P<id>[+-]?\\d+)
    s = ['/student/{name:str}/xxx/{id:int}',
         '/student/xxx/{id:int}/yyy',
         '/student/xxx/你好',
         '/student/{name:}/xxx/{id:any}',
         '/student/{name}/xxx/{id:aaa}'
         ]

    wo = parse(s[1])
    print(wo)
