import time

__author__ = 'denislavrov'

"""
If you want to port COR-Module to another language, you must implement everything in this module in the language.

"""


class CORModule:

	def __init__(self, network_adapter=None, *args, **kwargs):
		self.consumes = {}
		try:
			if getattr(self, "moduleID") is None:
				raise Exception("You must specify module identifier")
		except:
			raise Exception("You must specify module identifier")
		if network_adapter is None:
			from cor.comm import CallbackNetworkAdapter
			self.network_adapter = CallbackNetworkAdapter(self)
		else:
			self.network_adapter = network_adapter
		print("Initializaing %s" % type(self).__name__)

	def add_topics(self, topics):
		self.consumes.update(topics)

	def messagein(self, message):
		if message.atype in self.consumes:
			self.consumes[message.atype](message)
		else:
			if "UNSOLICITED" in self.consumes:
				self.consumes["UNSOLICITED"](message)
		if "ANY" in self.consumes:
			self.consumes["ANY"](message)

	def messageout(self, message, sync=False, timeout=None):
		while self.network_adapter is None:
			time.sleep(0.01)
		self.network_adapter.message_out(message)


class Type:
	def __init__(self, name, subtypes=None):
		super().__init__()
		self.name = name
		self.extends = subtypes


class Message:
	def __init__(self, atype, payload):
		super().__init__()
		self.atype = atype
		self.payload = payload

	def __str__(self, *args, **kwargs):
		return "Type: %s, Payload: %s" % (self.atype, self.payload)
