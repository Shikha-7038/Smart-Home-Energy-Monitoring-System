"""
Report Generator - Creates PDF reports from energy data
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from fpdf import FPDF
import pandas as pd

# Fix: Use relative import
from src.data_logger import DataLogger


class EnergyReportGenerator:
    """
    Generates PDF reports for energy consumption
    """
    
    def __init__(self, output_dir: str = "outputs/reports"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = DataLogger()
    
    def _get_daily_data(self, date: str = None) -> pd.DataFrame:
        """
        Get data for a specific date
        
        Args:
            date: Date string (YYYY-MM-DD), None for today
            
        Returns:
            DataFrame with readings
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        readings = self.logger.get_readings(
            start_date=date,
            end_date=date,
            limit=10000
        )
        
        if readings:
            df = pd.DataFrame(readings)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        
        return pd.DataFrame()
    
    def _get_monthly_data(self, year: int = None, month: int = None) -> pd.DataFrame:
        """
        Get data for a specific month
        
        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
            
        Returns:
            DataFrame with readings
        """
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        
        start_date = f"{year}-{month:02d}-01"
        
        # Calculate end date
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        readings = self.logger.get_readings(
            start_date=start_date,
            end_date=end_date,
            limit=100000
        )
        
        if readings:
            df = pd.DataFrame(readings)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        
        return pd.DataFrame()
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate statistics from DataFrame
        
        Args:
            df: DataFrame with readings
            
        Returns:
            Dictionary of statistics
        """
        if df.empty:
            return {}
        
        # Handle different column names
        energy_col = 'energy_wh' if 'energy_wh' in df.columns else 'energy_wh_this_interval'
        cost_col = 'cost_rs' if 'cost_rs' in df.columns else 'cost_rs_this_interval'
        power_col = 'power_w' if 'power_w' in df.columns else 'real_power_w'
        
        return {
            "total_energy_kwh": df[energy_col].sum() / 1000 if energy_col in df.columns else 0,
            "total_cost_rs": df[cost_col].sum() if cost_col in df.columns else 0,
            "peak_power_w": df[power_col].max() if power_col in df.columns else 0,
            "avg_power_w": df[power_col].mean() if power_col in df.columns else 0,
            "avg_voltage": df['voltage'].mean() if 'voltage' in df.columns else 0,
            "avg_current": df['current'].mean() if 'current' in df.columns else 0,
            "alert_count": df['alert_triggered'].sum() if 'alert_triggered' in df.columns else 0,
            "num_readings": len(df)
        }
    
    def generate_daily_report(self, date: str = None) -> Optional[str]:
        """
        Generate daily PDF report
        
        Args:
            date: Date string (YYYY-MM-DD)
            
        Returns:
            Path to generated PDF, or None if no data
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        df = self._get_daily_data(date)
        
        if df.empty:
            print(f"No data found for {date}")
            return None
        
        stats = self._calculate_statistics(df)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Smart Home Energy Monitoring System", ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Daily Energy Report - {date}", ln=True, align="C")
        pdf.ln(10)
        
        # Summary
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "SUMMARY", ln=True)
        pdf.set_font("Arial", "", 11)
        
        pdf.cell(100, 8, f"Total Energy Consumed:", 0, 0)
        pdf.cell(0, 8, f"{stats['total_energy_kwh']:.2f} kWh", 0, 1)
        
        pdf.cell(100, 8, f"Total Cost:", 0, 0)
        pdf.cell(0, 8, f"₹{stats['total_cost_rs']:.2f}", 0, 1)
        
        pdf.cell(100, 8, f"Peak Power:", 0, 0)
        pdf.cell(0, 8, f"{stats['peak_power_w']:.0f} W", 0, 1)
        
        pdf.cell(100, 8, f"Average Power:", 0, 0)
        pdf.cell(0, 8, f"{stats['avg_power_w']:.0f} W", 0, 1)
        
        pdf.cell(100, 8, f"Average Voltage:", 0, 0)
        pdf.cell(0, 8, f"{stats['avg_voltage']:.1f} V", 0, 1)
        
        pdf.cell(100, 8, f"Average Current:", 0, 0)
        pdf.cell(0, 8, f"{stats['avg_current']:.2f} A", 0, 1)
        
        pdf.cell(100, 8, f"Alerts Triggered:", 0, 0)
        pdf.cell(0, 8, f"{stats['alert_count']}", 0, 1)
        
        pdf.cell(100, 8, f"Total Readings:", 0, 0)
        pdf.cell(0, 8, f"{stats['num_readings']}", 0, 1)
        
        pdf.ln(10)
        
        # Hourly breakdown
        if 'timestamp' in df.columns and not df.empty:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "HOURLY BREAKDOWN", ln=True)
            
            # Group by hour
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            energy_col = 'energy_wh' if 'energy_wh' in df.columns else 'energy_wh_this_interval'
            hourly = df.groupby('hour')[energy_col].sum().reset_index()
            hourly['energy_kwh'] = hourly[energy_col] / 1000
            
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 8, "Hour", 1, 0, "C")
            pdf.cell(60, 8, "Energy (kWh)", 1, 0, "C")
            pdf.cell(60, 8, "Cost (₹)", 1, 1, "C")
            
            pdf.set_font("Arial", "", 10)
            for _, row in hourly.iterrows():
                hour = f"{int(row['hour'])}:00 - {int(row['hour'])+1}:00"
                cost = row['energy_kwh'] * 7.5  # Approximate rate
                pdf.cell(40, 7, hour, 1, 0)
                pdf.cell(60, 7, f"{row['energy_kwh']:.3f}", 1, 0)
                pdf.cell(60, 7, f"₹{cost:.2f}", 1, 1)
        
        # Save
        filename = self.output_dir / f"daily_report_{date}.pdf"
        pdf.output(str(filename))
        
        return str(filename)
    
    def generate_weekly_report(self) -> Optional[str]:
        """
        Generate weekly report (last 7 days)
        
        Returns:
            Path to generated PDF
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        readings = self.logger.get_readings(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            limit=100000
        )
        
        if not readings:
            print("No data found for last 7 days")
            return None
        
        df = pd.DataFrame(readings)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        stats = self._calculate_statistics(df)
        
        # Group by day
        df['date'] = df['timestamp'].dt.date
        energy_col = 'energy_wh' if 'energy_wh' in df.columns else 'energy_wh_this_interval'
        cost_col = 'cost_rs' if 'cost_rs' in df.columns else 'cost_rs_this_interval'
        
        daily = df.groupby('date').agg({
            energy_col: 'sum',
            cost_col: 'sum'
        }).reset_index()
        daily['energy_kwh'] = daily[energy_col] / 1000
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Smart Home Energy Monitoring System", ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Weekly Energy Report", ln=True, align="C")
        pdf.cell(0, 10, f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", ln=True, align="C")
        pdf.ln(10)
        
        # Summary
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "SUMMARY", ln=True)
        pdf.set_font("Arial", "", 11)
        
        pdf.cell(100, 8, f"Total Energy (7 days):", 0, 0)
        pdf.cell(0, 8, f"{stats['total_energy_kwh']:.2f} kWh", 0, 1)
        
        pdf.cell(100, 8, f"Total Cost (7 days):", 0, 0)
        pdf.cell(0, 8, f"₹{stats['total_cost_rs']:.2f}", 0, 1)
        
        pdf.cell(100, 8, f"Average Daily Energy:", 0, 0)
        pdf.cell(0, 8, f"{daily['energy_kwh'].mean():.2f} kWh", 0, 1)
        
        pdf.cell(100, 8, f"Average Daily Cost:", 0, 0)
        pdf.cell(0, 8, f"₹{daily[cost_col].mean():.2f}", 0, 1)
        
        # Daily breakdown
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "DAILY BREAKDOWN", ln=True)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 8, "Date", 1, 0, "C")
        pdf.cell(60, 8, "Energy (kWh)", 1, 0, "C")
        pdf.cell(60, 8, "Cost (₹)", 1, 1, "C")
        
        pdf.set_font("Arial", "", 10)
        for _, row in daily.iterrows():
            pdf.cell(60, 7, str(row['date']), 1, 0)
            pdf.cell(60, 7, f"{row['energy_kwh']:.2f}", 1, 0)
            pdf.cell(60, 7, f"₹{row[cost_col]:.2f}", 1, 1)
        
        filename = self.output_dir / f"weekly_report_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.pdf"
        pdf.output(str(filename))
        
        return str(filename)
    
    def generate_monthly_report(self, year: int = None, month: int = None) -> Optional[str]:
        """
        Generate monthly PDF report
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            Path to generated PDF
        """
        df = self._get_monthly_data(year, month)
        
        if df.empty:
            print(f"No data found for {year}-{month}")
            return None
        
        stats = self._calculate_statistics(df)
        
        # Calculate daily averages
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        energy_col = 'energy_wh' if 'energy_wh' in df.columns else 'energy_wh_this_interval'
        cost_col = 'cost_rs' if 'cost_rs' in df.columns else 'cost_rs_this_interval'
        power_col = 'power_w' if 'power_w' in df.columns else 'real_power_w'
        
        daily = df.groupby('date').agg({
            energy_col: 'sum',
            cost_col: 'sum',
            power_col: 'max'
        }).reset_index()
        daily['energy_kwh'] = daily[energy_col] / 1000
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Smart Home Energy Monitoring System", ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Monthly Energy Report - {year}-{month:02d}", ln=True, align="C")
        pdf.ln(10)
        
        # Summary
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "SUMMARY", ln=True)
        pdf.set_font("Arial", "", 11)
        
        pdf.cell(100, 8, f"Total Energy Consumed:", 0, 0)
        pdf.cell(0, 8, f"{stats['total_energy_kwh']:.2f} kWh", 0, 1)
        
        pdf.cell(100, 8, f"Total Cost:", 0, 0)
        pdf.cell(0, 8, f"₹{stats['total_cost_rs']:.2f}", 0, 1)
        
        pdf.cell(100, 8, f"Peak Power:", 0, 0)
        pdf.cell(0, 8, f"{stats['peak_power_w']:.0f} W", 0, 1)
        
        pdf.cell(100, 8, f"Average Daily Energy:", 0, 0)
        pdf.cell(0, 8, f"{daily['energy_kwh'].mean():.2f} kWh", 0, 1)
        
        pdf.cell(100, 8, f"Average Daily Cost:", 0, 0)
        pdf.cell(0, 8, f"₹{daily[cost_col].mean():.2f}", 0, 1)
        
        pdf.cell(100, 8, f"Total Alerts:", 0, 0)
        pdf.cell(0, 8, f"{stats['alert_count']}", 0, 1)
        
        pdf.ln(10)
        
        # Daily breakdown
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "DAILY BREAKDOWN", ln=True)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 8, "Date", 1, 0, "C")
        pdf.cell(50, 8, "Energy (kWh)", 1, 0, "C")
        pdf.cell(50, 8, "Cost (₹)", 1, 0, "C")
        pdf.cell(50, 8, "Peak Power (W)", 1, 1, "C")
        
        pdf.set_font("Arial", "", 10)
        for _, row in daily.iterrows():
            pdf.cell(40, 7, str(row['date']), 1, 0)
            pdf.cell(50, 7, f"{row['energy_kwh']:.2f}", 1, 0)
            pdf.cell(50, 7, f"₹{row[cost_col]:.2f}", 1, 0)
            pdf.cell(50, 7, f"{row[power_col]:.0f}", 1, 1)
        
        # Save
        filename = self.output_dir / f"monthly_report_{year}_{month:02d}.pdf"
        pdf.output(str(filename))
        
        return str(filename)


if __name__ == "__main__":
    generator = EnergyReportGenerator()
    
    # Generate reports
    daily = generator.generate_daily_report()
    if daily:
        print(f"Daily report generated: {daily}")
    
    weekly = generator.generate_weekly_report()
    if weekly:
        print(f"Weekly report generated: {weekly}")
    
    monthly = generator.generate_monthly_report()
    if monthly:
        print(f"Monthly report generated: {monthly}")