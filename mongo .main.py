from pymongo import MongoClient
import numpy as np
from datetime import datetime



client = MongoClient("mongodb://localhost:27017/")
db = client["ecg"]  
records = db["ecg"]  

print(" Connected to MongoDB successfully!")

ecg_values = [0.1, 0.2, 0.9, 0.3, 0.1, 0.8, 0.2, 0.9, 0.4, 0.1, 0.95, 0.3, 0.2, 0.85, 0.25, 0.9, 0.35, 0.1, 0.8, 0.3]


record = {
    "patient_name": "ghgh",
    "age":95,
    "time": datetime.now(),
    "ecg_signal": ecg_values
}
records.insert_one(record)
print(" ECG data stored successfully!")

heartbeats = len([v for v in ecg_values if v > 0.8])
duration_in_seconds = 10  
heart_rate = (heartbeats / duration_in_seconds) * 120
print(f" Detected Heart Rate: {heart_rate:.1f} bpm")


if heart_rate < 60:
    alert = " Low Heart Rate! (Bradycardia)"
elif heart_rate > 100:
    alert = " High Heart Rate! (Tachycardia)"
else:
    alert = " Normal Heart Rate"


alert_record = {
    "patient_name": "Test Patient",
    "alert_message": alert,
    "heart_rate": heart_rate,
    "time": datetime.now()
}
db.alerts.insert_one(alert_record)

print(alert)
print("Alert info saved in MongoDB!")

