# ScrubPy – The Smartest Data Cleaner (Phase 1)

>  A simple yet powerful command-line tool to help you clean and understand your datasets faster.

---

##  About
ScrubPy is a lightweight CLI tool that simplifies common data cleaning tasks for students, data analysts, and researchers. It doesn't aim to be revolutionary – just helpful, smart, and fast.

Phase 1 includes the core functionality: profiling, cleaning, previewing changes, and exporting reports.

---

##  Features

### Dataset Profiling
- Overview of rows, columns, memory usage
- Missing value analysis
- Duplicate detection
- Statistical summary of numeric columns (mean, median, std, skewness, outliers)
- Text column analysis (most common value, average word count, unique values)


###  Cleaning Tools
- Drop or fill missing values
- Remove duplicates
- Standardize text (lowercase + trim)
- Fix column names (spaces, lowercase)
- Convert column types safely
- Remove outliers (Z-score)
- Undo last change

###  Export Profiling Report
- Generates detailed `.txt` report with insights
- Designed for human-readability and sharing

###  Interactive CLI UI
- Built with Rich and InquirerPy
- Provides preview before applying changes

---

##  Usage

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

## What’s Next?
We plan to add smart visual exports, column intelligence, and eventually ML-powered cleaning.

---

##  Why This Exists
Sometimes you just need a quick tool to clean and inspect your data without writing boilerplate pandas code. ScrubPy helps you do that, even if you're not a data wizard.

---

##  License
MIT

---

Made with ❤️ by a student learning to make tools that help others.

