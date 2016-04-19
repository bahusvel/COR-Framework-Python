__author__ = 'denis'
import socket, threading, struct, time
from .protocol.message_pb2 import CORMessage

"""
If you want to port COR-Module to another language, you must implement everything in this file in your target language.
"""


class NetworkAdapter:

	def message_out(self, message):
		pass

	def set_module(self, module):
		self.module = module

	def __init__(self):
		super().__init__()
		self.module = None


class CallbackNetworkAdapter(NetworkAdapter):

	def handle(self, message):
		self.module.messagein(message)

	def message_out(self, message):
		super().message_out(message)
		if type(message).__name__ in self.callbacks:
			for callback in self.callbacks[type(message).__name__]:
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

	def __init__(self):
		super().__init__()
		self.callbacks = {}


class TCPSocketNetworkAdapter(NetworkAdapter):

	def message_out(self, message):
		message_type = type(message).__name__
		cormsg = CORMessage()
		cormsg.type = message_type
		cormsg.data = message.SerializeToString()
		if message_type in self.routes:
			sock = self.routes[message_type]
			cordata = cormsg.SerializeToString()
			corlength = struct.pack("I", len(cordata))
			sock.send(corlength)
			sock.send(cordata)
		else:
			print("Route not found")
			pass

	def register_link(self, atype, hostport):
		if hostport not in self.endpoints:
			aparts = hostport.split(":")
			client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client_socket.connect((aparts[0], int(aparts[1])))
			print("Connected to " + hostport)
			self.endpoints[hostport] = client_socket
			self.routes[atype] = client_socket
		else:
			self.routes[atype] = self.endpoints[hostport]

	def server_thread(self):
		self.server_socket.listen(10)
		while True:
			conn, addr = self.server_socket.accept()
			clientt = threading.Thread(target=self.client_thread, args=(conn,))
			clientt.start()

	def client_thread(self, conn):
		while True:
			lenbuf = conn.recv(4)
			if not lenbuf:
				time.sleep(0.0001)
				continue
			msglen = struct.unpack("I", lenbuf)[0]
			fullmessage = b""
			while len(fullmessage) < msglen:
				fullmessage += conn.recv(4096)
			cormsg = CORMessage()
			try:
				cormsg.ParseFromString(fullmessage)
				print("Received: " + cormsg.type)
			except Exception:
				print("Received a corrupt message")
				continue
			# type parse
			if cormsg.type in self.module.types:
				msg_instance = self.module.types[cormsg.type]()
				msg_instance.ParseFromString(cormsg.data)
				self.module.messagein(msg_instance)
			else:
				print("Type " + cormsg.type + " is not declared to be received")

	def __init__(self, hostport="127.0.0.1:6090"):
		super().__init__()
		self.endpoints = {}
		self.routes = {}
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		aparts = hostport.split(":")
		self.server_socket.bind((aparts[0], int(aparts[1])))
		self.sthread = threading.Thread(target=self.server_thread)
		self.sthread.start()

