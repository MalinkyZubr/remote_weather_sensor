import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import datetime
import Adafruit_MCP9808.MCP9808 as MCP9808
import Adafruit_BMP.BMP085 as BMP085
import threading
import socket
import smbus
import json


class HumiditySensor:
    def __init__(self, pin):
        self.pin = pin
        self.sensor = Adafruit_DHT.DHT11
        
    def receive_humidity_data(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
        return humidity
        
class TemperatureSensor:
    def __init__(self):
        self.sensor = MCP9808.MCP9808()
        self.sensor.begin()
    
    def receive_temperature_data(self):
        temp = self.sensor.readTempC()
        return temp 

        
class PressureSensor:
    def __init__(self):
        self.sensor = BMP085.BMP085()
        
    def receive_pressure_data(self):
        pressure = self.sensor.read_pressure()
        return pressure
        
    def receive_altitude_data(self):
        altitude = self.sensor.read_altitude()
        return altitude
        
class SocketConnection:
    def __init__(self, IP, PORT):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((IP, PORT))
    
    def send_data(self, message):
        message = json.dumps(message)
        self.connection.send(message.encode('utf-8'))
        
        
class SuiteOperation:
    def __init__(self, humidity_pin=None):
        self.humidity_sensor = HumiditySensor(humidity_pin)
        self.temperature_sensor = TemperatureSensor()
        self.pressure_sensor = PressureSensor()
        self.socket_connection = SocketConnection("192.168.0.173", 2222)
        
    def sensor_operation(self):
        while True:
            humidity = self.humidity_sensor.receive_humidity_data()
            temperature = self.temperature_sensor.receive_temperature_data()
            pressure = self.pressure_sensor.receive_pressure_data()
            altitude = self.pressure_sensor.receive_altitude_data()
            raw_date = datetime.date.today()
            year, month, day, hour, minute, sec, day_of_week, day_of_year, d_saving_time = raw_date.timetuple()
            sys_time = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S")
            sys_date = f"{year}/{month}/{day}"
            suite_data = {"DATE":sys_date, "TIME UTC":sys_time, "HUMIDITY %":humidity, "TEMPERATURE Celsius":temperature, "PRESSURE Pascal":pressure, "ALTITUDE Meters":altitude}
            print(suite_data)
            self.socket_connection.send_data(suite_data)
            time.sleep(60)
            
    def main(self):
        sensor_thread = threading.Thread(target=self.sensor_operation)
        
        threads = [sensor_thread]
        
        for thread in threads:
            thread.start()
            
        
if __name__ == '__main__':
    operator = SuiteOperation(humidity_pin=4)
    operator.main()


