from json import load, dump
from datetime import datetime

class Measurement:
    def __init__(self, date, arm, value, mvc, ai) -> None:
        self.arm = arm
        self.timestamp = date
        self.value = value
        self.mvc = mvc
        self.ai = ai


class UserNotExist(Exception):
    pass

class Database:
    def __init__(self, filename) -> None:
        self.filename = filename
        try:
            with open(filename, "r+") as file:
                self.data = load(file)
        except:
            self.data = {}
    
    def get_user_measurements(self, username):
        if not self.check_user_exists(username):
            return []
        return [Measurement(d["timestamp"], d["arm"], d["value"], d["mvc"], d["ai"]) for d in self.data[username]["measurements"]]
    
    def add_user(self, username, mvc, initial):
        if username in self.data:
            return
        self.data[username] = {
            "mvc": int(mvc),
            "initial": int(initial),
            "measurements": []
        }
        with open(self.filename, "w+") as file:
            dump(self.data, file)
    
    def add_user_measurement(self, username, number, arm):
        if username not in self.data:
            return
        now = datetime.now().replace(second=0, microsecond=0)
        self.data[username]["measurements"].append({
            "timestamp": now.isoformat(sep=" ", timespec="minutes"),
            "value": int(number),
            "mvc": (int(number) / self.data[username]["mvc"]) * 100,
            "ai": int((abs(int(number) - self.data[username]["initial"]) / max(int(number), self.data[username]["initial"])) * 100),
            "arm": arm
        })
        with open(self.filename, "w+") as file:
            dump(self.data, file)
    
    def check_user_exists(self, username):
        return username in self.data