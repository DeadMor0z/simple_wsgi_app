# simple_wsgi_app
Пример простейшего WSGI-роутера

router.**BasicRouter** - основной класс-роутер.

router.**BasicRouter.route** - декоратор, для функций, которые будут выполнять роль представлений (view). Параметр - ресурс, по которому будет производится поиск представления (строка или regexp-шаблон).

Декорируемая функция должна принимать два параметра:
1. environ - вся информация о запросе от wsgi-сервера
2. start_response - функция, которая позволяет установить свой собственный HTTP-статус и HTTP-заголовки в ответе. Если start_response не использовалась, то будет установлен HTTP-статус **'200 OK'** и HTTP-заголовок **'Content-Type: text/html'** (если в функции не будет вызвано исключений).

Если декорируемая функция вызовет исключение HttpException, то HTTP-cтатус будет установлен в соответствующий код. Все остальные исключения приведут к возврату HTTP-статуса **'500 INTERNAL SERVER ERROR'**.

Декорируемая функция может вернуть строку или словарь (dict), все остальные типы будут преобразованы в строку (по возможности). Если возвращаемое значение - словарь, то он будет преобразован в json-строку, а заголовок **'Content-Type'** будет установлен в **'application/json'** (если не была использована функия **start_response**).

router.**HttpException** - класс-исключение, для более простого возврата HTTP-статусов. В качестве параметра принимает код HTTP-статуса или перечисляемый тип HTTPStatus.

### Code example - simple_wsgi_app.py

```python
#-*- coding:utf-8 -*-

from router import BasicRouter, HttpException
from http import HTTPStatus

application = BasicRouter()

@application.route(r'/')
def index(environ, start_response):
    return 'Hello, world!!!'

@application.route(r'^/[1-5][1-3]\.test')
def index(environ, start_response):
    return dict(hello='Hello', world='World')

@application.route(r'^/[1-5][1-3]\.test/xyz')
def index(environ, start_response):
    raise HttpException(HTTPStatus.FORBIDDEN)
```
