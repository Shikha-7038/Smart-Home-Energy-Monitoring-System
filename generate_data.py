"""
Generate Data Files (CSV, SQLite, Daily Reports)
Run this file to create all data files
"""

import csv
import sqlite3
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

# Create folders
Path("data/raw_logs").mkdir(parents=True, exist_ok=True)
Path("data/daily_reports").mkdir(parents=True, exist_ok=True)

print("📊 Generating data files...")

# ============================================================
# 1. CSV FILE - Live Readings (60 seconds)
# ============================================================
csv_path = f"data/raw_logs/energy_log_{datetime.now().strftime('%Y%m%d')}.csv"

with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "voltage", "current", "power_w", "energy_wh", "cost_rs", "alert"])
    
    for i in range(60):
        timestamp = (datetime.now() - timedelta(seconds=60-i)).strftime("%Y-%m-%d %H:%M:%S")
        voltage = 230 + random.uniform(-5, 5)
        current = random.uniform(0.5, 5.0)
        power = voltage * current * 0.85
        energy = power / 3600
        cost = (energy / 1000) * 7.5
        alert = 1 if power > 1000 else 0
        
        writer.writerow([timestamp, round(voltage,1), round(current,2), 
                        round(power,1), round(energy,3), round(cost,4), alert])

print(f"   ✅ CSV: {csv_path}")

# ============================================================
# 2. CSV FILE - Historical Sample (24 hours)
# ============================================================
hist_path = "data/raw_logs/historical_sample_24h.csv"

with open(hist_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "voltage", "current", "power_w", "energy_wh", "cost_rs"])
    
    start = datetime.now() - timedelta(hours=24)
    for i in range(288):  # 5-minute intervals
        ts = start + timedelta(minutes=i*5)
        hour = ts.hour
        
        if 18 <= hour <= 22:
            current = random.uniform(4, 8)  # Peak hours
        elif 23 <= hour <= 5:
            current = random.uniform(0.3, 1)  # Night
        else:
            current = random.uniform(1.5, 3)  # Day
        
        voltage = 230 + current * 0.3
        power = voltage * current * 0.85
        energy = power * (5/60)
        cost = (energy / 1000) * 7.5
        
        writer.writerow([ts.strftime("%Y-%m-%d %H:%M:%S"), round(voltage,1), 
                        round(current,2), round(power,1), round(energy,3), round(cost,4)])

print(f"   ✅ CSV: {hist_path}")

# ============================================================
# 3. SQLITE DATABASE
# ============================================================
db_path = "data/energy_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        voltage REAL,
        current REAL,
        power_w REAL,
        energy_wh REAL,
        cost_rs REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_summary (
        id INTEGER PRIMARY KEY,
        date TEXT,
        total_energy_kwh REAL,
        total_cost_rs REAL
    )
''')

# Insert sample readings
for i in range(100):
    ts = (datetime.now() - timedelta(hours=2) + timedelta(seconds=i*72)).isoformat()
    current = random.uniform(0.5, 6)
    power = 230 * current * 0.85
    energy = power * (72/3600)
    cost = (energy / 1000) * 7.5
    
    cursor.execute("INSERT INTO readings (timestamp, voltage, current, power_w, energy_wh, cost_rs) VALUES (?, ?, ?, ?, ?, ?)",
                   (ts, 230, round(current,2), round(power,1), round(energy,3), round(cost,4)))

# Insert summary
cursor.execute("INSERT INTO daily_summary (date, total_energy_kwh, total_cost_rs) VALUES (?, ?, ?)",
               (datetime.now().strftime("%Y-%m-%d"), 12.5, 93.75))

conn.commit()
conn.close()
print(f"   ✅ SQLite: {db_path}")

# ============================================================
# 4. DAILY REPORT (JSON)
# ============================================================
json_path = f"data/daily_reports/summary_{datetime.now().strftime('%Y-%m-%d')}.json"

report = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "total_energy_kwh": 12.5,
    "total_cost_rs": 93.75,
    "peak_power_w": 1850,
    "alert_count": 8,
    "monthly_projection_kwh": 375,
    "monthly_projection_cost_rs": 2812.50
}

with open(json_path, 'w') as f:
    json.dump(report, f, indent=2)

print(f"   ✅ JSON: {json_path}")

# ============================================================
# 5. DAILY REPORT (TXT)
# ============================================================
txt_path = f"data/daily_reports/summary_{datetime.now().strftime('%Y-%m-%d')}.txt"

with open(txt_path, 'w') as f:
    f.write("="*40 + "\n")
    f.write("ENERGY SUMMARY\n")
    f.write("="*40 + "\n\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
    f.write(f"Total Energy: 12.5 kWh\n")
    f.write(f"Total Cost: Rs 93.75\n")
    f.write(f"Peak Power: 1850 W\n")
    f.write(f"Alerts: 8\n")

print(f"   ✅ TXT: {txt_path}")

print("\n✅ All data files generated successfully!")