"""
Data Logger - Handles CSV, JSON, and SQLite logging
Saves all sensor readings and calculations
"""

import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DataLogger:
    """
    Logs energy data to multiple formats: CSV, JSON, SQLite
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data logger
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir)
        self.raw_logs_dir = self.data_dir / "raw_logs"
        self.daily_reports_dir = self.data_dir / "daily_reports"
        
        # Create directories
        self.raw_logs_dir.mkdir(parents=True, exist_ok=True)
        self.daily_reports_dir.mkdir(parents=True, exist_ok=True)
        
        # SQLite database path
        self.db_path = self.data_dir / "energy_data.db"
        
        # Initialize SQLite database
        self._init_database()
        
        # Current CSV file
        self.current_csv_path = None
        self.csv_writer = None
        self.csv_file = None
        
    def _init_database(self) -> None:
        """Initialize SQLite database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                voltage REAL,
                current REAL,
                power_factor REAL,
                power_w REAL,
                energy_wh REAL,
                cost_rs REAL,
                alert_triggered INTEGER,
                temperature REAL,
                frequency REAL
            )
        ''')
        
        # Create daily_summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                total_energy_kwh REAL,
                total_cost_rs REAL,
                peak_power_w REAL,
                avg_power_w REAL,
                alert_count INTEGER,
                peak_hours_usage_kwh REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ SQLite database initialized: {self.db_path}")
    
    def _get_csv_filename(self) -> Path:
        """Get CSV filename for current date"""
        today = datetime.now().strftime("%Y%m%d")
        return self.raw_logs_dir / f"energy_log_{today}.csv"
    
    def _ensure_csv_file(self) -> None:
        """Ensure CSV file exists with headers"""
        target_path = self._get_csv_filename()
        
        # Check if we need to create a new file
        if self.current_csv_path != target_path:
            # Close previous file if open
            if self.csv_file:
                self.csv_file.close()
            
            self.current_csv_path = target_path
            file_exists = self.current_csv_path.exists()
            
            self.csv_file = open(self.current_csv_path, 'a', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            
            # Write header if new file
            if not file_exists:
                self.csv_writer.writerow([
                    "timestamp", "voltage", "current", "power_factor",
                    "power_w", "energy_wh", "cost_rs", "alert_triggered",
                    "temperature", "frequency", "simulation_progress"
                ])
    
    def log_reading(self, sensor_data: Dict, power_data: Dict, 
                    energy_data: Dict, alert_triggered: bool = False,
                    simulation_progress: float = 0) -> None:
        """
        Log a single reading to all storage backends
        
        Args:
            sensor_data: Data from sensor simulator
            power_data: Data from energy calculator
            energy_data: Energy and cost data
            alert_triggered: Whether an alert was triggered
            simulation_progress: Progress of current simulation (0-1)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log to CSV
        self._ensure_csv_file()
        self.csv_writer.writerow([
            timestamp,
            sensor_data.get("voltage", 0),
            sensor_data.get("current", 0),
            sensor_data.get("power_factor", 1),
            power_data.get("real_power_w", 0),
            energy_data.get("energy_wh_this_interval", 0),
            energy_data.get("cost_rs_this_interval", 0),
            1 if alert_triggered else 0,
            sensor_data.get("temperature", 25),
            sensor_data.get("frequency", 50),
            simulation_progress
        ])
        self.csv_file.flush()  # Ensure data is written
        
        # Log to SQLite
        self._log_to_sqlite(
            timestamp, sensor_data, power_data, energy_data, alert_triggered
        )
    
    def _log_to_sqlite(self, timestamp: str, sensor_data: Dict,
                       power_data: Dict, energy_data: Dict,
                       alert_triggered: bool) -> None:
        """Log reading to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO readings (
                timestamp, voltage, current, power_factor, power_w,
                energy_wh, cost_rs, alert_triggered, temperature, frequency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            sensor_data.get("voltage", 0),
            sensor_data.get("current", 0),
            sensor_data.get("power_factor", 1),
            power_data.get("real_power_w", 0),
            energy_data.get("energy_wh_this_interval", 0),
            energy_data.get("cost_rs_this_interval", 0),
            1 if alert_triggered else 0,
            sensor_data.get("temperature", 25),
            sensor_data.get("frequency", 50)
        ))
        
        conn.commit()
        conn.close()
    
    def save_daily_summary(self, date: str, summary: Dict) -> None:
        """
        Save daily summary to SQLite
        
        Args:
            date: Date string (YYYY-MM-DD)
            summary: Daily summary dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_summary (
                date, total_energy_kwh, total_cost_rs, peak_power_w,
                avg_power_w, alert_count, peak_hours_usage_kwh
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            date,
            summary.get("total_energy_kwh", 0),
            summary.get("total_cost_rs", 0),
            summary.get("peak_power_w", 0),
            summary.get("avg_power_w", 0),
            summary.get("alert_count", 0),
            summary.get("peak_hours_usage_kwh", 0)
        ))
        
        conn.commit()
        conn.close()
        
        # Also save as JSON
        json_path = self.daily_reports_dir / f"summary_{date}.json"
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def get_readings(self, limit: int = 100, start_date: str = None,
                     end_date: str = None) -> List[Dict]:
        """
        Retrieve readings from SQLite
        
        Args:
            limit: Maximum number of readings
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            
        Returns:
            List of reading dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM readings"
        params = []
        
        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append("date(timestamp) >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date(timestamp) <= ?")
                params.append(end_date)
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_daily_summaries(self, limit: int = 30) -> List[Dict]:
        """
        Get daily summaries from SQLite
        
        Args:
            limit: Maximum number of summaries
            
        Returns:
            List of summary dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM daily_summary 
            ORDER BY date DESC LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def export_to_json(self, output_path: str = None) -> str:
        """
        Export all readings to JSON file
        
        Args:
            output_path: Path for JSON file (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.data_dir / f"export_{timestamp}.json"
        
        readings = self.get_readings(limit=10000)  # Get all
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_readings": len(readings),
            "readings": readings
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return str(output_path)
    
    def cleanup_old_files(self, days_to_keep: int = 30) -> int:
        """
        Delete old CSV and JSON files
        
        Args:
            days_to_keep: Number of days to keep
            
        Returns:
            Number of files deleted
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        # Clean CSV files
        for csv_file in self.raw_logs_dir.glob("energy_log_*.csv"):
            file_date_str = csv_file.stem.replace("energy_log_", "")
            try:
                file_date = datetime.strptime(file_date_str, "%Y%m%d")
                if file_date < cutoff_date:
                    csv_file.unlink()
                    deleted_count += 1
            except ValueError:
                pass
        
        # Clean JSON exports
        for json_file in self.data_dir.glob("export_*.json"):
            if json_file.stat().st_mtime < cutoff_date.timestamp():
                json_file.unlink()
                deleted_count += 1
        
        return deleted_count
    
    def close(self) -> None:
        """Close all open file handles"""
        if self.csv_file:
            self.csv_file.close()
    
    def get_todays_csv_path(self) -> str:
        """Get path to today's CSV file"""
        return str(self._get_csv_filename())


# For direct testing
if __name__ == "__main__":
    logger = DataLogger()
    
    print("💾 Testing Data Logger...\n")
    
    # Test logging
    test_sensor = {"voltage": 230, "current": 2.5, "power_factor": 0.85, 
                   "temperature": 35, "frequency": 50}
    test_power = {"real_power_w": 488.75}
    test_energy = {"energy_wh_this_interval": 0.136, "cost_rs_this_interval": 1.02}
    
    logger.log_reading(test_sensor, test_power, test_energy, alert_triggered=False)
    
    # Get readings
    readings = logger.get_readings(limit=5)
    print(f"Retrieved {len(readings)} readings")
    
    print(f"Today's CSV: {logger.get_todays_csv_path()}")