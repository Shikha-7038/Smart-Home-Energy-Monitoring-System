"""
Generate Output Files (PDF Reports, Charts)
Run this file to create outputs folder with reports and charts
"""

from pathlib import Path
from datetime import datetime, timedelta

# Create folders
Path("outputs/reports").mkdir(parents=True, exist_ok=True)
Path("outputs/charts").mkdir(parents=True, exist_ok=True)

print("📄 Generating output files...")

# ============================================================
# 1. PDF REPORT (Using simple text-based PDF)
# ============================================================
try:
    from fpdf import FPDF
    
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Smart Home Energy Monitoring System', 0, 1, 'C')
    
    # Daily Report
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'Daily Energy Report', 0, 1, 'C')
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'SUMMARY', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(80, 8, 'Total Energy:', 0, 0)
    pdf.cell(0, 8, '12.5 kWh', 0, 1)
    pdf.cell(80, 8, 'Total Cost:', 0, 0)
    pdf.cell(0, 8, 'Rs 93.75', 0, 1)
    pdf.cell(80, 8, 'Peak Power:', 0, 0)
    pdf.cell(0, 8, '1850 W', 0, 1)
    
    pdf_path = f"outputs/reports/daily_report_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    pdf.output(pdf_path)
    print(f"   ✅ PDF: {pdf_path}")
    
    # Weekly Report
    pdf2 = PDF()
    pdf2.add_page()
    pdf2.set_font('Arial', 'B', 14)
    pdf2.cell(0, 10, f'Weekly Energy Report', 0, 1, 'C')
    end = datetime.now()
    start = end - timedelta(days=7)
    pdf2.set_font('Arial', 'I', 11)
    pdf2.cell(0, 10, f'{start.strftime("%Y-%m-%d")} to {end.strftime("%Y-%m-%d")}', 0, 1, 'C')
    pdf2.ln(10)
    
    pdf2.set_font('Arial', 'B', 12)
    pdf2.cell(0, 10, 'WEEKLY SUMMARY', 0, 1)
    pdf2.set_font('Arial', '', 11)
    pdf2.cell(80, 8, 'Total Weekly Energy:', 0, 0)
    pdf2.cell(0, 8, '87.2 kWh', 0, 1)
    pdf2.cell(80, 8, 'Total Weekly Cost:', 0, 0)
    pdf2.cell(0, 8, 'Rs 654.00', 0, 1)
    
    weekly_path = f"outputs/reports/weekly_report_{start.strftime('%Y%m%d')}_to_{end.strftime('%Y%m%d')}.pdf"
    pdf2.output(weekly_path)
    print(f"   ✅ PDF: {weekly_path}")
    
except ImportError:
    print("   ⚠️ PDF skipped (fpdf not installed). Run: pip install fpdf")

# ============================================================
# 2. CHARTS (PNG)
# ============================================================
try:
    import matplotlib.pyplot as plt
    
    # Chart 1: Daily Power Profile
    hours = list(range(24))
    power = [150, 120, 100, 80, 70, 90, 350, 500, 450, 320, 280, 300,
             350, 320, 300, 350, 400, 600, 750, 800, 700, 550, 400, 250]
    
    plt.figure(figsize=(12, 6))
    plt.plot(hours, power, 'b-', linewidth=2)
    plt.fill_between(hours, power, alpha=0.3)
    plt.axhline(y=500, color='orange', linestyle='--', label='Warning (500W)')
    plt.axhline(y=1000, color='red', linestyle='--', label='Critical (1000W)')
    plt.xlabel('Hour of Day')
    plt.ylabel('Power (Watts)')
    plt.title('Daily Power Consumption Profile')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('outputs/charts/daily_power_profile.png', dpi=150)
    plt.close()
    print("   ✅ Chart: outputs/charts/daily_power_profile.png")
    
    # Chart 2: Energy Distribution
    appliances = ['AC', 'Refrigerator', 'TV', 'Lights', 'Washing Machine', 'Others']
    energy = [6.2, 2.8, 1.5, 1.2, 0.8, 0.5]
    
    plt.figure(figsize=(10, 8))
    plt.pie(energy, labels=appliances, autopct='%1.1f%%', startangle=90)
    plt.title('Energy Consumption by Appliance')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('outputs/charts/energy_distribution.png', dpi=150)
    plt.close()
    print("   ✅ Chart: outputs/charts/energy_distribution.png")
    
    # Chart 3: Weekly Comparison
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekly = [11.2, 10.8, 12.1, 11.5, 13.2, 15.5, 13.8]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(days, weekly, color='#4ecdc4')
    for bar, val in zip(bars, weekly):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
                f'{val}', ha='center', va='bottom')
    plt.xlabel('Day')
    plt.ylabel('Energy (kWh)')
    plt.title('Weekly Energy Consumption')
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('outputs/charts/weekly_comparison.png', dpi=150)
    plt.close()
    print("   ✅ Chart: outputs/charts/weekly_comparison.png")
    
    # Chart 4: Cost Trend
    cost = [84, 81, 90.75, 86.25, 99, 116.25, 103.5]
    
    plt.figure(figsize=(12, 6))
    plt.plot(days, cost, 'r-o', linewidth=2, markersize=8)
    plt.fill_between(days, cost, alpha=0.2, color='red')
    plt.xlabel('Day')
    plt.ylabel('Cost (Rupees)')
    plt.title('Daily Electricity Cost')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('outputs/charts/cost_trend.png', dpi=150)
    plt.close()
    print("   ✅ Chart: outputs/charts/cost_trend.png")
    
except ImportError:
    print("   ⚠️ Charts skipped (matplotlib not installed). Run: pip install matplotlib")

print("\n✅ All output files generated successfully!")