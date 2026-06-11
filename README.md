# 🏠 Smart Home Energy Monitoring System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![IoT](https://img.shields.io/badge/IoT-Enabled-orange.svg)](https://en.wikipedia.org/wiki/Internet_of_things)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey)]()

> **An IoT-based Smart Home Energy Monitoring System that measures real-time electrical consumption, visualizes usage patterns, and triggers alerts to reduce energy waste and costs.**

---

## 📖 Overview

### What is this project?

A **complete IoT-based energy monitoring system** that simulates electrical sensors, calculates power/energy/cost in real-time, displays data on a live dashboard, triggers alerts for high usage, and generates PDF reports. **No physical hardware required!**

### Problem It Solves

| Problem | Solution |
|---------|----------|
| ❌ High electricity bills | ✅ Real-time cost tracking & monthly projections |
| ❌ No visibility into usage | ✅ Live dashboard with per-appliance breakdown |
| ❌ Energy waste | ✅ Alerts for high consumption & peak hours |
| ❌ Manual tracking | ✅ Automated CSV/SQLite logging & PDF reports |

### Why This Matters

- **For Homeowners:** Save 15-25% on electricity bills by identifying wasteful appliances
- **For Students:** Learn IoT concepts, data visualization, and energy analytics
- **For Businesses:** Monitor energy consumption across facilities
- **For the Planet:** Reduce carbon footprint through energy efficiency

---

## ✨ Features

### Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🔌 **Virtual Sensors** | Simulates current/voltage/power factor | ✅ Complete |
| 📊 **Live Dashboard** | Real-time gauges, charts, and metrics | ✅ Complete |
| ⚠️ **Smart Alerts** | Threshold-based notifications | ✅ Complete |
| 💰 **Cost Calculation** | Peak/off-peak pricing support | ✅ Complete |
| 📈 **Energy Analytics** | Power, energy, cost trends | ✅ Complete |
| 📑 **PDF Reports** | Daily, weekly, monthly reports | ✅ Complete |
| 💾 **Data Logging** | CSV, SQLite, JSON formats | ✅ Complete |
| 🎮 **Simulation Scenarios** | Multiple usage patterns | ✅ Complete |
| 📱 **Appliance Tracking** | Per-appliance consumption | ✅ Complete |
| 🔔 **Email Alerts** | Optional email notifications | ✅ Complete |

### Advanced Features

- **Peak Hour Detection**: Automatically identifies high-rate periods
- **Monthly Projections**: Estimate monthly bills based on usage
- **Efficiency Score**: Rate your energy efficiency (0-100)
- **Historical Analysis**: Compare usage across days/weeks
- **Export Options**: CSV, JSON, PDF, SQLite

---

## 🚀 Installation

### Prerequisites

- **Python 3.9 or higher** - [Download Python](https://python.org/downloads)
- **Git** (optional) - [Download Git](https://git-scm.com)

### Step 1: Clone or Download

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Smart-Home-Energy-Monitoring-System.git
# Navigate to project folder
cd Smart-Home-Energy-Monitoring-System

Step 2: Create Virtual Environment (Recommended)
Windows:
python -m venv venv
venv\Scripts\activate
Linux/Mac:
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies
pip install -r requirements.txt
Or install individually:
pip install streamlit pandas numpy plotly fpdf python-dotenv matplotlib seaborn pytest

Step 4: Generate Sample Data
python generate_data.py

Step 5: Verify Installationash
python -c "import streamlit; print('✅ Installation successful!')"
```

## 📁 Project Structure
```
Smart-Home-Energy-Monitoring-System/
│
├── 📁 src/                          # Core source code
│   ├── main.py                      # Main entry point
│   ├── sensor_simulator.py          # Virtual sensor simulation
│   ├── energy_calculator.py         # Power/energy/cost calculations
│   ├── alert_manager.py             # Threshold monitoring & alerts
│   ├── data_logger.py               # CSV/SQLite/JSON logging
│   └── report_generator.py          # PDF report generation
│
├── 📁 dashboard/                    # Streamlit web dashboard
│   └── streamlit_app.py             # Complete dashboard application
│
├── 📁 config/                       # Configuration files
│   ├── settings.json                # System settings
│   └── appliances.json              # Appliance definitions
│
├── 📁 simulation/                   # Simulation scenarios
│   ├── normal_day.json              # Regular usage pattern
│   ├── high_usage.json              # High consumption period
│   ├── overload.json                # Critical overload condition
│   └── multi_appliance.json         # Multiple appliances schedule
│
├── 📁 data/                         # Generated data (auto-created)
│   ├── raw_logs/                    # CSV log files
│   ├── daily_reports/               # JSON/TXT summaries
│   └── energy_data.db               # SQLite database
│
├── 📁 outputs/                      # Generated outputs (auto-created)
│   ├── reports/                     # PDF reports
│   └── charts/                      # PNG chart images
│
├── 📁 circuit_diagram/              # Circuit diagrams
│   ├── circuit_diagram.txt          # ASCII circuit diagram
│   ├── wiring_diagram.txt           # Pin connections
│   └── README.md                    # Diagram documentation
│
├── 📁 tests/                        # Unit tests
│   └── test_calculations.py         # Test energy calculations
│
├── 📁 images/                       # Screenshots for README
│
├── 📄 requirements.txt              # Python dependencies
├── 📄 .gitignore                    # Git ignore rules
├── 📄 README.md                     # This file
├── 📄 LICENSE                       # MIT License
│
├── 📄 generate_circuit_diagram.py   # Generate circuit diagrams
├── 📄 generate_data.py              # Generate sample data
├── 📄 generate_outputs.py           # Generate reports/charts
│
├── 📄 run.bat                       # Windows launcher
└── 📄 run.sh                        # Linux/Mac launcher
```

## ⚙️ How It Works
System Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        SIMULATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   sensor_simulator.py          energy_calculator.py            │
│   ┌──────────────────┐         ┌──────────────────┐           │
│   │ • Current (0-15A)│────────▶│ • P = V × I × PF │           │
│   │ • Voltage(210-250│         │ • E = P × t      │           │
│   │ • Power Factor   │         │ • C = E × Rate   │           │
│   │ • Temperature    │         └────────┬─────────┘           │
│   └────────┬─────────┘                  │                     │
│            │                            │                     │
│            ▼                            ▼                     │
│   ┌─────────────────┐          ┌─────────────────┐           │
│   │  alert_manager  │          │  data_logger    │           │
│   │ • Threshold     │          │ • CSV           │           │
│   │ • Overload      │          │ • SQLite        │           │
│   │ • Voltage       │          │ • JSON          │           │
│   └────────┬────────┘          └────────┬────────┘           │
│            │                            │                     │
│            └────────────┬───────────────┘                     │
│                         ▼                                     │
│                  ┌─────────────┐                              │
│                  │  Streamlit  │                              │
│                  │  Dashboard  │                              │
│                  └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow
- Sensor Simulation → Generates realistic electrical data
- Energy Calculation → Computes power, energy, cost
- Alert Check → Compares against thresholds
- Data Logging → Saves to CSV/SQLite/JSON
- Dashboard Update → Visualizes in real-time
- Report Generation → Creates PDF summaries

## Calculation Formulas
Formula	Description
- Power (W) = Voltage × Current × Power Factor	Real power consumption
- Energy (kWh) = Power (W) × Time (h) / 1000	Energy over time
- Cost (₹) = Energy (kWh) × Rate (₹/kWh)	Electricity cost
- Apparent Power (VA) = Voltage × Current	Total power delivered

📊 Dashboard
Main Dashboard Components
Component	Description
Live Metrics	Voltage, Current, Power, Power Factor
Energy Tracking	Total Energy, Daily Energy, Total Cost
Status Indicators	Normal/Warning/Critical states
Active Appliances	Currently running appliances
Alert Panel	Recent alerts and warnings
Power Chart	Real-time power consumption graph
Energy Chart	Cumulative energy over time
Cost Chart	Running total cost
Monthly Projection	Estimated monthly bill

## Dashboard Controls
- Scenario Selection → Choose simulation scenario
- Start Simulation → Begin selected scenario
- Reset Totals → Reset energy/cost counters
- Auto Refresh → Automatic dashboard updates
- Refresh Rate → 1-5 seconds interval

## 🛠️ Tech Stack
Languages & Frameworks
| Technology | Purpose | Version |
| Python | Core logic, calculations | 3.9+ |
| Streamlit | Web dashboard | 1.28+ |
| Pandas | Data manipulation | 2.0+ |
| NumPy | Numerical operations | 1.23+ |
| Plotly | Interactive charts | 5.17+ |
| Matplotlib | Static charts | 3.6+ |
| FPDF | PDF generation | 1.7+ |

## Development Tools
| Tool | Purpose |
| VS Code | IDE |
| Git | Version control |
| GitHub | Repository hosting |

## 🔮 Future Improvements
Short Term (1-2 weeks)
- Mobile app (React Native/Flutter)
- Email/SMS notifications
- Export to Excel format
- More simulation scenarios

Medium Term (1-2 months)
- AI-based load forecasting
- Solar energy integration
- Voice assistant support (Alexa/Google Home)
- Multi-user access
- Real hardware support (ESP32)

Long Term (3-6 months)
- Cloud deployment (AWS/Azure)
- Machine learning anomaly detection
- Automated appliance control
- Energy saving recommendations
- Integration with utility APIs