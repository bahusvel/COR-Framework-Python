__author__ = 'denislavrov'
from api import CORModule, Message
import threading
import shlex


class CORShell(CORModule):

	def repl(self):
		while True:
			i = input("|>")
			if i == "exit":
				exit(0)
			elif i.upper().startswith("MESSAGE"):
				parts = shlex.split(i)
				if len(parts) < 2:
					print("Error %s is an incorrect message" % i)
					continue
				payload = {}
				for k, v in zip(parts[2::2], parts[3::2]):
					payload[k] = v
				message = Message(parts[1], payload)
				print(message)
				self.messageout(message)
			else:
				print("Error %s is an unknown command" % i)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		threading.Thread(target=self.repl).start()

CORShell(managerif="tcp://127.0.0.1:7777")
