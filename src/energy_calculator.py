"""
Energy Calculator - Performs all electrical calculations
Power, Energy, Cost, and other derived metrics
"""

import json
from datetime import datetime
from typing import Dict, Optional, Tuple


class EnergyCalculator:
    """
    Calculates power consumption, energy usage, and cost
    Supports real and apparent power, peak/off-peak pricing
    """
    
    def __init__(self, config_path: str = "config/settings.json"):
        """
        Initialize calculator with configuration
        
        Args:
            config_path: Path to settings.json
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Running totals
        self.total_energy_wh = 0.0
        self.total_cost_rs = 0.0
        self.last_calculation_time = None
        self.daily_energy_wh = 0.0
        self.daily_reset_date = datetime.now().date()
        
        # Peak hour rates
        self.normal_rate = self.config["cost_per_kwh"]
        self.peak_rate = self.normal_rate * self.config["peak_hour_multiplier"]
        
    def calculate_power(self, voltage: float, current: float, 
                       power_factor: float = 1.0) -> Dict[str, float]:
        """
        Calculate real and apparent power
        
        Args:
            voltage: Voltage in volts
            current: Current in amperes
            power_factor: Power factor (0 to 1)
            
        Returns:
            Dictionary containing:
            - apparent_power_va: Apparent power in VA
            - real_power_w: Real power in Watts
            - reactive_power_var: Reactive power in VAR
        """
        apparent_power = voltage * current
        real_power = apparent_power * power_factor
        reactive_power = (apparent_power ** 2 - real_power ** 2) ** 0.5
        
        return {
            "apparent_power_va": round(apparent_power, 2),
            "real_power_w": round(real_power, 2),
            "reactive_power_var": round(reactive_power, 2)
        }
    
    def get_current_rate(self) -> float:
        """
        Get current electricity rate based on time of day
        
        Returns:
            Rate in Rupees per kWh
        """
        current_hour = datetime.now().hour
        peak_start = self.config["peak_hours_start"]
        peak_end = self.config["peak_hours_end"]
        
        if peak_start <= current_hour < peak_end:
            return self.peak_rate
        return self.normal_rate
    
    def calculate_energy_and_cost(self, power_w: float, 
                                  duration_seconds: float) -> Tuple[float, float]:
        """
        Calculate energy consumption and cost for a time period
        
        Args:
            power_w: Power in Watts
            duration_seconds: Time duration in seconds
            
        Returns:
            Tuple of (energy_wh, cost_rs)
        """
        # Energy in Watt-hours
        energy_wh = power_w * (duration_seconds / 3600.0)
        
        # Cost calculation
        rate = self.get_current_rate()
        cost_rs = (energy_wh / 1000.0) * rate
        
        return round(energy_wh, 3), round(cost_rs, 4)
    
    def update_totals(self, power_w: float, duration_seconds: float) -> Dict[str, float]:
        """
        Update running totals with new consumption data
        
        Args:
            power_w: Power in Watts
            duration_seconds: Time since last update
            
        Returns:
            Dictionary with updated totals
        """
        energy_wh, cost_rs = self.calculate_energy_and_cost(power_w, duration_seconds)
        
        # Update totals
        self.total_energy_wh += energy_wh
        self.total_cost_rs += cost_rs
        
        # Update daily totals
        today = datetime.now().date()
        if today != self.daily_reset_date:
            # Reset daily totals at midnight
            self.daily_energy_wh = 0
            self.daily_reset_date = today
        self.daily_energy_wh += energy_wh
        
        return {
            "energy_wh_this_interval": energy_wh,
            "cost_rs_this_interval": cost_rs,
            "total_energy_kwh": round(self.total_energy_wh / 1000, 3),
            "total_cost_rs": round(self.total_cost_rs, 2),
            "daily_energy_kwh": round(self.daily_energy_wh / 1000, 3),
            "current_rate_rs_per_kwh": self.get_current_rate()
        }
    
    def calculate_efficiency_score(self, power_w: float, 
                                   threshold_w: Optional[float] = None) -> Dict[str, any]:
        """
        Calculate efficiency score and provide recommendations
        
        Args:
            power_w: Current power in Watts
            threshold_w: Custom threshold (uses config if None)
            
        Returns:
            Dictionary with efficiency metrics
        """
        if threshold_w is None:
            threshold_w = self.config["power_threshold_warning"]
        
        # Score from 0 to 100 (higher = more efficient)
        if power_w <= threshold_w * 0.3:
            score = 100
            level = "Excellent"
            suggestion = "Great! Your energy usage is very efficient."
        elif power_w <= threshold_w * 0.6:
            score = 75
            level = "Good"
            suggestion = "Good usage. Consider checking standby devices."
        elif power_w <= threshold_w:
            score = 50
            level = "Fair"
            suggestion = "Usage is moderate. Consider reducing during peak hours."
        elif power_w <= threshold_w * 1.5:
            score = 25
            level = "Poor"
            suggestion = "High energy usage detected. Check for inefficient appliances."
        else:
            score = 0
            level = "Critical"
            suggestion = "Very high consumption! Immediate attention needed."
        
        return {
            "score": score,
            "level": level,
            "suggestion": suggestion,
            "threshold_w": threshold_w,
            "current_w": power_w
        }
    
    def estimate_monthly_bill(self) -> Dict[str, float]:
        """
        Estimate monthly electricity bill based on current usage pattern
        
        Returns:
            Dictionary with monthly estimates
        """
        # If we have less than a day of data, estimate based on current trend
        daily_kwh = self.daily_energy_wh / 1000
        
        # Calculate days in current month
        from calendar import monthrange
        today = datetime.now()
        days_in_month = monthrange(today.year, today.month)[1]
        days_elapsed = today.day
        
        if days_elapsed > 0 and daily_kwh > 0:
            # Project for full month
            projected_monthly_kwh = (daily_kwh / days_elapsed) * days_in_month
        else:
            # Fallback: assume average usage
            projected_monthly_kwh = 300  # Average Indian household
        
        projected_cost = projected_monthly_kwh * self.normal_rate
        
        return {
            "projected_monthly_kwh": round(projected_monthly_kwh, 1),
            "projected_monthly_cost_rs": round(projected_cost, 2),
            "average_daily_kwh": round(daily_kwh, 2),
            "days_tracked": days_elapsed
        }
    
    def get_summary(self) -> Dict:
        """
        Get complete summary of all calculations
        
        Returns:
            Dictionary with all metrics
        """
        monthly_estimate = self.estimate_monthly_bill()
        
        return {
            "total_energy_kwh": round(self.total_energy_wh / 1000, 3),
            "total_cost_rs": round(self.total_cost_rs, 2),
            "daily_energy_kwh": round(self.daily_energy_wh / 1000, 3),
            "current_rate_rs_per_kwh": self.get_current_rate(),
            "normal_rate_rs_per_kwh": self.normal_rate,
            "peak_rate_rs_per_kwh": self.peak_rate,
            "peak_hours": f"{self.config['peak_hours_start']:02d}:00 - {self.config['peak_hours_end']:02d}:00",
            "monthly_projection_kwh": monthly_estimate["projected_monthly_kwh"],
            "monthly_projection_cost_rs": monthly_estimate["projected_monthly_cost_rs"]
        }
    
    def reset(self) -> None:
        """Reset all totals (start fresh)"""
        self.total_energy_wh = 0.0
        self.total_cost_rs = 0.0
        self.daily_energy_wh = 0.0
        self.daily_reset_date = datetime.now().date()
        print("🔄 Energy calculator reset successfully!")


# For direct testing
if __name__ == "__main__":
    calc = EnergyCalculator()
    
    print("📐 Testing Energy Calculator...\n")
    
    # Test power calculation
    power = calc.calculate_power(230, 2.5, 0.85)
    print(f"Power Calculation: {power}")
    
    # Test energy and cost
    energy, cost = calc.calculate_energy_and_cost(500, 3600)  # 500W for 1 hour
    print(f"Energy for 1 hour at 500W: {energy} Wh, Cost: ₹{cost}")
    
    # Test rate
    rate = calc.get_current_rate()
    print(f"Current rate: ₹{rate}/kWh")
    
    # Get summary
    summary = calc.get_summary()
    print(f"\nSummary: {summary}")