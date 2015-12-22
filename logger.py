__author__ = 'denis'
from cor.api import CORModule
import logging
import re

class ConsoleLogger(CORModule):

	def __init__(self, filters=[".*"], *args, **kwargs):
		super().__init__(**kwargs)
		print("Starting logger")
		self.filters = filters
		self.logger = logging.getLogger()
		self.logger.setLevel(logging.INFO)
		for handle in kwargs.pop("HANDLERS", [logging.FileHandler("cor.log"), logging.StreamHandler()]):
			self.logger.addHandler(handle)
		self.add_topics({"ALL": None})

	def messagein(self, message):
		super().messagein(message)
		for f in self.filters:
			if re.search(f, message.atype) is not None:
				self.logger.info(message)
				break
