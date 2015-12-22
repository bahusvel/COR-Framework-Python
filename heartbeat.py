__author__ = 'denis'
from cor.api import Message, CORModule
import threading
import time


class Heartbeat(CORModule):
	def snort(self):
		while True:
			time.sleep(self.period)
			self.messageout(Message("HEARTBEAT", {"timestamp": time.clock()}))

	def rx_heartbeat(self, message):
		print("Received heartbeat from: " + message.source)

	def __init__(self, period=10, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.period = period
		self.add_topics({"HEARTBEAT": self.rx_heartbeat})
		self.subtree = []
		self.t = threading.Thread(target=self.snort)
		self.t.start()
		print("Initializing Heartbeat " + str(self.mid))
