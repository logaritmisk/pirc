import multiprocessing

from event import EventDispatcher


class AsyncEventDispatcher(EventDispatcher):
	def __init__(self, *args, **kwargs):
		super(AsyncEventDispatcher, self).__init__(*args, **kwargs)
		
		self._processes = []
	
	
	def dispatch_event(self, event, *args, **kwargs):
		callback = kwargs.get('callback', None)
		
		if callback:
			del kwargs['callback']
			
			caller = lambda *args, **kwargs: callback(func(*args, **kwargs))
		
		else:
			caller = lambda *args, **kwargs: func(*args, **kwargs)
		
		for func, config in self.event_handlers(event):
			p = multiprocessing.Process(target=caller, args=args, kwargs=kwargs)
			
			p.start()
			
			self._processes.append(p)
	
