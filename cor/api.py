import sys
import threading

import cor.comm as comm
import cor.protocol.lifecycle_pb2 as lifecycle
import cor.protocol.log_pb2 as log

__author__ = 'denislavrov'

"""
If you want to port COR-Module to another language, you must implement everything in this file in your target language.
"""


class CORModule:
	def __init__(self, local_socket, bind_url):
		self.consumes = {}
		self.types = {}
		self.network_adapter = comm.NetworkAdapter(self, local_socket=local_socket, bind_url=bind_url)
		self.register_topic("Connection", lifecycle.Connection, self.on_connection_request)
		self.register_topic("ModuleStart", lifecycle.ModuleStart, self.on_start)
		self.register_topic("ModuleStop", lifecycle.ModuleStop, self.on_stop)
		self.register_topic("ModuleRecover", lifecycle.ModuleRecover, self.on_recover)
		self.register_topic("ModuleParameters", lifecycle.ModuleParameters, self.on_parameters_received)
		self.register_type("Log", log.Log)
		print("Initializaing %s" % type(self).__name__)

	def add_topic(self, type, callback):
		self.consumes[type] = callback

	def register_topic(self, type, type_class, callback):
		self.register_type(type, type_class)
		self.add_topic(type, callback)

	def on_parameters_received(self, message):
		pass

	def on_start(self, message):
		pass

	def on_stop(self, message):
		exit(0)

	def on_connection_request(self, message):
		self.network_adapter.register_link(message.type, message.corurl)

	def on_recover(self, message):
		self.on_start(message)

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
		self.network_adapter.message_out(message)

	# COR 5.0, direct message extension
	def direct_message(self, message, url):
		self.network_adapter.direct_message(message, url)

	def log(self, text, level="INFO"):
		log_message = log.Log()
		log_message.level = level
		log_message.text = text
		self.messageout(log_message)


# Call this in main method of the file, to launch a supervised module
def launch_module(module_class):
	local_socket = sys.argv[1]
	bind_url = sys.argv[2]

	def mod_loader():
		smodule_instance = module_class(local_socket, bind_url)
	module_thread = threading.Thread(target=mod_loader)
	module_thread.start()
