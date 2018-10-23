import time
from threading import Thread
import socket
import os 
import json
import math

UDP_IP = "127.0.0.1"
UDP_PORT = 2115
UDP_PORT_SEND = 2116


class WTH4:
    """
    Class to update the map file
    """

    def __init__(self):
        self.on = True
        self.map = None
        self.socket_data = None

    def initiate_map_update(self):
        self.thread_map = Thread(target=self.start_map_update)
        self.thread_map.daemon = True
        self.thread_map.start()

    def start_map_update(self):
        while self.on:
            with open('map.json') as f:
                self.map = json.load(f)
            time.sleep(30)

    def initiate_socket(self):
        self.thread_socket = Thread(target=self.start_recvmsg)
        self.thread_socket.daemon = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))

        self.sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.thread_socket.start()

    def start_recvmsg(self):
        while self.on:
            self.socket_data = self.sock.recvmsg(1024)
            if self.socket_data != 0:
                coordinates = self.socket_data[0].split()
                coordinates = [float(coordinates[0]),float(coordinates[1])]
                road_points, building_points = self.match(
                    coordinates[0], coordinates[1])
                data = dict()
                data["road"] = road_points
                data["buildings"] = building_points
                self.sock_send.sendto(bytes(json.dumps(data), "ascii"), (UDP_IP, UDP_PORT_SEND))

    @staticmethod
    def distance(x1, y1, x2, y2):
        return math.sqrt(pow((x1-x2), 2) + pow((y1-y2), 2))

    def match(self, longitude, latitude):
        result = []
        buildings = []

        if not self.map:
            return result

        for point in self.map.get("features")[0].get("geometry").get("road_coordinates"):
            if self.distance(longitude, latitude, point[0], point[1]) <= 400:
                result.append(point)
        for building in self.map.get("features")[0].get("geometry").get("building_coordinates"):
            if self.distance(longitude, latitude, building[0], building[1]) <= 500:
                buildings.append(building)

        return result, buildings

    def shutdown(self):
        self.on = False
        self.sock.close()
        self.thread_map.join()
        self.thread_socket.join()


if __name__ == "__main__":
    stuff = WTH4()
    stuff.initiate_map_update()
    stuff.initiate_socket()
    os.system('read x "Press any key to continue..."')
