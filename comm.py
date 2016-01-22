__author__ = 'denis'


class NetworkAdapter:

	def message_out(self, message):
		pass

	def start(self):
		pass

	def __init__(self, module):
		super().__init__()
		self.module = module
		self.message_callback = module.messagein


class CallbackNetworkAdapter(NetworkAdapter):

	def handle(self, message):
		self.message_callback(message)

	def message_out(self, message):
		super().message_out(message)
		if message.atype in self.callbacks:
			for callback in self.callbacks[message.atype]:
				callback(message)

	def register_callback(self, atype, modules):
		if type(modules) is not list:
			modules = [modules]
		for module in modules:
			if type(module.network_adapter) == CallbackNetworkAdapter:
				if atype in self.callbacks:
					self.callbacks[atype].append(module.network_adapter.handle)
				else:
					self.callbacks[atype] = [module.network_adapter.handle]
			else:
				raise Exception(str(module) + " does not use CallbackNetworkAdapter, cannot register callback!")

	def __init__(self, module):
		super().__init__(module)
		self.callbacks = {}