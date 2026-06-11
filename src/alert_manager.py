"""
Alert Manager - Monitors thresholds and triggers alerts
Supports email, console, and file-based alerts
"""

import json
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional


class AlertManager:
    """
    Manages alert generation for power thresholds, overloads, and anomalies
    """
    
    # Alert severity levels
    SEVERITY_INFO = "INFO"
    SEVERITY_WARNING = "WARNING"
    SEVERITY_CRITICAL = "CRITICAL"
    
    # Alert types
    ALERT_TYPE_POWER_HIGH = "high_power"
    ALERT_TYPE_POWER_CRITICAL = "critical_power"
    ALERT_TYPE_OVERLOAD = "overload"
    ALERT_TYPE_VOLTAGE_EXTREME = "voltage_extreme"
    ALERT_TYPE_HIGH_TEMPERATURE = "high_temperature"
    ALERT_TYPE_APPLIANCE_STUCK = "appliance_stuck"
    
    def __init__(self, config_path: str = "config/settings.json", 
                 alert_log_path: str = "data/alerts_log.csv"):
        """
        Initialize alert manager
        
        Args:
            config_path: Path to settings.json
            alert_log_path: Path for alert log CSV
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.alert_log_path = Path(alert_log_path)
        self.alert_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Alert cooldown tracking (prevents alert spam)
        self.last_alert_time = {}
        self.alert_cooldown_seconds = 60  # Same alert type every 60 seconds max
        
        # Recent alerts for reporting
        self.recent_alerts = []  # Max 100 alerts stored
        self.max_recent_alerts = 100
        
        # Initialize alert log file with headers
        if not self.alert_log_path.exists():
            self._write_alert_log_header()
    
    def _write_alert_log_header(self) -> None:
        """Write CSV header for alert log file"""
        with open(self.alert_log_path, 'w') as f:
            f.write("timestamp,severity,alert_type,message,current_value,threshold\n")
    
    def _log_alert_to_csv(self, severity: str, alert_type: str, 
                          message: str, current_value: float, 
                          threshold: float) -> None:
        """
        Write alert to CSV log file
        
        Args:
            severity: Alert severity (INFO/WARNING/CRITICAL)
            alert_type: Type of alert
            message: Alert message
            current_value: Current value that triggered alert
            threshold: Threshold value
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp},{severity},{alert_type},\"{message}\",{current_value},{threshold}\n"
        
        with open(self.alert_log_path, 'a') as f:
            f.write(log_line)
    
    def _add_to_recent_alerts(self, alert: Dict) -> None:
        """Add alert to recent alerts list"""
        self.recent_alerts.insert(0, alert)
        
        # Keep only last N alerts
        if len(self.recent_alerts) > self.max_recent_alerts:
            self.recent_alerts.pop()
    
    def _should_send_alert(self, alert_type: str) -> bool:
        """
        Check if alert should be sent (respect cooldown)
        
        Args:
            alert_type: Type of alert
            
        Returns:
            True if alert should be sent
        """
        last_time = self.last_alert_time.get(alert_type, 0)
        if time.time() - last_time < self.alert_cooldown_seconds:
            return False
        
        self.last_alert_time[alert_type] = time.time()
        return True
    
    def _send_email_alert(self, subject: str, message: str) -> bool:
        """
        Send email alert (if configured)
        
        Args:
            subject: Email subject
            message: Email body
            
        Returns:
            True if sent successfully
        """
        if not self.config.get("alert_email_enabled", False):
            return False
        
        # Note: This requires SMTP configuration
        # For production, add your SMTP settings
        try:
            # Example with Gmail (requires app password)
            # sender = "your-email@gmail.com"
            # password = "your-app-password"
            # receiver = self.config.get("alert_email", "")
            
            # For now, just log that email would be sent
            print(f"📧 [EMAIL ALERT] {subject}: {message}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email alert: {e}")
            return False
    
    def _print_console_alert(self, severity: str, message: str) -> None:
        """
        Print alert to console with appropriate formatting
        
        Args:
            severity: Alert severity
            message: Alert message
        """
        emoji = {
            self.SEVERITY_INFO: "ℹ️",
            self.SEVERITY_WARNING: "⚠️",
            self.SEVERITY_CRITICAL: "🔴"
        }.get(severity, "📢")
        
        print(f"\n{emoji} [{severity}] {message}\n")
    
    def check_power_threshold(self, power_w: float) -> Optional[Dict]:
        """
        Check if power exceeds thresholds and generate alert
        
        Args:
            power_w: Current power in Watts
            
        Returns:
            Alert dictionary if triggered, None otherwise
        """
        warning_threshold = self.config["power_threshold_warning"]
        critical_threshold = self.config["power_threshold_critical"]
        
        if power_w >= critical_threshold:
            if self._should_send_alert(self.ALERT_TYPE_POWER_CRITICAL):
                message = f"CRITICAL: Power consumption is {power_w:.0f}W (exceeds {critical_threshold:.0f}W threshold!)"
                alert = {
                    "severity": self.SEVERITY_CRITICAL,
                    "type": self.ALERT_TYPE_POWER_CRITICAL,
                    "message": message,
                    "value": power_w,
                    "threshold": critical_threshold,
                    "timestamp": datetime.now()
                }
                self._process_alert(alert)
                return alert
        
        elif power_w >= warning_threshold:
            if self._should_send_alert(self.ALERT_TYPE_POWER_HIGH):
                message = f"High power consumption: {power_w:.0f}W (above {warning_threshold:.0f}W warning)"
                alert = {
                    "severity": self.SEVERITY_WARNING,
                    "type": self.ALERT_TYPE_POWER_HIGH,
                    "message": message,
                    "value": power_w,
                    "threshold": warning_threshold,
                    "timestamp": datetime.now()
                }
                self._process_alert(alert)
                return alert
        
        return None
    
    def check_overload(self, current_a: float, voltage: float) -> Optional[Dict]:
        """
        Check for overload condition (very high current)
        
        Args:
            current_a: Current in amperes
            voltage: Voltage in volts
            
        Returns:
            Alert dictionary if triggered
        """
        # Calculate apparent power
        apparent_va = voltage * current_a
        
        # Overload threshold: 3000VA (approx 13A at 230V)
        overload_threshold_va = 3000
        
        if apparent_va >= overload_threshold_va:
            if self._should_send_alert(self.ALERT_TYPE_OVERLOAD):
                message = f"OVERLOAD! Apparent power: {apparent_va:.0f}VA (Current: {current_a:.1f}A)"
                alert = {
                    "severity": self.SEVERITY_CRITICAL,
                    "type": self.ALERT_TYPE_OVERLOAD,
                    "message": message,
                    "value": apparent_va,
                    "threshold": overload_threshold_va,
                    "timestamp": datetime.now()
                }
                self._process_alert(alert)
                return alert
        
        return None
    
    def check_voltage_extreme(self, voltage: float) -> Optional[Dict]:
        """
        Check for extreme voltage conditions (brownout/overvoltage)
        
        Args:
            voltage: Voltage in volts
            
        Returns:
            Alert dictionary if triggered
        """
        min_voltage = 180  # Minimum safe voltage
        max_voltage = 260  # Maximum safe voltage
        
        if voltage < min_voltage:
            if self._should_send_alert(self.ALERT_TYPE_VOLTAGE_EXTREME):
                message = f"Low voltage detected: {voltage:.0f}V (below {min_voltage}V)"
                alert = {
                    "severity": self.SEVERITY_WARNING,
                    "type": self.ALERT_TYPE_VOLTAGE_EXTREME,
                    "message": message,
                    "value": voltage,
                    "threshold": min_voltage,
                    "timestamp": datetime.now()
                }
                self._process_alert(alert)
                return alert
        
        elif voltage > max_voltage:
            if self._should_send_alert(self.ALERT_TYPE_VOLTAGE_EXTREME):
                message = f"High voltage detected: {voltage:.0f}V (above {max_voltage}V)"
                alert = {
                    "severity": self.SEVERITY_CRITICAL,
                    "type": self.ALERT_TYPE_VOLTAGE_EXTREME,
                    "message": message,
                    "value": voltage,
                    "threshold": max_voltage,
                    "timestamp": datetime.now()
                }
                self._process_alert(alert)
                return alert
        
        return None
    
    def check_temperature(self, temperature_c: float) -> Optional[Dict]:
        """
        Check for high sensor temperature
        
        Args:
            temperature_c: Temperature in Celsius
            
        Returns:
            Alert dictionary if triggered
        """
        max_temperature = 70  # Maximum safe temperature
        
        if temperature_c > max_temperature:
            if self._should_send_alert(self.ALERT_TYPE_HIGH_TEMPERATURE):
                message = f"High sensor temperature: {temperature_c:.0f}°C (above {max_temperature}°C)"
                alert = {
                    "severity": self.SEVERITY_WARNING,
                    "type": self.ALERT_TYPE_HIGH_TEMPERATURE,
                    "message": message,
                    "value": temperature_c,
                    "threshold": max_temperature,
                    "timestamp": datetime.now()
                }
                self._process_alert(alert)
                return alert
        
        return None
    
    def _process_alert(self, alert: Dict) -> None:
        """
        Process and send alert through all channels
        
        Args:
            alert: Alert dictionary
        """
        # Log to CSV
        self._log_alert_to_csv(
            alert["severity"],
            alert["type"],
            alert["message"],
            alert["value"],
            alert["threshold"]
        )
        
        # Add to recent alerts
        self._add_to_recent_alerts(alert)
        
        # Print to console
        self._print_console_alert(alert["severity"], alert["message"])
        
        # Send email (if configured)
        if self.config.get("alert_email_enabled", False):
            self._send_email_alert(
                f"[Energy Monitor] {alert['severity']}: {alert['type']}",
                f"Time: {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n{alert['message']}"
            )
    
    def check_all(self, power_w: float, current_a: float, 
                  voltage: float, temperature_c: float) -> List[Dict]:
        """
        Check all conditions and return all triggered alerts
        
        Args:
            power_w: Power in Watts
            current_a: Current in Amperes
            voltage: Voltage in Volts
            temperature_c: Temperature in Celsius
            
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        alerts = [
            self.check_power_threshold(power_w),
            self.check_overload(current_a, voltage),
            self.check_voltage_extreme(voltage),
            self.check_temperature(temperature_c)
        ]
        
        for alert in alerts:
            if alert:
                triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict]:
        """
        Get recent alerts
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.recent_alerts[:limit]
    
    def get_alert_summary(self) -> Dict:
        """
        Get summary statistics of alerts
        
        Returns:
            Dictionary with alert statistics
        """
        severity_counts = {
            self.SEVERITY_INFO: 0,
            self.SEVERITY_WARNING: 0,
            self.SEVERITY_CRITICAL: 0
        }
        
        type_counts = {}
        
        for alert in self.recent_alerts:
            severity_counts[alert["severity"]] += 1
            alert_type = alert["type"]
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        return {
            "total_alerts": len(self.recent_alerts),
            "by_severity": severity_counts,
            "by_type": type_counts,
            "most_recent": self.recent_alerts[0] if self.recent_alerts else None
        }


# For direct testing
if __name__ == "__main__":
    alert_mgr = AlertManager()
    
    print("🔔 Testing Alert Manager...\n")
    
    # Test power threshold alerts
    alert_mgr.check_power_threshold(600)   # Warning (if threshold is 500)
    alert_mgr.check_power_threshold(1200)  # Critical
    
    # Test overload
    alert_mgr.check_overload(14, 230)  # ~3220VA - Overload
    
    # Test voltage
    alert_mgr.check_voltage_extreme(170)  # Low voltage
    
    # Get summary
    summary = alert_mgr.get_alert_summary()
    print(f"\nAlert Summary: {summary}")