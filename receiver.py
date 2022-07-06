import socket
import json
import csv
import os

pwd = os.path.dirname(os.path.abspath(__file__))

class Receiver:
    def __init__(self, IP, PORT):
        self.weather_data = os.path.join(pwd, r'weather_data.csv')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((IP, PORT))
        self.sock.listen(1)
        self.conn, ip = self.sock.accept()

    def receive(self):
        message = ''
        while True:
            try:
                message += self.conn.recv(1024).decode('utf-8')
                return message
            except ValueError:
                continue

    def formatter(self, content):
        return tuple([value[1:-1] if value[0] == '"' and value[-1] == '"' else value for value in content])

    def format_sensor_data(self, data):
        data = data[1:-1].split(", ")
        data = list(map(lambda y: list(y.split(': ')), data))
        data = list(map(self.formatter, data))
        formatted_data = {element[0]:element[1] for element in data}
        return formatted_data

    def write_csv(self, dictionary):
        if not os.path.isfile(self.weather_data):
            with open(self.weather_data, 'a') as wd:
                fields = list(dictionary.keys())
                writer = csv.DictWriter(wd, fieldnames=fields)
                writer.writeheader()
                writer.writerow(dictionary)
        
        else:
            with open(self.weather_data, 'a') as wd:
                fields = list(dictionary.keys())
                writer = csv.DictWriter(wd, fieldnames=fields)
                writer.writerow(dictionary)
    

if __name__ == "__main__":
    receiver = Receiver("192.168.0.173", 2222)
    while True:
        message = receiver.receive()
        formatted_message = receiver.format_sensor_data(message)
        receiver.write_csv(formatted_message)
        print(message)