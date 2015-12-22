__author__ = 'denis'

import socket
import os
import msgpack
import threading
import time
import cor.api


def dst_router_factory(default_route):
	def dst_router(message):
		if len(message.destination) == 0:
			return [default_route]
		else:
			return [message.destination[-1]]
	return dst_router


def static_router_factory(routes):
	def static_route(message):
		if message.atype in routes:
			return [routes[message.atype].mid]
		else:
			return [None]
	return static_route


class NetworkAdapter:

	def poller_worker(self):
		pass

	def message_out(self, message):
		pass

	def start(self):
		self.pollert.start()

	def __init__(self, module, route_callback=dst_router_factory("manager")):
		super().__init__()
		self.module = module
		self.message_callback = module.messagein
		self.route_callback = route_callback
		self.pollert = threading.Thread(target=self.poller_worker)


class CallbackNetworkAdapter(NetworkAdapter):

	callback_autotable = {}

	def message_out(self, message):
		super().message_out(message)
		dsts = self.route_callback(message)
		for dst in dsts:
			if dst in self.callbacks:
				self.callbacks[dst](message)
			elif dst in CallbackNetworkAdapter.callback_autotable:
				CallbackNetworkAdapter.callback_autotable[dst](message)
			else:
				print("Did not deliver %s, destination %s is unknown" % (str(message), str(dst)))

	def register_callback(self, module):
		self.callbacks[module.mid] = module.messagein

	def __init__(self, module, route_callback=dst_router_factory("manager")):
		super().__init__(module, route_callback)
		self.callbacks = {}
		CallbackNetworkAdapter.callback_autotable[module.mid] = module.messagein


class SocketModuleNetworkAdapter(NetworkAdapter):

	def __init__(self, module, url):
		super().__init__(module)
		self.url = url
		self.connected = False
		self.socket = self.createSocket(url)

	def createSocket(self, url):
		parts = str(url).split("://")
		if parts[0] == "unixsock":
			family = socket.AF_UNIX
			type = socket.SOCK_STREAM
		elif parts[0] == "tcp":
			family = socket.AF_INET
			type = socket.SOCK_STREAM
		else:
			raise ValueError("UNSUPPORTED SOCKET TYPE " + url)

		sock = socket.socket(family, type)
		return sock

	def connect_to_manager(self, managerif):
		parts = str(managerif).split("://")
		aparts = parts[1].split(":")
		if len(aparts) == 2:
			self.socket.connect((aparts[0], int(aparts[1])))
		elif len(aparts) == 1:
			self.socket.connect(aparts[0])
		self.connected = True

	def message_out(self, message):
		super().message_out(message)
		if not self.connected:
			print("Dropping Message, Socket not connected")
			return

		self.socket.send(msgpack.packb(message.__dict__, use_bin_type=True))

	def poller_worker(self):
		super().poller_worker()
		unpacker = msgpack.Unpacker(encoding="UTF-8")
		while True:
			if not self.connected:
				time.sleep(0.0001)
				continue
			buf = self.socket.recv(4096)
			if not buf:
				time.sleep(0.0001)
				continue
			unpacker.feed(buf)
			for unpacked in unpacker:
				msg = cor.api.Message(None, None)
				msg.__dict__.update(unpacked)
				self.message_callback(msg)


class SocketManagerNetworkAdapter(NetworkAdapter):

	@staticmethod
	def ipid(addrlist):
		ipid = b""
		for addr in addrlist:
			ipid += addr
		return ipid

	def client_thread(self, conn):

		unpacker = msgpack.Unpacker(encoding="UTF-8")
		while True:
			buf = conn.recv(4096)
			if not buf:
				time.sleep(0.0001)
				continue
			unpacker.feed(buf)
			for unpacked in unpacker:
				msg = cor.api.Message(None, None)
				msg.__dict__.update(unpacked)
				self.clients[SocketManagerNetworkAdapter.ipid(msg.source)] = conn
				#print("Manager Received: " + str(msg))
				self.message_callback(msg)

	@staticmethod
	def createSocket(url):
		parts = str(url).split("://")
		if parts[0] == "unixsock":
			family = socket.AF_UNIX
			type = socket.SOCK_STREAM
			addr = parts[1]
			try:
				os.unlink(addr)
			except:
				pass
		elif parts[0] == "tcp":
			family = socket.AF_INET
			type = socket.SOCK_STREAM
			aparts = parts[1].split(":")
			addr = (aparts[0], int(aparts[1]))
		else:
			raise ValueError("UNSUPPORTED SOCKET TYPE " + url)

		sock = socket.socket(family, type)
		sock.bind(addr)
		return sock

	def __init__(self, message_callback, url):
		super().__init__(message_callback)
		self.sock = SocketManagerNetworkAdapter.createSocket(url)
		self.clients = {}

	def poller_worker(self):
		super().poller_worker()
		self.sock.listen(10)
		while True:
			conn, addr = self.sock.accept()
			clientt = threading.Thread(target=self.client_thread, args=(conn,))
			clientt.start()

	def message_out(self, message):
		super().message_out(message)
		try:
			sock = self.clients[SocketManagerNetworkAdapter.ipid(message.destination)]
			#print("Manager Sent: " + str(message))
			sock.send(msgpack.packb(message.__dict__, use_bin_type=True))
		except KeyError:
			print("Could not find recipient for the message")

