"""
Setup script for Smart Home Energy Monitoring System
"""

from setuptools import setup, find_packages

setup(
    name="smart-home-energy-monitor",
    version="1.0.0",
    author="Student Developer",
    description="IoT-based Smart Home Energy Monitoring System",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.29.0",
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "plotly>=5.17.0",
        "fpdf>=1.7.2",
        "python-dotenv>=1.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.13.0",
        "pytest>=7.4.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "energy-monitor=src.main:main",
            "energy-dashboard=dashboard.streamlit_app:main",
        ],
    },
)