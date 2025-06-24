import socket
import json
import asyncio

class Client:
  def __init__(self, server_ip):
    self.server_ip = server_ip
    self.s = socket.create_connection((server_ip, 7777))

  async def recv(self):
    loop = asyncio.get_running_loop()
    message = (await loop.sock_recv(self.s, 1024)).decode('utf-8')
    return json.loads(message)

  async def send(self, message):
    self.s.send(message.encode('utf-8'))

async def start():
  client = Client(input('Server ip: '))
  while True:
    message = await client.recv()
    if message['type'] == 'msg':
      print(message['msg'], end='')
      message = json.dumps({'msg':'Ok'})
      await client.send(message)
    elif message['type'] == 'request':
      print(message['msg'], end='')
      message = json.dumps({'msg':input()})
      await client.send(message)
    elif message['type'] == 'command':
      if message['msg'] == 'exit':
        break

asyncio.run(start())