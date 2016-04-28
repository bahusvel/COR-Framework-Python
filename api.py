import time
import threading
import json
import sys
import os

__author__ = 'denislavrov'

"""
If you want to port COR-Module to another language, you must implement everything in this file in your target language.
"""


class CORModule:
	def __init__(self, network_adapter=None, *args, **kwargs):
		self.consumes = {}
		self.types = {}
		if network_adapter is None:
			from .comm import CallbackNetworkAdapter
			self.network_adapter = CallbackNetworkAdapter()
		else:
			self.network_adapter = network_adapter
		network_adapter.module = self
		print("Initializaing %s" % type(self).__name__)

	def add_topic(self, type, callback):
		self.consumes[type] = callback

	def register_type(self, type, type_class):
		self.types[type] = type_class

	def messagein(self, message):
		if type(message).__name__ in self.consumes:
			self.consumes[type(message).__name__](message)
		else:
			if "UNSOLICITED" in self.consumes:
				self.consumes["UNSOLICITED"](message)
		if "ANY" in self.consumes:
			self.consumes["ANY"](message)

	def messageout(self, message):
		while self.network_adapter is None:
			time.sleep(0.01)
		self.network_adapter.message_out(message)


class Launcher:
	def __init__(self):
		super().__init__()
		self.module_thread = None
		self.module_instance = None

	def launch_module(self, module_class, *mod_args, **mod_kwargs):
		def mod_loader():
			self.module_instance = module_class(*mod_args, **mod_kwargs)

		self.module_thread = threading.Thread(target=mod_loader)
		self.module_thread.start()

	def wait_for_instance(self):
		while self.module_instance is None:
			time.sleep(0.5)

	def link_internal(self, messagetype, other_loader):
		self.wait_for_instance()
		other_loader.wait_for_instance()
		self.module_instance.network_adapter.register_callback(messagetype, other_loader.module_instance)

	def link_external(self, messagetype, hostport):
		self.wait_for_instance()
		network_adapter = self.module_instance.network_adapter
		if type(network_adapter).__name__ == "TCPSocketNetworkAdapter":
			network_adapter.register_link(messagetype, hostport)
		else:
			print("Can Not Link")
