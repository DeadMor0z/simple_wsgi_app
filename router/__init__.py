#-*- coding: utf-8 -*-
import re
import json
from http import HTTPStatus

class HttpException(Exception):
    def __init__(self, code):
        if not isinstance(code, HTTPStatus):
            code = HTTPStatus(code)
        super().__init__(code.description)
        self.code = code

class BasicRouter(object):
    """Простейший WSGI-роутер

    Вызывает декорированную функцию, чей ресурс соответствует PATH_INFO.
    Поддерживает указание ресурса в виде regexp-шаблона. Поиск производится от самого длинного ресурса.
    Обрабатывает исключения выдаваемые вызываемой функцией (напр. raise HttpException(HTTPStatus.FORBIDDEN).
    Автоматически конвертирует возвращаемый из функции dict в json и устанавливает соответствующий content-type.
    """

    def __init__(self):
        self.views = {}

    def __call__(self, environ, start_response):
        def client_response(*args, **kwargs):
            nonlocal is_response_written
            is_response_written = True

            if isinstance(args[0], HTTPStatus):
                args = ('{0.value} {0.phrase}'.format(args[0]),) + args[1:]

            start_response(*args, **kwargs)

        view = None
        is_response_written = False
        routes = sorted(self.views.keys(), reverse=True)
        for route in routes:
            if re.match(route, environ['PATH_INFO']):
                view = self.views[route]
                break

        if not view:
            start_response('{0.value} {0.phrase}'.format(HTTPStatus.NOT_FOUND), [('Content-Type','text/html')])
            return [HTTPStatus.NOT_FOUND.description]

        status = HTTPStatus.OK
        try:
            result = view(environ, client_response)
            if is_response_written:
                status = None
        except HttpException as http_e:
            status = http_e.code
            result = status.description
        except Exception as e:
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            result = e

        if isinstance(result, dict):
            result = json.dumps(result)
            content_type = 'application/json'
        else:
            content_type = 'text/html'

        if status:
            start_response('{0.value} {0.phrase}'.format(status), [('Content-Type',content_type)])

        return [str(result).encode('utf-8')]

    def route(self, path):
        """Декоратор для функций-представлений"""

        if not isinstance(path, str):
            raise TypeError('Path must be a string')

        def decorator(func):
            self.views[path] = func
            return func

        return decorator
