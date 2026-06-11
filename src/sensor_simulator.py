"""
Sensor Simulator - Generates fake current and voltage data
No hardware required - completely virtual simulation
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SensorSimulator:
    """
    Simulates electrical sensors (current clamp, voltage sensor)
    Generates realistic data based on appliance schedules
    """
    
    def __init__(self, config_path: str = "config/settings.json", 
                 appliances_path: str = "config/appliances.json"):
        """
        Initialize the sensor simulator with configuration
        
        Args:
            config_path: Path to settings.json
            appliances_path: Path to appliances.json
        """
        self.config = self._load_json(config_path)
        self.appliances = self._load_json(appliances_path)["appliances"]
        self.appliance_dict = {a["name"]: a for a in self.appliances}
        
        # Simulation state
        self.current_schedule = None
        self.schedule_start_time = None
        self.schedule_end_time = None
        self.base_voltage = self.config["voltage_nominal"]
        
    def _load_json(self, filepath: str) -> dict:
        """Load JSON configuration file"""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def load_simulation_scenario(self, scenario_path: str) -> None:
        """
        Load a simulation scenario from JSON file
        
        Args:
            scenario_path: Path to scenario JSON file (e.g., "simulation/normal_day.json")
        """
        self.current_schedule = self._load_json(scenario_path)
        self.schedule_start_time = time.time()
        self.schedule_end_time = self.schedule_start_time + self.current_schedule["duration_seconds"]
        print(f"✅ Loaded scenario: {self.current_schedule['name']}")
        print(f"   Duration: {self.current_schedule['duration_seconds']} seconds")
        
    def _get_active_appliances(self, elapsed_seconds: float) -> List[Tuple[str, int]]:
        """
        Determine which appliances are active at the current time
        
        Args:
            elapsed_seconds: Time elapsed since simulation started
            
        Returns:
            List of (appliance_name, quantity) tuples
        """
        active = []
        for schedule in self.current_schedule["appliance_schedule"]:
            if schedule["start_sec"] <= elapsed_seconds <= schedule["end_sec"]:
                active.append((schedule["appliance"], schedule["quantity"]))
        return active
    
    def _calculate_total_current(self, active_appliances: List[Tuple[str, int]]) -> float:
        """
        Calculate total current draw from active appliances
        
        Args:
            active_appliances: List of (appliance_name, quantity) tuples
            
        Returns:
            Total current in amperes
        """
        total_current = 0.0
        
        for appliance_name, quantity in active_appliances:
            appliance = self.appliance_dict.get(appliance_name)
            if appliance:
                # Add current for this appliance (with some random variation)
                base_current = appliance["typical_current_a"]
                variation = random.uniform(-0.05, 0.05) * base_current
                total_current += (base_current + variation) * quantity
        
        # Add background noise (phantom loads, standby power)
        noise = random.uniform(0, self.current_schedule.get("background_noise_amps", 0.05))
        total_current += noise
        
        return round(total_current, 3)
    
    def _calculate_voltage(self) -> float:
        """
        Simulate voltage variations (usually 220-240V)
        Small fluctuations based on time of day and load
        
        Returns:
            Voltage in volts
        """
        # Base voltage with small random variation
        variation = random.uniform(-5, 5)
        voltage = self.base_voltage + variation
        
        # During peak hours (6 PM - 10 PM), voltage may drop slightly
        current_hour = datetime.now().hour
        if self.config["peak_hours_start"] <= current_hour < self.config["peak_hours_end"]:
            voltage -= random.uniform(2, 5)
        
        return round(voltage, 1)
    
    def _calculate_power_factor(self, current: float) -> float:
        """
        Simulate power factor based on current draw
        Higher current typically means inductive loads (lower PF)
        
        Args:
            current: Current in amperes
            
        Returns:
            Power factor (0 to 1)
        """
        if current < 0.5:
            # Small loads (LEDs, chargers) - good power factor
            return round(random.uniform(0.85, 0.95), 2)
        elif current < 2.0:
            # Medium loads (fans, TV) - decent power factor
            return round(random.uniform(0.80, 0.90), 2)
        elif current < 5.0:
            # Large loads (AC, fridge) - moderate power factor
            return round(random.uniform(0.75, 0.85), 2)
        else:
            # Very high loads (heater, motor) - lower power factor
            return round(random.uniform(0.65, 0.80), 2)
    
    def read_sensors(self) -> Dict[str, float]:
        """
        Read simulated sensor values
        
        Returns:
            Dictionary containing:
            - voltage: Voltage in volts
            - current: Current in amperes
            - power_factor: Power factor (0-1)
            - frequency: Grid frequency in Hz
            - temperature: Simulated sensor temperature
        """
        # Check if simulation is still running
        if self.current_schedule and time.time() > self.schedule_end_time:
            print("\n🏁 Simulation scenario completed!")
            self.current_schedule = None
            return None
        
        # Calculate elapsed time
        elapsed = 0
        if self.current_schedule and self.schedule_start_time:
            elapsed = time.time() - self.schedule_start_time
        
        # Get active appliances and calculate current
        if self.current_schedule:
            active = self._get_active_appliances(elapsed)
            current = self._calculate_total_current(active)
        else:
            # Idle mode - just background load
            current = round(random.uniform(0.1, 0.5), 3)
        
        # Calculate other sensor values
        voltage = self._calculate_voltage()
        power_factor = self._calculate_power_factor(current)
        
        # Simulate grid frequency (normally 50Hz with small variations)
        frequency = round(50 + random.uniform(-0.2, 0.2), 2)
        
        # Simulate sensor temperature (increases with current)
        temperature = round(25 + (current / 15) * 15, 1)
        
        return {
            "voltage": voltage,
            "current": current,
            "power_factor": power_factor,
            "frequency": frequency,
            "temperature": temperature,
            "simulation_time_elapsed": round(elapsed, 1)
        }
    
    def get_appliance_breakdown(self) -> List[Dict]:
        """
        Get detailed breakdown of which appliances are active
        
        Returns:
            List of active appliances with their power consumption
        """
        if not self.current_schedule or not self.schedule_start_time:
            return []
        
        elapsed = time.time() - self.schedule_start_time
        active = self._get_active_appliances(elapsed)
        
        breakdown = []
        for appliance_name, quantity in active:
            appliance = self.appliance_dict.get(appliance_name)
            if appliance:
                breakdown.append({
                    "name": appliance_name,
                    "quantity": quantity,
                    "power_w": appliance["typical_power_w"] * quantity,
                    "current_a": appliance["typical_current_a"] * quantity
                })
        
        return breakdown
    
    def is_simulation_running(self) -> bool:
        """Check if a simulation is currently active"""
        if not self.current_schedule or not self.schedule_start_time:
            return False
        
        # Check if we have a valid running schedule
        if self.schedule_end_time and time.time() <= self.schedule_end_time:
            return True
        
        # Auto-clear if expired
        if self.schedule_end_time and time.time() > self.schedule_end_time:
            self.current_schedule = None
            self.schedule_start_time = None
            self.schedule_end_time = None
        
        return False
    
    def get_simulation_progress(self) -> float:
        """Get progress of current simulation (0 to 1)"""
        if not self.is_simulation_running():
            return 0
        
        elapsed = time.time() - self.schedule_start_time
        total = self.current_schedule["duration_seconds"]
        return min(1.0, elapsed / total)
    
    def get_simulation_name(self) -> str:
        """Get name of current simulation scenario"""
        if self.current_schedule:
            return self.current_schedule["name"]
        return "Idle Mode"


# For direct testing
if __name__ == "__main__":
    simulator = SensorSimulator()
    simulator.load_simulation_scenario("simulation/normal_day.json")
    
    print("\n📊 Testing Sensor Simulator...\n")
    
    for i in range(20):
        sensors = simulator.read_sensors()
        if sensors:
            print(f"[{i+1:2d}] V={sensors['voltage']:.1f}V | "
                  f"I={sensors['current']:.2f}A | "
                  f"PF={sensors['power_factor']:.2f} | "
                  f"Freq={sensors['frequency']:.1f}Hz")
        time.sleep(0.5)