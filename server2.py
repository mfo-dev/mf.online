import socket
import asyncio
import get_ip
import json

users = {}
usernames = []

rooms = {}


class User:

  def __init__(self, username, conn, addr):
    self.id = addr[0] + ':' + str(addr[1])
    self.username = username
    self.conn = conn
    self.addr = addr
    self.state = 'main_menu'
    self.game = None


class Room:

  def __init__(self, name, owner_id):
    self.name = name
    self.user_ids = []
    self.owner_id = owner_id


async def start():
  loop = asyncio.get_running_loop()
  with socket.create_server((get_ip.get_ip(), 7777)) as s:
    s.setblocking(False)
    s.listen()
    print("Сервер запущен")
    print("IP:Port = ", get_ip.get_ip() + ':7777')
    while True:
      conn, addr = await loop.sock_accept(s)
      asyncio.create_task(handle_client(conn, addr))


async def handle_client(conn, addr):
  msg = 'Enter your username: '
  message = json.dumps({'type': 'request', 'msg': msg})
  await send(conn, message)
  username = await recv(conn)
  msg = 'This username is already taken\nUsername: '
  message = json.dumps({'type': 'request', 'msg': msg})
  if not username or username == 'ConnectionResetError':
    return None
  username = username['msg']
  while True:
    if username not in usernames:
      break
    await send(conn, message)
    username = await recv(conn)
    if not username or username == 'ConnectionResetError':
      return None
    username = username['msg']
  user = User(username, conn, addr)
  users[user.id] = user
  usernames.append(username)
  print(f'{user.username}({user.id}) connected 📢')
  await main_menu(user)


async def send(conn, message):
  conn.send(message.encode('utf-8'))


async def exit(user):
  msg = 'exit'
  message = json.dumps({'type': 'command', 'msg': msg})
  await send(user.conn, message)
  print(f'{user.username}({user.id}) disconnected 📢')
  del users[user.id]
  usernames.remove(user.username)


async def main_menu(user):
  msg = 'Choose action:\n\t0 - Exit\n\t1 - Quick game\n\t2 - Create room\n\t3 - Join room\n -> '
  message = json.dumps({'type': 'request', 'msg': msg})
  await send(user.conn, message)
  message = await recv(user.conn)
  if not message or message == 'ConnectionResetError':
    await exit(user)
    return None
  message = message['msg']
  if message == '0':
    await exit(user)
  elif message == '1':
    pass  # await quick_game(user)
  elif message == '2':
    pass  # await create_room(user)
  elif message == '3':
    pass  # await join_room(user)
  else:
    msg = 'Invalid input\n'
    message = json.dumps({'type': 'msg', 'msg': msg})
    await send(user.conn, message)
    await recv(user.conn)
  await main_menu(user)


async def recv(conn):
  loop = asyncio.get_running_loop()
  try:
    message = (await loop.sock_recv(conn, 1024)).decode('utf-8')
  except ConnectionResetError:
    return 'ConnectionResetError'
  try:
    message = json.loads(message)
    return message
  except json.JSONDecodeError:
    return None
