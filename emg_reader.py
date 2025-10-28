import threading
from serial import Serial
from queue import Queue
from time import time
from statistics import fmean

VALUES_AVG_TIME = 0.5

class EMGReader(threading.Thread):
    def __init__(self, port, baudrate, data_queue: Queue):
        super().__init__()
        self.ser = Serial(port, baudrate, timeout=1)
        self.data_queue = data_queue

        self.last_time = time()
        self.temp_values = []

        self.running = True

    def run(self):
        while self.running:
            try:
                line = self.ser.readline().decode().strip()
                if line.isdigit():
                    line = int(line)
                    #print(line)
                    #if line > 0:
                    self.temp_values.append(int(line))
            except Exception as e:
                print("EMG Read Error:", e)
            finally:
                if time() - self.last_time >= VALUES_AVG_TIME:
                    self.data_queue.put_nowait(fmean(self.temp_values))
                    self.temp_values.clear()
                    self.last_time = time()

    def stop(self):
        self.running = False
        self.ser.close()