

class HTTPStatusException(Exception):
	""" Contains a message and HTTP status code. """
	def __init__(self, msg, http_status_code): # real signature unknown
		self.msg = msg
		self.http_status = http_status_code
