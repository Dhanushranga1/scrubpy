# ScrubPy: Intelligent Data Cleaning Tool

ScrubPy is a command-line tool designed to streamline data cleaning and preparation for analysis. It transforms messy datasets into analysis-ready formats with smart profiling and cleaning capabilities.

## Key Features

- **Dataset Profiling**: Comprehensive analysis including missing values, duplicates, statistics, and outliers
- **Cleaning Tools**: 
  - Handle missing values and duplicates
  - Standardize text and column names
  - Safe type conversion
  - Outlier removal
- **Reporting**:
  - Detailed text reports with cleaning suggestions
  - PDF EDA reports with visualizations
- **Interactive CLI**: Preview changes before applying with undo functionality

## Installation

```bash
git clone https://github.com/your-username/scrubpy.git
cd scrubpy
pip install -r requirements.txt
```
## Usage
```bash
Place your CSV file in the same directory before running.
PYTHONIOENCODING=utf-8 python -m scrubpy.cli
```

## License
    GNU General Public License v3.0

