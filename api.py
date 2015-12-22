import time

__author__ = 'denislavrov'
import random
import struct
import cor.comm
"""
If you want to port COR-Module to another language, you must implement everything in this module in the language.

"""


def id_generator():
	# Generates random 32bit integer
	return struct.pack(">I", random.randint(0, 2147483647))


class CORModule:

	def __init__(self, network_adapter=cor.comm.CallbackNetworkAdapter, mid=None, *args, **kwargs):
		if mid is None:
			mid = id_generator()
		self.mid = mid
		self.produces = []
		self.consumes = {}
		self.network_adapter = network_adapter(self, **kwargs)
		print("Initializaing %s %s" % (type(self).__name__, self.mid))

	def add_topics(self, topics):
		self.consumes.update(topics)
		ta = Message("TOPIC_ADVERTISEMENT", {"consumes": list(topics.keys())})
		self.messageout(ta)

	def messagein(self, message):
		if message.atype in self.consumes:
			self.consumes[message.atype](message)

	def messageout(self, message, sync=False, timeout=None):
		while self.network_adapter is None:
			time.sleep(0.01)
		message.source.append(self.mid)
		self.network_adapter.message_out(message)


class Message:
	def __init__(self, atype, payload):
		super().__init__()
		self.source = []
		self.destination = []
		self.atype = atype
		self.number = random.SystemRandom().randint(0, 2147483647)
		self.payload = payload

	def src_ipid(self):
		return b''.join(self.source)

	def dst_ipid(self):
		return b''.join(self.destination)

	def src_from(self, ipid):
		tmp = []
		for i in range(0, len(ipid), 8):
			tmp.append(ipid[i:i+8])
		self.source = tmp

	def dst_from(self, ipid):
		tmp = []
		for i in range(0, len(ipid), 8):
			tmp.append(ipid[i:i+8])
		self.destination = tmp

	def __str__(self, *args, **kwargs):
		return "Type: %s, Source: %s, Destination: %s, Message Number: %s, Payload: %s" % (
			self.atype, self.source, self.destination, self.number, self.payload)
