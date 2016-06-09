import socket
import threading
import struct
import time
import os
import cor.protocol.message_pb2 as message

__author__ = 'denis'

"""
If you want to port COR-Module to another language, you must implement everything in this file in your target language.
"""


class NetworkAdapter:

	def message_out(self, message):
		message_type = type(message).__name__
		cormsg = message.CORMessage()
		cormsg.type = message_type
		cormsg.data = message.SerializeToString()
		if message_type in self.routes:
			sock = self.endpoints[self.routes[message_type]]
			cordata = cormsg.SerializeToString()
			corlength = struct.pack(">I", len(cordata))
			try:
				sock.send(corlength+cordata)
			except Exception:
				print("Unable to send message, attempting to reconnect")
				self._connect(self.routes[message_type])
				self.message_out(message)
		else:
			print("Route not found")
			print(self.routes)
			pass

	# COR 5.0, direct message extension
	def direct_message(self, message, url):
		message_type = type(message).__name__
		cormsg = message.CORMessage()
		cormsg.type = message_type
		cormsg.data = message.SerializeToString()
		sock = self.endpoints[url]
		cordata = cormsg.SerializeToString()
		corlength = struct.pack(">I", len(cordata))
		try:
			sock.send(corlength+cordata)
		except Exception:
			print("Unable to send direct message")

	def _connect(self, url):
		if url.startswith("sock://"):
			aparts = url[len("sock://"):]
			if url in self.endpoints:
				self.endpoints[url].close()
			while True:
				try:
					sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
					sock.connect((aparts))
					self.endpoints[url] = sock
					print("Connected to " + url)
					break
				except Exception as e:
					print(e)
					print("Connection to %s failed retrying" % url)
					time.sleep(1)
		elif url.startswith("tcp://"):
			aparts = url[len("tcp://"):].split(":")
			if url in self.endpoints:
				self.endpoints[url].close()
			while True:
				try:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((aparts[0], int(aparts[1])))
					if self.nodelay:
						# Disables Nagle's Algorithm to reduce latency
						sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
					self.endpoints[url] = sock
					print("Connected to " + url)
					break
				except Exception as e:
					print(e)
					print("Connection to %s failed retrying" % url)
					time.sleep(1)
		else:
			raise Exception("Unknown url type specified")

	def register_link(self, atype, hostport):
		if hostport not in self.endpoints:
			self._connect(hostport)
		self.routes[atype] = hostport

	def server_thread(self, socket):
		socket.listen(10)
		while True:
			conn, addr = socket.accept()
			clientt = threading.Thread(target=self.client_thread, args=(conn,))
			clientt.start()

	def client_thread(self, conn):
		while True:
			lenbuf = conn.recv(4)
			if not lenbuf:
				time.sleep(0.0001)
				continue
			msglen = struct.unpack(">I", lenbuf)[0]
			fullmessage = b""
			while len(fullmessage) < msglen:
				rcv_buf_size = 8192 if (msglen - len(fullmessage)) > 8192 else (msglen - len(fullmessage))
				fullmessage += conn.recv(rcv_buf_size)
			cormsg = message.CORMessage()
			try:
				cormsg.ParseFromString(fullmessage)
				#print("Received: " + cormsg.type)
			except Exception:
				print("Received a corrupt message, reseting connection")
				conn.close()
				return
			# type parse
			if cormsg.type in self.module.types:
				msg_instance = self.module.types[cormsg.type]()
				msg_instance.ParseFromString(cormsg.data)
				self.module.messagein(msg_instance)
			else:
				print("Type " + cormsg.type + " is not declared to be received")

	def __init__(self, module, local_socket="", bind_url="127.0.0.1:6090", nodelay=True):
		super().__init__()
		self.nodelay = nodelay
		self.endpoints = {}
		self.module = module
		self.routes = {}
		# tcp socket
		self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# allow to reuse the address (in case of server crash and quick restart)
		self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		aparts = bind_url.split(":")
		self.tcp_socket.bind((aparts[0], int(aparts[1])))
		self.tcp_thread = threading.Thread(target=self.server_thread, args=[self.tcp_socket])
		self.tcp_thread.start()

		# domain socket
		self.domain_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		try:
			os.unlink(local_socket)
		except FileNotFoundError:
			pass
		self.domain_socket.bind((local_socket))
		self.domain_thread = threading.Thread(target=self.server_thread, args=[self.domain_socket])
		self.domain_thread.start()



