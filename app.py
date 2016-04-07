import threading

import time

from cor.api import CORModule
from test_pb2 import Request, Reply


class Requester(CORModule):

	def acknowledge(self, message):
		print(message.data)

	def request_worker(self):
		while True:
			request = Request()
			request.data = "Hello"
			self.messageout(request)

	def __init__(self, network_adapter=None, *args, **kwargs):
		super().__init__(network_adapter, *args, **kwargs)
		self.add_topic("Reply", self.acknowledge)
		t = threading.Thread(target=self.request_worker)
		t.start()


class Responder(CORModule):

	def respond(self, message):
		print(message.data)
		reply = Reply()
		reply.data = "Hi"
		self.messageout(reply)

	def __init__(self, network_adapter=None, *args, **kwargs):
		super().__init__(network_adapter, *args, **kwargs)
		self.add_topic("Request", self.respond)


requester = Requester()
responder = Responder()
requester.network_adapter.register_callback("Request", responder)
responder.network_adapter.register_callback("Reply", requester)

while True:
	time.sleep(100)
