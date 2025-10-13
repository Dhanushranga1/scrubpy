# ScrubPy Developer Onboarding Guide

> **Welcome to ScrubPy!** This comprehensive guide will get you from zero to contributing in 30 minutes.

## Table of Contents
- [Quick Setup](#quick-setup)
- [Project Architecture](#project-architecture)
- [Development Workflow](#development-workflow)
- [Code Organization](#code-organization)
- [Key Concepts](#key-concepts)
- [Testing Guidelines](#testing-guidelines)
- [Common Tasks](#common-tasks)

---

## 🏁 Quick Setup

### 1. Prerequisites
```bash
# Required
- Python 3.8+ 
- Git
- 4GB+ RAM (for large file processing)

# Optional but Recommended  
- VS Code with Python extension
- Ollama (for LLM features)
- Docker (for isolated testing)
```

### 2. Clone & Install
```bash
git clone https://github.com/Dhanushranga1/scrubpy.git
cd scrubpy
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
# Test all interfaces work
python main.py --help
python main.py --cli
python -c "from scrubpy.core import load_dataset; print('Core imports work')"
python -m pytest tests/ -v  # Run tests if available
```

### 4. First Run
```bash
# Try the web interface
python main.py
# Open http://localhost:8501 and upload sample_data.csv

# Try CLI interface  
python main.py --cli
# Select sample_data.csv and explore features
```

---

## 🏗️ Project Architecture

### High-Level Structure
```
scrubpy/
├── 🎮 Entry Points
│   ├── __main__.py          # Package entry (python -m scrubpy)
│   ├── main.py              # Multi-interface launcher
│   └── setup.py             # Package configuration
│
├── 🧠 Core Engine (scrubpy/)
│   ├── core.py              # Data cleaning operations
│   ├── quality_analyzer.py  # Quality assessment engine
│   ├── column_insights.py   # Smart column analysis  
│   ├── smart_imputation.py  # ML-based missing value handling
│   └── profiling.py         # Dataset profiling
│
├── 🎨 User Interfaces
│   ├── enhanced_cli.py      # Modern CLI (Typer-based)
│   ├── cli.py               # Legacy CLI (Rich-based)
│   ├── web_app.py           # Streamlit web interface
│   ├── enhanced_web_app.py  # Advanced web features
│   └── chat_assistant.py    # AI conversation interface
│
├── AI Integration
│   ├── llm_utils.py         # LLM client and utilities
│   └── chat_assistant.py    # Conversational interface
│
├── Advanced Features
│   ├── template_system.py   # Reusable cleaning workflows
│   ├── advanced_text_cleaning.py  # Phone/email/address cleaning
│   ├── large_file_handler.py     # Memory-efficient processing
│   └── enhanced_file_handler.py  # Excel multi-sheet support
│
├── Analysis & Reporting
│   ├── eda_analysis.py      # Exploratory data analysis
│   ├── smart_eda.py         # PDF report generation
│   └── export_profiling_report.py  # Quality reports
│
└── 🧪 Testing
    ├── test_imports.py      # Import validation
    ├── test_enhanced_features.py  # New features testing
    └── test_llm_integration.py   # AI features testing
```

### Data Flow Architecture
```
📥 Input Sources
  ├── CSV Files
  ├── Excel (Multi-sheet) 
  ├── Large Files (>1GB)
  └── Direct DataFrame

      ⬇️

🔍 Analysis Pipeline
  ├── Dataset Profiling (profiling.py)
  ├── Column Insights (column_insights.py)  
  ├── Quality Assessment (quality_analyzer.py)
  └── Pattern Detection (AI-powered)

      ⬇️

🧹 Cleaning Engine (core.py)
  ├── Missing Value Handling
  ├── Duplicate Detection
  ├── Outlier Removal
  ├── Text Standardization
  ├── Type Conversion
  └── Custom Transformations

      ⬇️

Output & Reports
  ├── Cleaned Dataset
  ├── Quality Reports (PDF/Text)
  ├── EDA Reports (PDF with plots)
  ├── Cleaning Templates (YAML)
  └── Code Generation (Python)
```

---

## 💼 Development Workflow

### Branching Strategy
```bash
main          # Production-ready code
├── phase-3   # Current development (AI features)
├── feature/* # New feature development
├── fix/*     # Bug fixes  
└── docs/*    # Documentation updates
```

### Development Process
1. **Create Feature Branch**
   ```bash
   git checkout -b feature/awesome-new-feature
   ```

2. **Make Changes** following our [Code Standards](#code-standards)

3. **Test Locally**
   ```bash
   python -m pytest tests/
   python main.py --cli  # Manual testing
   ```

4. **Update Documentation** if needed

5. **Submit Pull Request** with clear description

### Code Standards
```python
# Good: Clear function names and docstrings
def analyze_missing_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze patterns in missing data across columns.
    
    Args:
        df: Input DataFrame to analyze
        
    Returns:
        Dict containing missing data insights and recommendations
    """
    pass

# Good: Type hints and error handling
def load_dataset(filepath: Union[str, Path]) -> Optional[pd.DataFrame]:
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return None
```

---

## 📚 Key Concepts

### 1. Column Insights System
**Purpose**: Automatically detect what each column represents
```python
from scrubpy.column_insights import get_column_insights

# Analyzes column names, data patterns, and values
insights = get_column_insights(df)
# Returns: role predictions, data types, quality metrics
```

### 2. Quality Assessment Engine  
**Purpose**: Comprehensive data quality scoring
```python
from scrubpy.quality_analyzer import SmartDataQualityAnalyzer

analyzer = SmartDataQualityAnalyzer(df)
report = analyzer.analyze_all()
# Returns: issues list, quality score, recommendations
```

### 3. Template System
**Purpose**: Reusable cleaning workflows
```python
from scrubpy.template_system import TemplateManager

manager = TemplateManager()
template = manager.load_template("customer_data")
cleaned_df = manager.apply_template(df, template)
```

### 4. Smart Imputation
**Purpose**: AI-powered missing value handling
```python
from scrubpy.smart_imputation import SmartImputer

imputer = SmartImputer(df)
# Uses multiple strategies: statistical, ML, pattern-based
cleaned_df = imputer.impute_all()
```

---

## Common Development Tasks

### Adding a New Cleaning Operation

1. **Add Core Function** (`scrubpy/core.py`)
   ```python
   def my_new_cleaning_operation(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
       """Your new cleaning operation"""
       # Implementation here
       return df
   ```

2. **Add to CLI Menu** (`scrubpy/enhanced_cli.py`)
   ```python
   # Add to cleaning_operations menu
   @app.command()
   def my_operation():
       """CLI command for your operation"""
       pass
   ```

3. **Add to Web Interface** (`web_app.py`)
   ```python
   # Add to Streamlit sidebar
   if st.sidebar.button("My Operation"):
       result = my_new_cleaning_operation(df)
       st.success("Operation completed!")
   ```

4. **Add Tests** (`test_enhanced_features.py`)
   ```python
   def test_my_new_operation():
       """Test your new operation"""
       test_df = pd.DataFrame({"col": [1, 2, 3]})
       result = my_new_cleaning_operation(test_df)
       assert len(result) == 3  # Your assertions
   ```

### Adding a New Template

1. **Create YAML Template** (`templates/my_template.yaml`)
   ```yaml
   name: "My Data Template"
   description: "Template for my specific data type"
   operations:
     - type: "drop_missing"
       columns: ["important_col"]
     - type: "standardize_text" 
       columns: ["name_col"]
   ```

2. **Test Template** 
   ```python
   from scrubpy.template_system import TemplateManager
   manager = TemplateManager()
   template = manager.load_template("my_template")
   ```

### Integrating New AI Features

1. **Extend LLM Utils** (`scrubpy/llm_utils.py`)
   ```python
   class MyAIFeature:
       def analyze_data(self, df: pd.DataFrame) -> str:
           """Your AI analysis logic"""
           return self.llm_client.query("Analyze this data...")
   ```

2. **Add to Chat Interface** (`scrubpy/chat_assistant.py`)
   ```python
   # Add new command handling
   if "analyze patterns" in user_input.lower():
       feature = MyAIFeature()
       response = feature.analyze_data(self.df)
   ```

---

## 🧪 Testing Strategy

### Test Categories
1. **Import Tests** (`test_imports.py`)
   - Verify all modules import correctly
   - Check dependency availability

2. **Feature Tests** (`test_enhanced_features.py`) 
   - Test specific functionality
   - Edge cases and error handling

3. **Integration Tests** (`test_llm_integration.py`)
   - End-to-end workflows
   - Interface integration

### Running Tests
```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python test_imports.py

# Test with coverage
python -m pytest --cov=scrubpy tests/
```

---

## 🚨 Common Pitfalls & Solutions

### Import Issues
**Problem**: `ModuleNotFoundError: No module named 'scrubpy'`
```bash
# Solution: Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Or use relative imports within package
```

### Memory Issues with Large Files
**Problem**: Out of memory with large datasets
```python
# Solution: Use chunked processing
from scrubpy.large_file_handler import LargeFileHandler
handler = LargeFileHandler(chunk_size=10000)
```

### LLM Connection Issues  
**Problem**: AI features not working
```bash
# Check Ollama is running
ollama serve
ollama pull mistral

# Or use alternative provider in config
```

---

## 📖 Next Steps

1. **Read**: [API Reference](API_REFERENCE.md) for detailed function documentation
2. **Study**: [Architecture Deep Dive](ARCHITECTURE.md) for system internals  
3. **Practice**: Start with small bug fixes or feature enhancements
4. **Contribute**: Check our [Issues](https://github.com/Dhanushranga1/scrubpy/issues) for good first contributions

---

## 💬 Getting Help

- **Documentation**: Check existing `.md` files in repo
- **Code Examples**: Look at test files for usage patterns
- **Issues**: Create GitHub issue for bugs or questions
- **Discussions**: Use GitHub Discussions for general questions

**Happy Coding! 🎉**