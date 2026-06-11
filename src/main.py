#!/usr/bin/env python3
"""
Smart Home Energy Monitoring System - Main Entry Point
Complete virtual simulation of energy monitoring without hardware
"""

import time
import signal
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from sensor_simulator import SensorSimulator
from energy_calculator import EnergyCalculator
from alert_manager import AlertManager
from data_logger import DataLogger


class EnergyMonitoringSystem:
    """
    Main system class that orchestrates all components
    """
    
    def __init__(self, scenario_path: str = None):
        """
        Initialize the energy monitoring system
        
        Args:
            scenario_path: Path to simulation scenario JSON file
        """
        print("\n" + "="*60)
        print("🏠 SMART HOME ENERGY MONITORING SYSTEM")
        print("="*60)
        print("📡 Virtual Simulation Mode (No Hardware Required)")
        print("="*60 + "\n")
        
        # Initialize all components
        self.sensor = SensorSimulator()
        self.calculator = EnergyCalculator()
        self.alert_manager = AlertManager()
        self.logger = DataLogger()
        
        # System state
        self.running = True
        self.last_read_time = None
        self.readings_count = 0
        self.alerts_count = 0
        
        # Load simulation scenario if provided
        if scenario_path:
            self.load_scenario(scenario_path)
        else:
            print("💡 No scenario loaded. System running in IDLE mode.")
            print("   Use load_scenario() to load a simulation scenario.\n")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Display initial configuration
        self._display_config()
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Shutting down system...")
        self.running = False
    
    def _display_config(self):
        """Display current configuration"""
        print("📋 SYSTEM CONFIGURATION")
        print("-" * 40)
        print(f"   Voltage Nominal: {self.calculator.config['voltage_nominal']}V")
        print(f"   Warning Threshold: {self.calculator.config['power_threshold_warning']}W")
        print(f"   Critical Threshold: {self.calculator.config['power_threshold_critical']}W")
        print(f"   Electricity Rate: ₹{self.calculator.normal_rate}/kWh")
        print(f"   Peak Rate: ₹{self.calculator.peak_rate}/kWh")
        print(f"   Peak Hours: {self.calculator.config['peak_hours_start']:02d}:00 - {self.calculator.config['peak_hours_end']:02d}:00")
        print(f"   Sampling Interval: {self.calculator.config['sampling_interval_ms']}ms")
        print("-" * 40 + "\n")
    
    def load_scenario(self, scenario_path: str):
        """
        Load a simulation scenario
        
        Args:
            scenario_path: Path to scenario JSON file
        """
        self.sensor.load_simulation_scenario(scenario_path)
        print(f"🎬 Loaded scenario: {self.sensor.get_simulation_name()}\n")
    
    def _print_header(self):
        """Print table header for console output"""
        print("\n" + "="*100)
        print(f"{'Time':^12} | {'Voltage':^8} | {'Current':^8} | {'Power':^8} | {'Energy':^10} | {'Cost':^8} | {'Status':^12} | {'Progress':^8}")
        print("="*100)
    
    def _format_output(self, sensor_data: dict, power_data: dict, 
                       energy_data: dict, alert_triggered: bool,
                       progress: float) -> str:
        """
        Format the output line for console
        
        Returns:
            Formatted string
        """
        now = datetime.now().strftime("%H:%M:%S")
        voltage = sensor_data.get("voltage", 0)
        current = sensor_data.get("current", 0)
        power = power_data.get("real_power_w", 0)
        energy = energy_data.get("total_energy_kwh", 0)
        cost = energy_data.get("total_cost_rs", 0)
        
        status = "⚠️ ALERT" if alert_triggered else "✓ NORMAL"
        progress_pct = int(progress * 100)
        
        return (f"{now:^12} | {voltage:^8.1f} | {current:^8.2f} | "
                f"{power:^8.0f} | {energy:^10.3f} | ₹{cost:^7.2f} | "
                f"{status:^12} | {progress_pct:^8}%")
    
    def _print_reading(self, formatted_line: str):
        """Print a single reading line"""
        print(formatted_line)
    
    def _print_appliance_breakdown(self):
        """Print current active appliances"""
        appliances = self.sensor.get_appliance_breakdown()
        if appliances:
            print("\n📱 Active Appliances:")
            for app in appliances:
                print(f"   • {app['name']} x{app['quantity']} → {app['power_w']:.0f}W")
    
    def _print_summary(self):
        """Print final summary when stopping"""
        print("\n" + "="*60)
        print("📊 FINAL SUMMARY")
        print("="*60)
        
        summary = self.calculator.get_summary()
        print(f"   Total Energy Consumed: {summary['total_energy_kwh']} kWh")
        print(f"   Total Cost: ₹{summary['total_cost_rs']}")
        print(f"   Daily Energy (today): {summary['daily_energy_kwh']} kWh")
        print(f"   Current Rate: ₹{summary['current_rate_rs_per_kwh']}/kWh")
        print(f"   Peak Hours: {summary['peak_hours']}")
        print(f"   Monthly Projection: {summary['monthly_projection_kwh']} kWh (₹{summary['monthly_projection_cost_rs']})")
        
        alert_summary = self.alert_manager.get_alert_summary()
        if alert_summary['total_alerts'] > 0:
            print(f"\n   ⚠️ Alerts Triggered: {alert_summary['total_alerts']}")
            print(f"      - Warnings: {alert_summary['by_severity']['WARNING']}")
            print(f"      - Critical: {alert_summary['by_severity']['CRITICAL']}")
        
        print(f"\n   💾 Data saved to: {self.logger.get_todays_csv_path()}")
        print(f"   📁 SQLite database: {self.logger.db_path}")
        print("="*60 + "\n")
    
    def run(self, duration_seconds: int = None, quiet: bool = False):
        """
        Run the energy monitoring system
        
        Args:
            duration_seconds: Run for specific duration (None = until Ctrl+C)
            quiet: Suppress console output (useful for dashboard mode)
        """
        print("▶️ SYSTEM STARTED")
        print("   Press Ctrl+C to stop\n")
        
        if not quiet:
            self._print_header()
        
        start_time = time.time()
        self.last_read_time = start_time
        
        try:
            while self.running:
                # Check if duration limit reached
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    print(f"\n⏰ Duration limit ({duration_seconds}s) reached.")
                    break
                
                # Read sensors
                sensor_data = self.sensor.read_sensors()
                
                # Check if simulation ended
                if sensor_data is None:
                    print("\n🏁 Simulation completed. Waiting for new scenario...")
                    print("   Press Ctrl+C to exit or load new scenario.\n")
                    time.sleep(2)
                    continue
                
                # Calculate elapsed time since last reading
                current_time = time.time()
                if self.last_read_time:
                    elapsed = current_time - self.last_read_time
                else:
                    elapsed = self.calculator.config["sampling_interval_ms"] / 1000
                self.last_read_time = current_time
                
                # Calculate power
                power_data = self.calculator.calculate_power(
                    sensor_data["voltage"],
                    sensor_data["current"],
                    sensor_data["power_factor"]
                )
                
                # Update energy and cost totals
                energy_data = self.calculator.update_totals(
                    power_data["real_power_w"],
                    elapsed
                )
                
                # Check alerts
                triggered_alerts = self.alert_manager.check_all(
                    power_data["real_power_w"],
                    sensor_data["current"],
                    sensor_data["voltage"],
                    sensor_data["temperature"]
                )
                alert_triggered = len(triggered_alerts) > 0
                if alert_triggered:
                    self.alerts_count += 1
                
                # Log data
                progress = self.sensor.get_simulation_progress()
                self.logger.log_reading(
                    sensor_data, power_data, energy_data,
                    alert_triggered, progress
                )
                self.readings_count += 1
                
                # Console output
                if not quiet:
                    formatted = self._format_output(
                        sensor_data, power_data, energy_data,
                        alert_triggered, progress
                    )
                    self._print_reading(formatted)
                    
                    # Print appliance breakdown periodically (every 10 readings)
                    if self.readings_count % 10 == 0:
                        self._print_appliance_breakdown()
                
                # Wait for next reading
                interval = self.calculator.config["sampling_interval_ms"] / 1000
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ System interrupted by user")
        finally:
            self._print_summary()
            self.logger.close()
    
    def run_dashboard_mode(self):
        """
        Run in dashboard mode (no console output)
        Used when Streamlit dashboard is running
        """
        self.run(quiet=True)
    
    def get_status(self) -> dict:
        """
        Get current system status (for dashboard API)
        
        Returns:
            Dictionary with current readings
        """
        sensor_data = self.sensor.read_sensors()
        if sensor_data is None:
            return None
        
        # Calculate elapsed time
        current_time = time.time()
        if self.last_read_time:
            elapsed = current_time - self.last_read_time
        else:
            elapsed = self.calculator.config["sampling_interval_ms"] / 1000
        self.last_read_time = current_time
        
        # Calculate power
        power_data = self.calculator.calculate_power(
            sensor_data["voltage"],
            sensor_data["current"],
            sensor_data["power_factor"]
        )
        
        # Update energy and cost totals
        energy_data = self.calculator.update_totals(
            power_data["real_power_w"],
            elapsed
        )
        
        # Check alerts
        triggered_alerts = self.alert_manager.check_all(
            power_data["real_power_w"],
            sensor_data["current"],
            sensor_data["voltage"],
            sensor_data["temperature"]
        )
        
        # Log data
        progress = self.sensor.get_simulation_progress()
        self.logger.log_reading(
            sensor_data, power_data, energy_data,
            len(triggered_alerts) > 0, progress
        )
        self.readings_count += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor": sensor_data,
            "power": power_data,
            "energy": energy_data,
            "alerts": triggered_alerts,
            "simulation": {
                "name": self.sensor.get_simulation_name(),
                "progress": progress,
                "is_running": self.sensor.is_simulation_running()
            },
            "appliances": self.sensor.get_appliance_breakdown()
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Home Energy Monitoring System")
    parser.add_argument("--scenario", "-s", type=str, 
                       help="Path to simulation scenario JSON file")
    parser.add_argument("--duration", "-d", type=int,
                       help="Run for specified seconds")
    parser.add_argument("--list-scenarios", "-l", action="store_true",
                       help="List available simulation scenarios")
    
    args = parser.parse_args()
    
    if args.list_scenarios:
        print("\n📁 Available Simulation Scenarios:")
        print("-" * 40)
        scenario_dir = Path("simulation")
        if scenario_dir.exists():
            for scenario in scenario_dir.glob("*.json"):
                print(f"   • {scenario.name}")
        else:
            print("   No scenarios found. Create JSON files in 'simulation/' directory.")
        print()
        return
    
    # Create system instance
    system = EnergyMonitoringSystem(args.scenario)
    
    # Run the system
    system.run(duration_seconds=args.duration)


if __name__ == "__main__":
    main()