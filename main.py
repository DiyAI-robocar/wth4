import requests
import time
from threading import Thread
import ast
import socket


class WTH4:
	"""
	Class to update the map file
	"""

	def __init__(self):
		self.on = True
		self.map = None

	def initiate_map_update(self, path):
		self.github_file = path
		self.thread = Thread(target = self.start_map_update)
		self.thread.daemon = True
		self.thread.start()

	def start_map_update(self):
		while self.on:
			response = requests.get(self.github_file).text
			self.map = ast.literal_eval(response)
			time.sleep(30)

	def initiate_socket(self):
		self.udp_ip = '127.0.0.1'
		self.udp_socket = 5005
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((self.udp_ip, self.udp_socket))
		self.data = None

	def start_recvmsg(self):
		while self.on:
			self.data = self.sock.recvmsg(1024)

	@staticmethod
	def distance(x1, y1, x2, y2):
		return pow((x1-x2), 2) + pow((y1-y2), 2)

	def match(self, longitude, latitude):
		if not self.map:
			return

		result = []
		for point in self.map.get("features").get("geometry").get("coordinates"):
			# 200 is the number that still need to validate!!!
			if self.distance(longitude, latitude, point[0], point[1]) <= 200:
				result.append(point)

		print(len(result))
		return result

	def shutdown(self):
		self.on = False
		self.sock.close()
		self.thread.join()


if __name__ == "__main__":
	stuff = WTH4
	stuff.initiate_map_update("https://raw.githubusercontent.com/nai1gun/robocar-map/master/map/track.geojson")
	stuff.start_map_update()

	stuff.initiate_socket()
	stuff.start_recvmsg()

