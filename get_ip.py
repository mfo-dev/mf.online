import request

def get_ip():
  return request.get('https://api.ipify.org').content.decode('utf8')