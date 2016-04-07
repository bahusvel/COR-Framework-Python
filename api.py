import time

__author__ = 'denislavrov'

"""
If you want to port COR-Module to another language, you must implement everything in this module in the language.

"""


class CORModule:

	def __init__(self, network_adapter=None, *args, **kwargs):
		self.consumes = {}
		if network_adapter is None:
			from .comm import CallbackNetworkAdapter
			self.network_adapter = CallbackNetworkAdapter(self)
		else:
			self.network_adapter = network_adapter
		self.consumes["PING"] = self.pong
		print("Initializaing %s" % type(self).__name__)

	def add_topic(self, type, callback):
		self.consumes[type] = callback

	def messagein(self, message):
		if type(message).__name__ in self.consumes:
			self.consumes[type(message).__name__](message)
		else:
			if "UNSOLICITED" in self.consumes:
				self.consumes["UNSOLICITED"](message)
		if "ANY" in self.consumes:
			self.consumes["ANY"](message)

	# Responsible for dynamic linkage across different communication domains
	def pong(self, ping):
		#self.messageout(Message("PONG", {"moduleID": getattr(self, "moduleID"), "in": list(self.consumes.keys())}))
		pass

	def messageout(self, message):
		while self.network_adapter is None:
			time.sleep(0.01)
		self.network_adapter.message_out(message)

