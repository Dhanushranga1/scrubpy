# 📖 ScrubPy API Reference Documentation

> **Complete reference for all ScrubPy modules, classes, and functions**

## Table of Contents
- [Core Module](#core-module)
- [Quality Analyzer](#quality-analyzer)  
- [Column Insights](#column-insights)
- [Smart Imputation](#smart-imputation)
- [LLM Utils](#llm-utils)
- [Template System](#template-system)
- [Advanced Features](#advanced-features)
- [Web Interface Components](#web-interface-components)
- [CLI Commands](#cli-commands)

---

## Core Module (`scrubpy.core`)

### Dataset Operations

#### `load_dataset(filepath: str) -> pd.DataFrame | None`
**Purpose**: Safely load CSV files with error handling
```python
from scrubpy.core import load_dataset

df = load_dataset("data.csv")
if df is not None:
    print(f"Loaded {len(df)} rows")
```

#### `get_dataset_summary(df: pd.DataFrame) -> str`
**Purpose**: Generate comprehensive dataset overview
```python
summary = get_dataset_summary(df)
print(summary)
# Output: Rows, columns, missing values, duplicates, memory usage
```

#### `save_dataset(df: pd.DataFrame, dataset: str) -> pd.DataFrame`
**Purpose**: Save cleaned dataset with smart versioning
```python
# Automatically creates cleaned_data_1.csv, cleaned_data_2.csv, etc.
save_dataset(df, "data.csv")
```

### Data Cleaning Operations

#### `drop_missing_values(df: pd.DataFrame) -> pd.DataFrame`
**Purpose**: Remove rows with missing values (with confirmation for >20% missing)
```python
clean_df = drop_missing_values(df)
# Interactive confirmation if >20% data would be lost
```

#### `fill_missing_values(df: pd.DataFrame, value: Any) -> pd.DataFrame`
**Purpose**: Fill missing values with specified value
```python
# Fill with custom value
filled_df = fill_missing_values(df, "N/A")
filled_df = fill_missing_values(df, df.mean())  # numeric mean
```

#### `remove_duplicates(df: pd.DataFrame) -> pd.DataFrame`
**Purpose**: Remove duplicate rows
```python
deduped_df = remove_duplicates(df)
```

#### `standardize_text(df: pd.DataFrame, column: str) -> pd.DataFrame`
**Purpose**: Standardize text column (lowercase, trimmed)
```python
clean_df = standardize_text(df, "name_column")
```

#### `fix_column_names(df: pd.DataFrame) -> pd.DataFrame`
**Purpose**: Standardize column names (lowercase, underscores)
```python
# "First Name" -> "first_name", "  Age  " -> "age"
clean_df = fix_column_names(df)
```

#### `convert_column_types(df: pd.DataFrame, column: str, dtype: str) -> pd.DataFrame`
**Purpose**: Safe column type conversion
```python
# Supported types: 'integer', 'float', 'string', 'datetime', 'category', 'boolean'
df = convert_column_types(df, "age", "integer")
df = convert_column_types(df, "date", "datetime")  
df = convert_column_types(df, "is_active", "boolean")
```

#### `remove_outliers(df: pd.DataFrame, column: str, method: str = "zscore", **kwargs) -> pd.DataFrame`
**Purpose**: Remove outliers using various methods
```python
# Method options: 'zscore', 'iqr', 'percentile'
clean_df = remove_outliers(df, "salary", method="zscore")
clean_df = remove_outliers(df, "age", method="iqr", iqr_factor=1.5)
clean_df = remove_outliers(df, "score", method="percentile", lower_pct=0.01, upper_pct=0.99)
```

---

## Quality Analyzer (`scrubpy.quality_analyzer`)

### QualityIssue Class
```python
@dataclass
class QualityIssue:
    column: str          # Column with issue
    issue_type: str      # Type: 'missing_data', 'duplicates', 'outliers', etc.
    severity: str        # 'low', 'medium', 'high', 'critical'
    description: str     # Human-readable description
    suggested_fix: str   # Recommended action
    affected_rows: int   # Number of affected rows
    confidence: float    # Confidence level (0.0-1.0)
```

### SmartDataQualityAnalyzer Class

#### `__init__(df: pd.DataFrame)`
**Purpose**: Initialize analyzer with dataset
```python
from scrubpy.quality_analyzer import SmartDataQualityAnalyzer

analyzer = SmartDataQualityAnalyzer(df)
```

#### `analyze_all() -> Dict[str, Any]`
**Purpose**: Run comprehensive quality analysis
```python
report = analyzer.analyze_all()
# Returns: issues, quality_score, recommendations, column_profiles
```

#### `get_quality_score(df: pd.DataFrame = None) -> Tuple[float, List[QualityIssue]]`
**Purpose**: Get overall quality score (0-100) and issues list
```python
score, issues = analyzer.get_quality_score()
print(f"Quality Score: {score}/100")
for issue in issues:
    print(f"⚠️ {issue.column}: {issue.description}")
```

### Analysis Methods

#### `_analyze_missing_patterns()`
**Purpose**: Detect missing data patterns and severity
- Identifies columns with >50% missing (critical)
- Finds consecutive missing values (data collection issues)
- Suggests appropriate imputation strategies

#### `_analyze_duplicates()`  
**Purpose**: Detect duplicate patterns
- Full row duplicates
- Partial duplicates in key columns
- ID column duplicate analysis

#### `_analyze_outliers()`
**Purpose**: Statistical outlier detection
- Z-score based detection
- IQR method for robust detection
- Context-aware thresholds

#### `_analyze_business_rules()`
**Purpose**: Domain-specific validation
- Email format validation
- Phone number format checking
- Date range validation

---

## 🧠 Column Insights (`scrubpy.column_insights`)

### `get_column_insights(df: pd.DataFrame) -> Dict[str, Any]`
**Purpose**: Automatically detect column roles and characteristics
```python
from scrubpy.column_insights import get_column_insights

insights = get_column_insights(df)
print(insights)
```

**Returns:**
```python
{
    "column_roles": {
        "email": "contact",
        "first_name": "personal", 
        "age": "numeric",
        "is_active": "boolean"
    },
    "data_types": {
        "email": "object",
        "age": "int64"
    },
    "quality_metrics": {
        "email": {"completeness": 0.95, "uniqueness": 0.88}
    },
    "suggested_transformations": {
        "email": ["validate_format", "standardize_case"]
    }
}
```

### Column Role Detection
The system identifies columns as:
- **personal**: Names, gender, age, etc.
- **contact**: Email, phone, address
- **geographic**: Location, city, coordinates
- **financial**: Price, salary, revenue
- **temporal**: Dates, timestamps
- **categorical**: Categories, status
- **numeric**: Measurements, scores
- **boolean**: Flags, yes/no values

### `suggest_transformations(df: pd.DataFrame, column: str) -> List[str]`
**Purpose**: Recommend specific transformations for a column
```python
suggestions = suggest_transformations(df, "email_address")
# Returns: ["validate_email", "lowercase", "trim_whitespace"]
```

---

## Smart Imputation (`scrubpy.smart_imputation`)

### SmartImputer Class

#### `__init__(df: pd.DataFrame, strategy: str = "auto")`
**Purpose**: Initialize smart imputation engine
```python
from scrubpy.smart_imputation import SmartImputer

# Auto-detect best strategy per column
imputer = SmartImputer(df, strategy="auto")

# Force specific strategy
imputer = SmartImputer(df, strategy="iterative")
```

#### Available Strategies:
- **"auto"**: Automatically selects best method per column
- **"mean"**: Mean/mode imputation
- **"median"**: Median imputation for numeric columns
- **"iterative"**: ML-based iterative imputation (requires sklearn)
- **"knn"**: K-nearest neighbors imputation
- **"forward_fill"**: Forward fill for time series

#### `impute_all(columns: List[str] = None) -> pd.DataFrame`
**Purpose**: Impute missing values across all or specified columns
```python
# Impute all columns
clean_df = imputer.impute_all()

# Impute specific columns
clean_df = imputer.impute_all(columns=["age", "salary"])
```

#### `impute_column(column: str, strategy: str = None) -> pd.Series`
**Purpose**: Impute single column with specific strategy
```python
# Use column-specific strategy
imputed_series = imputer.impute_column("age", strategy="median")
```

#### `get_imputation_report() -> Dict[str, Any]`
**Purpose**: Get detailed report of imputation performed
```python
report = imputer.get_imputation_report()
# Returns: methods used, success rates, quality improvements
```

---

## 💬 LLM Utils (`scrubpy.llm_utils`)

### LLMAssistant Class

#### `__init__(df: pd.DataFrame, column_insights_data: Dict = None, model: str = "mistral", use_ollama: bool = True)`
**Purpose**: Initialize AI assistant for dataset analysis
```python
from scrubpy.llm_utils import LLMAssistant

assistant = LLMAssistant(
    df=df,
    model="mistral",
    use_ollama=True
)
```

#### `analyze_dataset(question: str = None) -> str`
**Purpose**: Get AI analysis of the dataset
```python
# General analysis
analysis = assistant.analyze_dataset()

# Specific question
analysis = assistant.analyze_dataset("What are the main quality issues?")
```

#### `suggest_cleaning_operations() -> List[Dict[str, Any]]`
**Purpose**: Get AI-recommended cleaning operations
```python
suggestions = assistant.suggest_cleaning_operations()
for suggestion in suggestions:
    print(f"Operation: {suggestion['operation']}")
    print(f"Reason: {suggestion['reason']}")
    print(f"Code: {suggestion['code']}")
```

#### `generate_cleaning_code(operations: List[str]) -> str`
**Purpose**: Generate Python code for cleaning operations
```python
code = assistant.generate_cleaning_code([
    "remove_duplicates",
    "fill_missing_values", 
    "standardize_text"
])
print(code)  # Executable pandas code
```

### EnhancedLLMClient Class

#### `__init__(model: str = "mistral", base_url: str = None)`
**Purpose**: Lower-level LLM client for custom queries
```python
from scrubpy.llm_utils import EnhancedLLMClient

client = EnhancedLLMClient(model="mistral")
response = client.query("Analyze this data pattern: ...")
```

---

## 🗂️ Template System (`scrubpy.template_system`)

### TemplateManager Class

#### `__init__(template_dir: str = "templates")`
**Purpose**: Manage cleaning templates
```python
from scrubpy.template_system import TemplateManager

manager = TemplateManager()
```

#### `get_available_templates() -> Dict[str, CleaningTemplate]`
**Purpose**: List all available templates
```python
templates = manager.get_available_templates()
for name, template in templates.items():
    print(f"{name}: {template.description}")
```

#### `load_template(name: str) -> CleaningTemplate`
**Purpose**: Load specific template
```python
template = manager.load_template("customer_data")
```

#### `apply_template(df: pd.DataFrame, template: CleaningTemplate) -> pd.DataFrame`
**Purpose**: Apply template operations to dataset
```python
cleaned_df = manager.apply_template(df, template)
```

#### `create_template_from_operations(name: str, operations: List[Dict]) -> CleaningTemplate`
**Purpose**: Create new template from operation list
```python
operations = [
    {"type": "drop_missing", "columns": ["id"]},
    {"type": "standardize_text", "columns": ["name"]}
]
template = manager.create_template_from_operations("my_template", operations)
```

### CleaningTemplate Class
```python
@dataclass
class CleaningTemplate:
    name: str
    description: str
    operations: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_date: datetime
```

---

## Advanced Features

### Enhanced File Handler (`scrubpy.enhanced_file_handler`)

#### ExcelHandler Class
```python
from scrubpy.enhanced_file_handler import ExcelHandler

handler = ExcelHandler()
sheets = handler.get_sheet_names("workbook.xlsx")
df = handler.read_sheet("workbook.xlsx", sheet_name="Data")
```

### Large File Handler (`scrubpy.large_file_handler`)

#### LargeFileHandler Class
```python
from scrubpy.large_file_handler import LargeFileHandler

handler = LargeFileHandler(chunk_size=10000)
# Process file in chunks to avoid memory issues
processed_df = handler.process_large_file("huge_file.csv")
```

### Advanced Text Cleaning (`scrubpy.advanced_text_cleaning`)

#### PhoneNumberStandardizer Class
```python
from scrubpy.advanced_text_cleaning import PhoneNumberStandardizer

standardizer = PhoneNumberStandardizer()
clean_phone = standardizer.standardize_phone("+1-555-123-4567")
# Returns: "+15551234567"
```

#### Email Validation
```python
from scrubpy.advanced_text_cleaning import validate_email_series

# Validate entire column
is_valid = validate_email_series(df["email"])
valid_emails = df[is_valid]
```

---

## 🌐 Web Interface Components

### Streamlit App Structure (`web_app.py`)

#### Key Functions:
- `render_professional_header()`: UI header with branding
- `render_data_quality_score(df)`: Quality score visualization
- `get_ai_insights(df, analysis_type)`: AI-powered insights
- `render_cleaning_operations(df)`: Interactive cleaning tools

### Usage in Custom Apps:
```python
import streamlit as st
from scrubpy.core import load_dataset, get_dataset_summary
from scrubpy.quality_analyzer import SmartDataQualityAnalyzer

# Your custom Streamlit app
uploaded_file = st.file_uploader("Upload CSV")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Use ScrubPy components
    st.write(get_dataset_summary(df))
    
    analyzer = SmartDataQualityAnalyzer(df)
    score, issues = analyzer.get_quality_score()
    st.metric("Quality Score", f"{score}/100")
```

---

## CLI Commands (`scrubpy.enhanced_cli`)

### Main Commands

#### `scrubpy clean [OPTIONS]`
**Purpose**: Interactive cleaning workflow
```bash
python -m scrubpy clean --help
```

#### `scrubpy analyze <file> [OPTIONS]`
**Purpose**: Quick dataset analysis
```bash
python -m scrubpy analyze data.csv --format json
```

#### `scrubpy chat <file> [OPTIONS]`
**Purpose**: Start AI chat session
```bash  
python -m scrubpy chat data.csv --model mistral
```

#### `scrubpy template [SUBCOMMAND]`
**Purpose**: Template management
```bash
python -m scrubpy template list
python -m scrubpy template apply customer_data data.csv
```

### Configuration Management
```bash
# View current config
python -m scrubpy config show

# Set config values
python -m scrubpy config set llm.model "mistral"
python -m scrubpy config set cleaning.auto_preview false
```

---

## 🧪 Testing Utilities

### Import Validation
```python
# Test all imports work
from test_imports import test_smart_imputation, test_quality_analyzer
test_smart_imputation()  # Returns True if working
test_quality_analyzer()  # Returns True if working
```

### Feature Testing
```python
# Test enhanced features
from test_enhanced_features import test_enhanced_features
test_enhanced_features()  # Comprehensive feature test
```

---

## 🔍 Error Handling Patterns

### Graceful Degradation
```python
try:
    from scrubpy.llm_utils import EnhancedLLMClient
    llm_available = True
except ImportError:
    llm_available = False
    # Fallback to non-AI features

if llm_available:
    client = EnhancedLLMClient()
else:
    st.warning("AI features unavailable - install Ollama")
```

### Safe Operations
```python
# All core operations include error handling
try:
    clean_df = remove_outliers(df, "salary")
except Exception as e:
    st.error(f"Outlier removal failed: {e}")
    clean_df = df  # Keep original data
```

---

## Performance Considerations

### Memory Management
- Use `LargeFileHandler` for files >1GB
- Process in chunks when possible
- Monitor memory usage with built-in utilities

### Optimization Tips
- Enable auto_preview=False for large datasets
- Use specific column lists instead of applying to all columns
- Cache expensive operations (quality analysis, column insights)

---

**This API reference covers all major ScrubPy components. For implementation examples, see the test files and web interface code.**