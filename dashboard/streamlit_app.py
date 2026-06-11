"""
Streamlit Dashboard for Smart Home Energy Monitoring System
Real-time visualization of energy data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sensor_simulator import SensorSimulator
from src.energy_calculator import EnergyCalculator
from src.alert_manager import AlertManager
from src.data_logger import DataLogger


# Page configuration
st.set_page_config(
    page_title="Smart Home Energy Monitor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .alert-warning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
    }
    .alert-critical {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


class EnergyDashboard:
    """Main dashboard class"""
    
    def __init__(self):
        """Initialize dashboard components"""
        self.sensor = SensorSimulator()
        self.calculator = EnergyCalculator()
        self.alert_manager = AlertManager()
        self.logger = DataLogger()
        
        # System state
        self.running = True
        self.last_update = None
        self.history = []
        self.max_history = 300  # Keep last 300 readings
        
        # Dashboard state
        self.selected_scenario = None
        
    def load_scenario(self, scenario_path: str):
        """Load a simulation scenario"""
        self.sensor.load_simulation_scenario(scenario_path)
        self.calculator.reset()  # Reset totals when starting new scenario
        
    def get_available_scenarios(self):
        """Get list of available scenario files"""
        scenario_dir = Path("simulation")
        if scenario_dir.exists():
            return list(scenario_dir.glob("*.json"))
        return []
    
    def update(self):
        """Get one reading and update history"""
        # Read sensors
        sensor_data = self.sensor.read_sensors()
        if sensor_data is None:
            return None
        
        # Calculate elapsed time
        current_time = time.time()
        if self.last_update:
            elapsed = current_time - self.last_update
        else:
            elapsed = self.calculator.config["sampling_interval_ms"] / 1000
        self.last_update = current_time
        
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
        
        # Create reading record
        reading = {
            "timestamp": datetime.now(),
            "voltage": sensor_data["voltage"],
            "current": sensor_data["current"],
            "power_factor": sensor_data["power_factor"],
            "real_power_w": power_data["real_power_w"],
            "apparent_power_va": power_data["apparent_power_va"],
            "reactive_power_var": power_data["reactive_power_var"],
            "total_energy_kwh": energy_data["total_energy_kwh"],
            "daily_energy_kwh": energy_data["daily_energy_kwh"],
            "cost_rs": energy_data["total_cost_rs"],
            "temperature": sensor_data["temperature"],
            "frequency": sensor_data["frequency"],
            "alerts": triggered_alerts,
            "progress": progress,
            "simulation_name": self.sensor.get_simulation_name(),
            "appliances": self.sensor.get_appliance_breakdown()
        }
        
        # Add to history
        self.history.append(reading)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return reading
    
    def get_history_df(self):
        """Convert history to DataFrame"""
        if not self.history:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.history)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df


def main():
    """Main dashboard function"""
    
    # Initialize dashboard
    if "dashboard" not in st.session_state:
        st.session_state.dashboard = EnergyDashboard()
    
    dashboard = st.session_state.dashboard
    
    # Header
    st.title("🏠 Smart Home Energy Monitoring System")
    st.markdown("*Real-time Virtual Simulation | No Hardware Required*")
    
    # Sidebar
    with st.sidebar:
        st.header("🎮 Control Panel")
        
        # Scenario selection
        st.subheader("Simulation Scenarios")
        scenarios = dashboard.get_available_scenarios()
        
        if scenarios:
            scenario_names = [s.name for s in scenarios]
            selected_name = st.selectbox("Select Scenario", scenario_names)
            
            if st.button("🚀 Start Simulation", use_container_width=True):
                selected_scenario = [s for s in scenarios if s.name == selected_name][0]
                dashboard.load_scenario(str(selected_scenario))
                st.success(f"Started: {selected_name}")
                st.rerun()
        else:
            st.warning("No scenario files found in 'simulation/' directory")
        
        st.divider()
        
        # System info
        st.subheader("📊 System Info")
        st.metric("Electricity Rate", f"₹{dashboard.calculator.normal_rate}/kWh")
        st.metric("Peak Rate", f"₹{dashboard.calculator.peak_rate}/kWh")
        st.info(f"Peak Hours: {dashboard.calculator.config['peak_hours_start']:02d}:00 - {dashboard.calculator.config['peak_hours_end']:02d}:00")
        
        st.divider()
        
        # Controls
        st.subheader("⚙️ Controls")
        if st.button("🔄 Reset Totals", use_container_width=True):
            dashboard.calculator.reset()
            st.success("Totals reset!")
        
        auto_refresh = st.checkbox("Auto Refresh", value=True)
        refresh_rate = st.slider("Refresh Rate (seconds)", 1, 5, 2, disabled=not auto_refresh)
    
    # Main content - two columns
    col1, col2 = st.columns(2)
    
    # Get current reading
    reading = dashboard.update()
    
    if reading:
        # Column 1 - Live Metrics
        with col1:
            st.subheader("📈 Live Metrics")
            
            # Metrics row
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Voltage", f"{reading['voltage']:.1f} V", 
                         delta=f"{reading['voltage']-230:.1f}")
            with m2:
                st.metric("Current", f"{reading['current']:.2f} A")
            with m3:
                st.metric("Power", f"{reading['real_power_w']:.0f} W")
            with m4:
                st.metric("Power Factor", f"{reading['power_factor']:.2f}")
            
            # Second row of metrics
            m5, m6, m7, m8 = st.columns(4)
            with m5:
                st.metric("Total Energy", f"{reading['total_energy_kwh']:.3f} kWh")
            with m6:
                st.metric("Today's Energy", f"{reading['daily_energy_kwh']:.3f} kWh")
            with m7:
                st.metric("Total Cost", f"₹{reading['cost_rs']:.2f}")
            with m8:
                st.metric("Frequency", f"{reading['frequency']:.1f} Hz")
            
            # Temperature
            temp_color = "normal" if reading['temperature'] < 50 else "inverse"
            st.metric("Sensor Temperature", f"{reading['temperature']:.1f} °C", 
                     delta="High!" if reading['temperature'] > 60 else None,
                     delta_color="inverse")
        
        # Column 2 - Simulation Status
        with col2:
            st.subheader("🎬 Simulation Status")
            
            progress = reading['progress']
            st.progress(progress, text=f"Scenario: {reading['simulation_name']}")
            
            if reading['alerts']:
                st.warning(f"⚠️ {len(reading['alerts'])} Active Alert(s)")
                for alert in reading['alerts']:
                    if alert['severity'] == 'CRITICAL':
                        st.error(alert['message'])
                    else:
                        st.warning(alert['message'])
            else:
                st.success("✓ No Active Alerts")
            
            # Active appliances
            if reading['appliances']:
                st.subheader("📱 Active Appliances")
                for app in reading['appliances']:
                    st.markdown(f"• **{app['name']}** x{app['quantity']} → {app['power_w']:.0f}W")
            else:
                st.info("No active appliances (idle mode)")
        
        # Row 2 - Charts
        st.subheader("📊 Live Power Chart")
        
        # Create history dataframe
        df = dashboard.get_history_df()
        
        if not df.empty:
            # Power over time chart
            fig = make_subplots(rows=2, cols=1, 
                               subplot_titles=("Power Consumption (W)", "Current (A)"),
                               vertical_spacing=0.15)
            
            fig.add_trace(
                go.Scatter(x=df["timestamp"], y=df["real_power_w"],
                          mode='lines', name='Power (W)',
                          line=dict(color='#ff6b6b', width=2)),
                row=1, col=1
            )
            
            # Add threshold lines
            warning_threshold = dashboard.calculator.config["power_threshold_warning"]
            critical_threshold = dashboard.calculator.config["power_threshold_critical"]
            
            fig.add_hline(y=warning_threshold, line_dash="dash", 
                         line_color="orange", row=1, col=1,
                         annotation_text="Warning")
            fig.add_hline(y=critical_threshold, line_dash="dash",
                         line_color="red", row=1, col=1,
                         annotation_text="Critical")
            
            fig.add_trace(
                go.Scatter(x=df["timestamp"], y=df["current"],
                          mode='lines', name='Current (A)',
                          line=dict(color='#4ecdc4', width=2)),
                row=2, col=1
            )
            
            fig.update_layout(height=500, showlegend=True,
                             title_font_size=14)
            fig.update_xaxes(title_text="Time", row=2, col=1)
            fig.update_yaxes(title_text="Watts", row=1, col=1)
            fig.update_yaxes(title_text="Amperes", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Energy and Cost chart
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Energy Consumption")
                energy_df = df[["timestamp", "total_energy_kwh"]].copy()
                fig_energy = px.area(energy_df, x="timestamp", y="total_energy_kwh",
                                     title="Cumulative Energy (kWh)",
                                     color_discrete_sequence=['#95e77e'])
                fig_energy.update_layout(showlegend=False)
                st.plotly_chart(fig_energy, use_container_width=True)
            
            with col2:
                st.subheader("💰 Cost Accumulation")
                cost_df = df[["timestamp", "cost_rs"]].copy()
                fig_cost = px.area(cost_df, x="timestamp", y="cost_rs",
                                   title="Total Cost (₹)",
                                   color_discrete_sequence=['#ffd93d'])
                fig_cost.update_layout(showlegend=False)
                st.plotly_chart(fig_cost, use_container_width=True)
            
            # Recent readings table
            with st.expander("📋 Recent Readings"):
                recent_df = df.tail(20).copy()
                recent_df["timestamp"] = recent_df["timestamp"].dt.strftime("%H:%M:%S")
                recent_df = recent_df[["timestamp", "voltage", "current", "real_power_w", 
                                       "total_energy_kwh", "cost_rs"]]
                recent_df.columns = ["Time", "Voltage(V)", "Current(A)", 
                                    "Power(W)", "Energy(kWh)", "Cost(₹)"]
                st.dataframe(recent_df, use_container_width=True)
            
            # Monthly projection
            st.subheader("📅 Monthly Projection")
            monthly = dashboard.calculator.estimate_monthly_bill()
            
            proj_col1, proj_col2, proj_col3 = st.columns(3)
            with proj_col1:
                st.metric("Projected Monthly Energy", f"{monthly['projected_monthly_kwh']} kWh")
            with proj_col2:
                st.metric("Projected Monthly Cost", f"₹{monthly['projected_monthly_cost_rs']}")
            with proj_col3:
                st.metric("Average Daily Usage", f"{monthly['average_daily_kwh']} kWh")
        
        # Auto-refresh
        if auto_refresh:
            time.sleep(refresh_rate)
            st.rerun()
    
    else:
        st.info("💡 No simulation running. Select a scenario from the sidebar to start.")
        
        # Show available scenarios
        st.subheader("Available Scenarios")
        scenarios = dashboard.get_available_scenarios()
        if scenarios:
            for scenario in scenarios:
                with open(scenario, 'r') as f:
                    import json
                    data = json.load(f)
                    st.markdown(f"**{data['name']}**")
                    st.caption(f"Duration: {data['duration_seconds']} seconds | Appliances: {len(data['appliance_schedule'])}")
                    st.markdown("---")
        else:
            st.warning("No scenario files found. Create JSON files in the 'simulation/' directory.")


if __name__ == "__main__":
    main()