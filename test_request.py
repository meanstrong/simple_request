from simple_request import get,post
response = get(url='http://172.31.89.40/').response
#response = get(url='http://192.168.1.10').response
print response.response.read()
#print (response.response.read())
