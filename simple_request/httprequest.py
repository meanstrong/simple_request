import urllib
from base64 import b64encode
import httplib
import mimetools
import mimetypes
import socket


__version__ = '0.0.2'


class HTTPRequest(object):
    """HTTP request module.
    Arguments:
        method(str):
            'GET','POST'
        url(str):
            HTTP request url.
        params(dict):
            the params append to url.
        data(dict or str):
            the data need to post.
        auth(tuple):
            the basic authenticate username and password.
        cookies(str):
            the cookies to send.
        files(dict):
            the files to send.like: dict(file=('1.txt', open('1.txt')))
    """
    def __init__(self, method, url,
        params=None,
        data=None,
        auth=None,
        cookies=None,
        files=None,
        headers=dict(),
        sessions=None,
        **kargs):
    
        # parse url
        scheme, _auth, host, port, uri = parseurl(url)
        host = socket.gethostbyname(host)
    
        if params is not None:
            params = urllib.urlencode(params)
            uri = '%s?%s' % (uri, params)
    
        body = None
        if data is not None:
            if isinstance(data, str):
                body = data
            elif isinstance(data, dict):
                body = urllib.urlencode(data)
            if 'Content-Type' not in headers.keys() \
            and 'content-type' not in headers.keys():
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
    
        if files:
            #fields = {}
            #for (filename, filedata) in list(files.items()):
            #    fields[filename] = filedata
            (boundary, body) = multipart_encode(files)
            content_type = 'multipart/form-data; boundary=%s' % boundary
            headers['Content-Type'] = content_type
    
        if 'User-Agent' not in headers:
            headers['User-Agent'] = 'Python-httprequest/%s' % __version__
        if 'Accept-Encoding' not in headers:
            headers['Accept-Encoding'] = ','.join(('gzip', 'deflate'))
    
        if auth is not None \
        and isinstance(auth, tuple) \
        and len(auth) == 2:
            headers['Authorization'] = \
                'Basic ' + b64encode("%s:%s" % (auth[0], auth[1]))
        elif _auth is not None:
            headers['Authorization'] = \
                'Basic ' + b64encode(_auth)
    
        if sessions:
            for (key, value) in list(sessions.items()):
                headers[key] = value
    
        if cookies:
            headers['Cookie'] = cookies
    
        print host, method, uri
        self.conn = httplib.HTTPConnection(host, port=port)
        req = self.conn.request(method, uri, body, headers)

    @property
    def response(self):
        if not hasattr(self, 'getresponse'):
            self.getresponse = HTTPResponse(self.conn.getresponse())
            if self.getresponse.will_close:
                self.conn.close()
        return self.getresponse


def parseurl(url):
    scheme = 'http'
    auth = None
    host = url
    port = None
    uri = '/'
    if '://' in host:
        scheme, host = url.split('://', 1)
    if '/' in host:
        host, uri = host.split('/', 1)
        uri = '/' + uri
    if '@' in host:
        auth, host = host.split('@', 1)
    if ':' in host:
        host, port = host.split(':', 1)

    return scheme, auth, host, port, uri

def multipart_encode(files, boundary=None):
    if boundary is None:
        boundary = mimetools.choose_boundary()

    data = ''
    for (key, value) in list(files.items()):
        if isinstance(value, tuple):
            content_type = mimetypes.guess_type(key)[0] \
                or 'application/octet-stream'
            data += '--%s\r\n' % boundary
            data += ('Content-Disposition: form-data; name'
                '="%s"; filename="%s"\r\n') % (key, value[0])
            data += 'Content-Type: %s\r\n' % content_type
            value[1].seek(0)
            data += '\r\n' + value[1].read() + '\r\n'
        else:
            data += '--%s\r\n' % boundary
            data += 'Content-Disposition: form-data; name="%s"' % key
            data += '\r\n\r\n' + value + '\r\n'
    data += '--%s--\r\n\r\n' % boundary
    return boundary, data


class HTTPResponse(object):
    def __init__(self, response=None):
        self.response = response

    def __repr__(self):
        return '<HTTPResponse [%d]>' % self.status

    @property
    def content(self):
        return self.response.read()

    @property
    def status(self):
        return self.response.status

    @property
    def cookies(self):
        return self.response.getheader('set-cookie')

    @property
    def realm(self):
		authenticate = self.response.getheader('www-authenticate')
		if authenticate is not None:
			return authenticate[len('Basic realm="'):-1]
		else:
			return None

    @property
    def headers(self):
        return dict(self.response.getheaders())

    @property
    def will_close(self):
        return self.response.will_close
