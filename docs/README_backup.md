# ScrubPy - Enhanced Smart Data Cleaning Assistant

An intelligent, conversation-driven data cleaning and analysis tool that combines automated insights with LLM-powered assistance.

## New Features & Improvements

### **Interactive Dataset Chat**
- **Natural Language Queries**: Ask questions about your data in plain English
- **Smart Context Awareness**: AI understands your dataset structure and provides relevant insights
- **Quick Commands**: Built-in shortcuts for common analysis tasks
- **Session Persistence**: Save and resume conversations

```bash
# Start a chat session with your dataset
python -m scrubpy.enhanced_cli chat data.csv

# Example queries:
# "What are the main data quality issues?"
# "Show me outliers in the price column"
# "Suggest cleaning steps for this dataset"
```

### 🔍 **Advanced Data Quality Analysis**
- **Comprehensive Scoring**: 100-point quality score with detailed breakdown
- **Pattern Detection**: Identifies missing data patterns, business rule violations
- **Smart Recommendations**: Prioritized suggestions based on impact and effort
- **Automated Reports**: JSON, YAML, and text export formats

```bash
# Run quality analysis
python -m scrubpy.enhanced_cli analyze data.csv --format json
```

### **Quick Clean Mode**
- **One-Command Cleaning**: Apply sensible defaults for common issues
- **Intelligent Type Detection**: Auto-convert numeric strings, dates
- **Batch Processing**: Clean multiple files simultaneously
- **Smart Defaults**: Handles duplicates, missing values, outliers automatically

```bash
# Quick clean with smart defaults
python -m scrubpy.enhanced_cli quick-clean data.csv --ops duplicates missing types

# Batch process multiple files
python -m scrubpy.enhanced_cli batch ./data/ --ops analyze insights
```

### 🧠 **Enhanced Column Intelligence**
- **Role Detection**: Automatically identifies column purposes (ID, categorical, monetary, etc.)
- **Business Rule Validation**: Detects invalid emails, ages, percentages
- **Transformation Suggestions**: Smart recommendations for each column type
- **Confidence Scoring**: Reliability metrics for all insights

### 🛠️ **Improved CLI Experience**
- **Multiple Entry Points**: Choose between full interactive mode or specific commands
- **Configuration Management**: Persistent settings for LLM models, output formats
- **Progress Indicators**: Visual feedback for long-running operations
- **Error Recovery**: Graceful handling of common issues

### 🤝 **Smart Imputation Engine**
- **Multiple Strategies**: KNN, Iterative (MICE), ML-based prediction
- **Pattern-Aware**: Considers missing data patterns when choosing methods
- **Correlation-Based**: Uses relationships between columns for better imputation
- **Validation**: Business rule compliance for imputed values

---

## Features

### Dataset Profiling
- Overview of rows, columns, memory usage
- Missing value analysis
- Duplicate detection
- Statistical summary of numeric columns (mean, median, std, skewness, outliers)
- Text column analysis (most common value, average word count, unique values)


### 🚮 Cleaning Tools
- Drop or fill missing values
- Remove duplicates
- Standardize text (lowercase + trim)
- Fix column names (spaces, lowercase)
- Convert column types safely
- Remove outliers (Z-score)
- Undo last change

### Export Profiling Report
- Generates detailed `.txt` report with insights
- Designed for human-readability and sharing

### 🎨 Interactive CLI UI
- Built with Rich and InquirerPy
- Provides preview before applying changes

---

## 📝 Usage

### 1. Clone this repo
```bash
git clone https://github.com/your-username/scrubpy.git
cd scrubpy
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run ScrubPy CLI
Make sure your dataset (CSV) is in the current folder.
```bash
PYTHONIOENCODING=utf-8 python -m scrubpy.cli
```

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

## ✨ What’s Next?
We plan to add smart visual exports, column intelligence, and eventually ML-powered cleaning.

---

## 🎉 Why This Exists
Sometimes you just need a quick tool to clean and inspect your data without writing boilerplate pandas code. ScrubPy helps you do that, even if you're not a data wizard.

---

## 📚 License
MIT

---

Made with ❤️ by a student learning to make tools that help others.

