import socket
import queue

from event import EventDispatcher


def nick(nickname, hopcount=0):
	return 'NICK {nickname} {hopcount}\r\n'.format(nickname=nickname, hopcount=hopcount).encode('utf-8')

def user(user, host, server, real):
	return 'USER {user} {host} {server} :{real}\r\n'.format(user=user, host=host, server=server, real=real).encode('utf-8')



class Message(object):
	def __init__(self, message):
		self._raw = message
		
		(self._prefix, message) = self._prefix(message)
		(self._command, message) = self._command(message)
		(self._params, message) = self._params(message)
	
	
	@property
	def raw(self):
		return self._raw
	
	@property
	def prefix(self):
		return self._prefix
	
	@property
	def command(self):
		return self._command
	
	@property
	def params(self):
		return self._params
	
	
	def _prefix(self, message):
		if not message[0] == ':':
			return None, message
		
		return message.split(' ', 1)
	
	def _command(self, message):
		return message.split(' ', 1)
	
	def _params(self, message):
		params = {
			'middle': [],
			'trailing': '',
		}
		
		if message.find(':') != -1:
			(middle, params['trailing']) = message.split(':', 1)
		
		else:
			middle = message
		
		params['middle'] = list(filter(lambda x: x, middle.split(' ')))
		
		return params, ''
	

class Client(EventDispatcher):
	def __init__(self, host, port, *args, **kwargs):
		kwargs.setdefault('ignore_case', True)
		
		super(Client, self).__init__(*args, **kwargs)
		
		self.push_handler('ping', self.on_ping)
		
		self._host = host
		self._port = port
		self._nick = 'fruktkakan'
		
		self._queue = queue.Queue()
		
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self.connect()
	
	
	def on_ping(self, data):
		pass
	
	
	def connect(self):
		self._socket.connect((self._host, self._port))
		
		self.send(nick(self._nick))
		self.send(user(self._nick, self._nick, self._nick, "My Name"))
	
	
	def send(self, msg):
		self._socket.send(msg)
	
	
	def run(self):
		recv = b''
		
		while True:
			recv += self._socket.recv(512)
			
			if not recv:
				break
			
			while recv.find(b'\r\n') != -1:
				(line, recv) = recv.split(b'\r\n', 1)
				
				message = Message(line.decode('utf-8'))
				
				self.dispatch_event('on_message', message, callback=lambda data: self._queue.put(data))
				self.dispatch_event('on_' + message.command, message, callback=lambda data: self._queue.put(data))
			
			while not self._queue.empty():
				try:
					respons = self._queue.get()
					
					if respons:
						self.send(respons)
					
					self._queue.task_done()
				
				except queue.Empty:
					break
	
	def stop(self):
		self.send(b'QUIT :done\r\n')
		
		self._queue.join()
		
		self._socket.close()
	
