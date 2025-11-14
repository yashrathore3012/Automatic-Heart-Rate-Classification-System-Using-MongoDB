import mysql.connector
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from datetime import datetime





# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root12',         
    'password': '123456789',  
    'database': 'ecglog'
}

# --- CONNECT TO DATABASE ---
def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

# --- INSERT PATIENT ---
def insert_patient(name, age, gender):
    cnx = connect_db()
    cur = cnx.cursor()
    cur.execute("INSERT INTO patients (name, age, gender) VALUES ('yash', 20, 'male')", (name, age, gender))
    cnx.commit()
    pid = cur.lastrowid
    cnx.close()
    return pid

# --- INSERT ECG RECORD ---
def insert_ecg_record(patient_id, fs, samples):
    cnx = connect_db()
    cur = cnx.cursor()
    cur.execute(
        "INSERT INTO ecg_records (patient_id, record_time, sampling_rate, samples) VALUES (%s, %s, %s, %s)",
        (patient_id, datetime.now(), fs, ",".join(map(str, samples)))
    )
    cnx.commit()
    rid = cur.lastrowid
    cnx.close()
    return rid

# --- COMPUTE METRICS ---
def compute_metrics(signal, fs):
    # R-peak detection
    peaks, _ = find_peaks(signal, distance=int(0.3*fs), height=np.mean(signal) + 0.2*np.std(signal))
    if len(peaks) < 2:
        return {'mean_hr': 0, 'rr_mean': 0, 'sdnn': 0, 'arrhythmia_flag': 1, 'notes': 'No clear R-peaks detected'}

    rr_intervals = np.diff(peaks) / fs
    rr_mean = np.mean(rr_intervals)
    sdnn = np.std(rr_intervals) * 1000  # in ms
    hr = 60 / rr_mean

    # Check abnormality
    if hr < 50:
        flag, note = 1, f'Bradycardia detected (HR={hr:.1f} bpm)'
    elif hr > 110:
        flag, note = 1, f'Tachycardia detected (HR={hr:.1f} bpm)'
    elif sdnn < 20:
        flag, note = 1, f'Low HRV (SDNN={sdnn:.1f} ms)'
    else:
        flag, note = 0, 'Normal rhythm'

    return {'mean_hr': hr, 'rr_mean': rr_mean, 'sdnn': sdnn, 'arrhythmia_flag': flag, 'notes': note}

# --- STORE METRICS ---
def insert_metrics(record_id, metrics):
    cnx = connect_db()
    cur = cnx.cursor()
    cur.execute(
        "INSERT INTO ecg_metrics (record_id, mean_hr, rr_mean, sdnn, arrhythmia_flag, notes) VALUES (%s,%s,%s,%s,%s,%s)",
        (record_id, metrics['mean_hr'], metrics['rr_mean'], metrics['sdnn'], metrics['arrhythmia_flag'], metrics['notes'])
    )
    cnx.commit()
    cnx.close()

# --- SYNTHETIC ECG GENERATOR ---
def synthetic_ecg(duration_s=10, fs=250, hr_bpm=75):
    t = np.arange(0, duration_s, 1/fs)
    rr = 60/hr_bpm
    peaks = np.arange(0, duration_s, rr)
    signal = np.zeros_like(t)
    for p in peaks:
        signal += np.exp(-((t-p)**2)/(2*(0.01**2))) * 1.0
    signal += 0.01*np.random.randn(len(t))
    return signal

# --- MAIN FLOW ---
if __name__ == "__main__":
    print("=== ECG DATA LOGGER & ANALYZER ===")
    patient_id = insert_patient("Test Patient", 25, "M")
    fs = 250
    ecg_signal = synthetic_ecg(duration_s=30, fs=fs, hr_bpm=80)
    record_id = insert_ecg_record(patient_id, fs, ecg_signal)
    metrics = compute_metrics(ecg_signal, fs)
    insert_metrics(record_id, metrics)
    print(f"Patient ID: {patient_id}, Record ID: {record_id}")
    print(f"Metrics: HR={metrics['mean_hr']:.2f} bpm, SDNN={metrics['sdnn']:.2f} ms")
    print(f"Status: {metrics['notes']}")
