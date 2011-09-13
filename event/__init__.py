class EventDispatcher(object):
	def __init__(self, *args, **kwargs):
		self._ignore_case = kwargs.get('ignore_case', False)
		
		self._stack = {}
	
	
	def event(self, func=None, **kwargs):
		def decorate(func, event=None):
			self.push_handler(event if event else func.__name__, func, **kwargs)
			
			return func
		
		
		if func is None:
			return decorate
		
		elif callable(func):
			return decorate(func)
		
		elif type(func) is str:
			return lambda x: decorate(x, func)
	
	
	def dispatch_event(self, event, *args, **kwargs):
		callback = kwargs.get('callback', None)
		
		if callback:
			del kwargs['callback']
			
			caller = lambda *args, **kwargs: callback(func(*args, **kwargs))
		
		else:
			caller = lambda *args, **kwargs: func(*args, **kwargs)
		
		for func, config in self.event_handlers(event):
			caller(*args, **kwargs)
	
	
	def event_handlers(self, event):
		if self._ignore_case:
			event = event.lower()
		
		return self._stack.get(event, [])
	
	def push_handler(self, event, func, **kwargs):
		if self._ignore_case:
			event = event.lower()
		
		if event not in self._stack:
			self._stack[event] = []
		
		self._stack[event].append((func, {'async': kwargs.get('async', False)}))
	
