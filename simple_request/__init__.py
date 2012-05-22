from .httprequest import HTTPRequest

__version__ = '1.0.0'

def get(url, *args, **kargs):
    return HTTPRequest(method='GET', url=url, **kargs)

def post(url, *args, **kargs):
    return HTTPRequest(method='POST', url=url, **kargs)
