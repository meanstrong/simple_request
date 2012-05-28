from .httprequest import HTTPRequest
from .httprequest import __version__

def get(url, *args, **kargs):
    return HTTPRequest(method='GET', url=url, **kargs)

def post(url, *args, **kargs):
    return HTTPRequest(method='POST', url=url, **kargs)
