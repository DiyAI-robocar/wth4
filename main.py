import requests
import time
from threading import Thread, Lock
import ast
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 2115


class WTH4:
	"""
	Class to update the map file
	"""

	def __init__(self):
		self.on = True
		self.map = None
		self.socket_data = None
		self.mutex = Lock()

	def initiate_map_update(self, path):
		self.github_file = path
		self.thread_map = Thread(target = self.start_map_update)
		self.thread_map.daemon = True
		self.thread_map.start()

	def start_map_update(self):
		while self.on:
			response = requests.get(self.github_file).text
			self.mutex.acquire()
			try:
				self.map = ast.literal_eval(response)
			finally:
				self.mutex.release()
			time.sleep(5)

	def initiate_socket(self):
		self.thread_socket = Thread(target=self.start_recvmsg)
		self.thread_socket.daemon = True

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((UDP_IP, UDP_PORT))
		self.sock.listen(1)
		self.sock.settimeout(2)

		self.thread_socket.start()

	def start_recvmsg(self):
		while self.on:
			try:
				self.sock.accept()
				self.socket_data = self.sock.recvmsg(1024)
				if self.socket_data != 0:
					coordinates = self.socket_data.split()
					road_points, building_points = self.match(coordinates[0], coordinates[1])
					data = dict()
					data["road"] = road_points
					data["buildings"] = building_points
					self.sock.sendto(bytes(data, "ascii"), (UDP_IP, UDP_PORT))
			except:
				print("Localisation service is not available")

	@staticmethod
	def distance(x1, y1, x2, y2):
		return pow((x1-x2), 2) + pow((y1-y2), 2)

	def match(self, longitude, latitude):
		result = []
		buildings = []

		if not self.map:
			return result

		self.mutex.acquire()
		try:
			for point in self.map.get("features").get("geometry").get("road_coordinates"):
				# 200 is the number that still need to validate!!!
				if self.distance(longitude, latitude, point[0], point[1]) <= 200:
					result.append(point)
			for building in self.map.get("features").get("geometry").get("building_coordinates"):
				# remove it or check
				if self.distance(longitude, latitude, building[0], building[1]) <= 300:
					buildings.append(building)

		finally:
			self.mutex.release()
			return result, buildings

	def shutdown(self):
		print ("Shutdown call...")
		self.on = False
		self.sock.close()
		self.thread_map.join()
		self.thread_socket.join()


if __name__ == "__main__":
	stuff = WTH4()
	stuff.initiate_map_update(path="https://raw.githubusercontent.com/nai1gun/robocar-map/master/map/track.geojson")
	stuff.initiate_socket()

	stuff.shutdown()

