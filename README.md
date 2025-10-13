# ScrubPy

[![PyPI version](https://badge.fury.io/py/scrubpy.svg)](https://badge.fury.io/py/scrubpy)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Introduction

ScrubPy is a comprehensive Python library for intelligent data cleaning and preprocessing. It provides multiple interfaces including a web application, CLI tools, and AI-powered chat assistance to help data scientists, analysts, and researchers transform messy datasets into clean, analysis-ready formats. The library combines automated quality analysis with intelligent suggestions to streamline the data preparation workflow.

## Key Features

- **Multi-Interface Support**: Web GUI (Streamlit), Command Line Interface (CLI), and Interactive Chat Assistant
- **AI-Powered Analysis**: Integration with Large Language Models for intelligent data cleaning recommendations
- **Comprehensive Quality Assessment**: Automated detection of missing values, duplicates, outliers, and data type inconsistencies
- **Smart Cleaning Operations**: Automated and guided data cleaning with preview capabilities
- **Professional Reporting**: Generate detailed PDF reports and export cleaned datasets

## Architecture Overview

ScrubPy follows a modular architecture where users can interact through multiple interfaces (Web, CLI, Chat) that all utilize the same core data processing engine. The workflow starts with data loading through the core module, followed by quality analysis using the quality analyzer, interactive cleaning operations with preview capabilities, and finally export of cleaned data with comprehensive reporting. The AI components provide intelligent suggestions throughout the process.

## Installation

Install ScrubPy using pip:

```bash
pip install scrubpy
```

For AI features, install with additional dependencies:

```bash
pip install scrubpy[ai]
```

## Module Documentation

### Core Module (`scrubpy.core`)

The core module provides fundamental data loading and cleaning operations:

- `load_dataset(file_path)`: Intelligent data loading with automatic format detection for CSV, JSON, Excel, and Parquet files
- `get_dataset_summary(df)`: Comprehensive dataset overview including shape, column types, and basic statistics
- `remove_duplicates(df, method)`: Advanced duplicate detection with configurable strategies
- `fill_missing_values(df, method, columns)`: Multiple imputation methods including mean, median, mode, and forward/backward fill
- `detect_outliers(df, method)`: Statistical outlier detection using IQR, Z-score, and isolation forest methods
- `convert_data_types(df)`: Automatic data type optimization and conversion

### Quality Analyzer Module (`scrubpy.quality_analyzer`)

Intelligent quality assessment system:

- `SmartDataQualityAnalyzer`: Main analyzer class providing comprehensive quality scoring
- `analyze_quality(df)`: Complete quality analysis returning issue detection and recommendations
- `QualityIssue` dataclass: Structured representation of detected data quality issues
- Quality scoring algorithms for completeness, consistency, validity, and uniqueness metrics

### CLI Module (`scrubpy.cli`)

Interactive command-line interface:

- Rich terminal interface with progress indicators and colored output
- Interactive dataset selection and preview capabilities
- Step-by-step guided cleaning workflow
- Export options for cleaned datasets and quality reports

### Web Interface (`scrubpy.web`)

Modern Streamlit-based web application:

- Drag-and-drop file upload with format validation
- Real-time data preview with pagination
- Interactive quality dashboard with visual indicators
- One-click cleaning operations with preview capabilities
- Export functionality for multiple formats

## Usage Examples

### Basic Data Cleaning

```python
import scrubpy

# Load your dataset
df = scrubpy.load_dataset("data.csv")

# Analyze data quality
analyzer = scrubpy.SmartDataQualityAnalyzer()
quality_report = analyzer.analyze_quality(df)

# Clean the data
clean_df = scrubpy.remove_duplicates(df)
clean_df = scrubpy.fill_missing_values(clean_df, method="mean", numeric_only=True)
clean_df = scrubpy.detect_outliers(clean_df, method="iqr")
```

### Command Line Interface
```bash
# Launch interactive CLI
scrubpy

# Follow the interactive prompts to clean your data
```

### Web Interface Usage

```bash
# Start the web application
scrubpy-web

# Navigate to http://localhost:8501 in your browser
# Upload your dataset and follow the interactive cleaning workflow
```

### AI Chat Assistant

```bash
# Start chat mode with your dataset
scrubpy-chat data.csv

# Interact with the AI assistant using natural language:
# "What quality issues does my data have?"
# "Remove duplicates and handle missing values"
# "Generate a quality report"
```

## API Reference

### Core Functions

```python
import scrubpy

# Data loading
df = scrubpy.load_dataset(file_path, **kwargs)

# Quality analysis
analyzer = scrubpy.SmartDataQualityAnalyzer()
issues = analyzer.analyze_quality(df)

# Data cleaning operations
clean_df = scrubpy.remove_duplicates(df, method='exact')
clean_df = scrubpy.fill_missing_values(df, method='mean')
outliers = scrubpy.detect_outliers(df, method='iqr')
```

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, Linux
- **Memory**: 2GB minimum (4GB recommended for large datasets)
- **Storage**: 100MB for installation

## Contributing

We welcome contributions to ScrubPy! Please follow these guidelines:

1. Fork the repository and create a feature branch
2. Write tests for new functionality
3. Ensure code follows PEP 8 style guidelines
4. Submit a pull request with a clear description of changes

### Development Setup

```bash
git clone https://github.com/username/scrubpy.git
cd scrubpy
pip install -e ".[dev]"
pytest tests/
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with pandas and numpy for efficient data processing
- Streamlit for the modern web interface
- Typer and Rich for enhanced CLI experience
- OpenAI for AI-powered features

---

## What’s Next?
We plan to add smart visual exports, column intelligence, and eventually ML-powered cleaning.

---

## Why This Exists
Sometimes you just need a quick tool to clean and inspect your data without writing boilerplate pandas code. ScrubPy helps you do that, even if you're not a data wizard.

---

## 📚 License
MIT

---

Made with ❤️ by a student learning to make tools that help others.

