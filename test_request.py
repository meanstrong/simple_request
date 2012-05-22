from simple_request import get, post
response = get(url='192.168.1.1').response
print response.content
