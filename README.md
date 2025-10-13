# 🧹 ScrubPy – AI-Powered Data Cleaning Made Simple

[![PyPI version](https://badge.fury.io/py/scrubpy.svg)](https://badge.fury.io/py/scrubpy)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Transform messy data into clean, analysis-ready datasets with AI assistance, interactive web interface, and powerful CLI tools.**

---

## What is ScrubPy?

ScrubPy is an advanced data cleaning toolkit that combines AI-powered intelligence with user-friendly interfaces. Whether you're a data scientist, analyst, or researcher, ScrubPy helps you clean and understand your datasets faster than ever.

### Key Highlights
- **AI-Powered**: LLM integration for intelligent data cleaning suggestions
- **🌐 Web Interface**: Modern Streamlit-based GUI with drag-and-drop
- **💬 Chat Assistant**: Interactive AI guide for data cleaning workflows  
- **CLI Tools**: Rich terminal interface with progress indicators
- **Smart Analysis**: Automated EDA with quality scoring
- **Professional Reports**: Generate PDF reports and insights

---

## � Quick Start

### Installation

Install ScrubPy with a single command:

```bash
pip install scrubpy
```

### Usage Options

**🌐 Web Interface** (Recommended for beginners):
```bash
scrubpy-web
```

**💬 AI Chat Assistant**:
```bash
scrubpy-chat your_data.csv
```

**CLI Interface**:
```bash
scrubpy
```

---

## Features

### AI-Powered Intelligence
- **Smart Suggestions**: AI analyzes your data and recommends cleaning steps
- **Natural Language Processing**: Advanced text cleaning and normalization
- **Quality Scoring**: Automatic data quality assessment and insights
- **Pattern Recognition**: Detect and fix common data issues automatically

### 🌐 Modern Interfaces
- **Web App**: Drag-and-drop file upload with real-time previews
- **Chat Assistant**: Conversational AI guide for cleaning workflows
- **Rich CLI**: Beautiful terminal interface with progress bars and colors

### Advanced Analytics
- **Smart EDA**: Automated exploratory data analysis
- **Quality Reports**: Comprehensive data quality assessments
- **Visual Insights**: Generate correlation heatmaps and distributions
- **PDF Exports**: Professional reports for stakeholders

### Powerful Cleaning Tools
- **Missing Values**: Smart imputation strategies
- **Duplicates**: Advanced duplicate detection and removal
- **Outliers**: Statistical outlier detection and handling
- **Data Types**: Intelligent type inference and conversion
- **Text Processing**: Advanced text standardization and cleaning
- **Validation**: Email, phone number, and custom validation rules

---

## � Usage Examples

### Command Line Interface
```bash
# Launch interactive CLI
scrubpy

# Quick clean with default settings
scrubpy clean data.csv --output cleaned_data.csv

# Generate quality report
scrubpy analyze data.csv --report
```

### Python API
```python
import scrubpy as sp

# Load and analyze data
df = sp.load_data('messy_data.csv')
quality_score = sp.analyze_quality(df)

# AI-powered cleaning
cleaned_df = sp.smart_clean(df, ai_suggestions=True)

# Export results
sp.export_data(cleaned_df, 'cleaned_data.csv')
sp.generate_report(df, cleaned_df, 'quality_report.pdf')
```

---

## 🛠️ Installation & Setup

### System Requirements
- **Python**: 3.8 or higher
- **OS**: Windows, macOS, Linux
- **RAM**: 2GB minimum (4GB recommended for large datasets)

### Installing from PyPI
```bash
# Install latest stable version
pip install scrubpy

# Install with all AI features
pip install scrubpy[ai]

# Install development version
pip install scrubpy[dev]
```

### Verify Installation
```bash
scrubpy --version
scrubpy-web --help
scrubpy-chat --help
```

---

## 🏗️ Architecture

ScrubPy is built with modern Python practices and modular design:

```
scrubpy/
├── core.py              # Core data processing engine  
├── cli.py               # Rich CLI interface
├── chat_assistant.py    # AI chat interface
├── quality_analyzer.py  # Data quality assessment
├── llm_utils.py         # AI/LLM integration
├── eda_analysis.py      # Exploratory data analysis
├── validation.py        # Data validation rules
├── web/                 # Streamlit web interface
├── config/              # Configuration templates
└── utils/               # Utility functions
```

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/dhanushranga1/scrubpy.git
cd scrubpy
pip install -e .[dev]
```

### Running Tests
```bash
pytest tests/
```

---

## Performance

ScrubPy is optimized for performance:
- **Memory Efficient**: Processes large datasets with minimal RAM usage
- **Fast Processing**: Vectorized operations with pandas and numpy
- **Streaming Support**: Handle datasets larger than memory
- **Parallel Processing**: Multi-core support for intensive operations

---

## Use Cases

### Data Science Workflows
- **EDA**: Quick exploratory data analysis
- **Preprocessing**: Clean data before ML pipelines  
- **Quality Assessment**: Validate data quality metrics

### Business Analytics
- **CRM Data**: Clean customer databases
- **Sales Data**: Process transaction records
- **Survey Data**: Clean and standardize responses

### Research & Academia
- **Dataset Preparation**: Clean research datasets
- **Statistical Analysis**: Prepare data for statistical tests
- **Report Generation**: Create professional data quality reports

---

## 🔗 Links

- **Documentation**: [Full documentation and API reference](docs/)
- **GitHub**: [Source code and issues](https://github.com/dhanushranga1/scrubpy)
- **PyPI**: [Package on Python Package Index](https://pypi.org/project/scrubpy/)
- **Changelog**: [Release history and updates](CHANGELOG.md)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

ScrubPy is built on the shoulders of giants:
- **pandas** & **numpy** for data processing
- **Streamlit** for the beautiful web interface
- **Typer** & **Rich** for the modern CLI experience
- **scikit-learn** for machine learning utilities

---

**Made with ❤️ for the data community**

---

## 🌐 Folder Structure
```
scrubpy/
├── cli.py                    # Main CLI interface
├── core.py                   # Core cleaning logic
├── preview.py                # Preview operations before applying
├── profiling.py              # Dataset profiling & suggestions
├── export_profiling_report.py# Export detailed profiling reports
```

---

## 🛠️ Requirements
- Python 3.8+
- pandas
- numpy
- typer
- rich
- InquirerPy
- scipy

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

