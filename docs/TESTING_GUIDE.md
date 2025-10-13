# 🧪 ScrubPy Testing & Quality Guide

> **Comprehensive guide to testing strategies, quality assurance, and development standards for ScrubPy**

## Table of Contents
- [Testing Philosophy](#testing-philosophy)
- [Test Structure Overview](#test-structure-overview)
- [Testing Strategies by Component](#testing-strategies-by-component)
- [Quality Assurance Process](#quality-assurance-process)
- [Code Quality Standards](#code-quality-standards)
- [Continuous Integration](#continuous-integration)
- [Performance Testing](#performance-testing)
- [Documentation Standards](#documentation-standards)

---

## Testing Philosophy

### Core Principles
1. **Test Early, Test Often**: Every new feature should have corresponding tests
2. **Fail Fast**: Tests should quickly identify breaking changes
3. **Real-World Scenarios**: Test with actual data patterns and edge cases
4. **User Experience Focus**: Test from the user's perspective
5. **Performance Awareness**: Monitor performance impact of changes

### Testing Pyramid
```
    ┌─────────────────┐
    │   E2E Tests     │  ← Interface integration, full workflows
    │   (Few, Slow)   │
    ├─────────────────┤
    │ Integration     │  ← Module interactions, API contracts
    │ Tests (Some)    │  
    ├─────────────────┤
    │  Unit Tests     │  ← Individual functions, core logic
    │  (Many, Fast)   │
    └─────────────────┘
```

---

## 🗂️ Test Structure Overview

### Current Test Files
```
tests/
├── test_imports.py              # Import validation and dependency checks
├── test_enhanced_features.py    # Phase 1&2 features testing  
├── test_enhanced_functionality.py # Core functionality testing
├── test_llm_integration.py      # AI features testing
├── test_full_integration.py     # End-to-end workflow testing
└── conftest.py                  # 📝 Test configuration (TODO)
```

### Test Categories

#### 1. Import Tests (`test_imports.py`)
**Purpose**: Validate all modules import correctly and dependencies are available
```python
def test_smart_imputation():
    """Test SmartImputer functionality"""
    try:
        from scrubpy.smart_imputation import SmartImputer, SKLEARN_AVAILABLE
        assert SKLEARN_AVAILABLE, "sklearn not available"
        
        # Test instantiation
        test_data = create_test_dataframe()
        imputer = SmartImputer(test_data)
        assert imputer is not None
        
        return True
    except Exception as e:
        pytest.fail(f"SmartImputer test failed: {e}")
```

#### 2. Feature Tests (`test_enhanced_features.py`)
**Purpose**: Test specific features implemented in development phases
```python
def test_template_system():
    """Test template loading and application"""
    from scrubpy.template_system import TemplateManager
    
    manager = TemplateManager()
    templates = manager.get_available_templates()
    
    assert len(templates) > 0, "No templates available"
    
    # Test template application
    template_name = list(templates.keys())[0]
    template = manager.load_template(template_name)
    
    test_df = create_test_dataframe()
    result_df = manager.apply_template(test_df, template)
    
    assert result_df is not None
    assert len(result_df) <= len(test_df)  # May remove rows
```

#### 3. Integration Tests (`test_llm_integration.py`)
**Purpose**: Test AI features and external integrations
```python
def test_llm_availability():
    """Test if LLM services are available"""
    try:
        from scrubpy.llm_utils import EnhancedLLMClient
        
        client = EnhancedLLMClient()
        is_available = client.test_connection()
        
        if not is_available:
            pytest.skip("LLM service not available")
        
        # Test basic query
        response = client.query("Hello, can you respond?")
        assert len(response) > 0
        
    except ImportError:
        pytest.skip("LLM utilities not available")
```

---

## 🧩 Testing Strategies by Component

### 1. Core Data Operations Testing

#### Test Data Generation
```python
import pandas as pd
import numpy as np
from typing import Dict, Any

def create_test_dataframe(scenario: str = "mixed") -> pd.DataFrame:
    """Generate test DataFrames for various scenarios"""
    
    scenarios = {
        "clean": {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "email": ["alice@test.com", "bob@test.com", "charlie@test.com"]
        },
        "missing": {
            "name": ["Alice", None, "Charlie"],
            "age": [25, np.nan, 35],
            "email": ["alice@test.com", "", "charlie@test.com"]
        },
        "duplicates": {
            "name": ["Alice", "Alice", "Bob"],
            "age": [25, 25, 30],
            "email": ["alice@test.com", "alice@test.com", "bob@test.com"]
        },
        "outliers": {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 999],  # 999 is outlier
            "salary": [50000, 55000, 9999999]  # 9999999 is outlier
        },
        "mixed": {
            "name": ["Alice", None, "Bob", "Bob"],
            "age": [25, np.nan, 30, 30],
            "email": ["alice@test.com", "", "invalid-email", "bob@test.com"],
            "salary": [50000, 55000, 9999999, 52000]
        }
    }
    
    return pd.DataFrame(scenarios.get(scenario, scenarios["mixed"]))

def create_large_test_dataframe(rows: int = 100000) -> pd.DataFrame:
    """Generate large test DataFrame for performance testing"""
    np.random.seed(42)  # Reproducible results
    
    return pd.DataFrame({
        'id': range(rows),
        'name': [f"Person_{i}" for i in range(rows)],
        'age': np.random.normal(35, 10, rows),
        'salary': np.random.normal(60000, 15000, rows),
        'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], rows)
    })
```

#### Core Function Testing Template
```python
def test_core_operation(operation_func, test_scenarios: List[str]):
    """Generic test template for core operations"""
    
    for scenario in test_scenarios:
        # Arrange
        test_df = create_test_dataframe(scenario)
        original_shape = test_df.shape
        
        # Act
        try:
            result_df = operation_func(test_df.copy())
        except Exception as e:
            pytest.fail(f"Operation failed on {scenario} data: {e}")
        
        # Assert
        assert isinstance(result_df, pd.DataFrame), "Result should be DataFrame"
        assert len(result_df.columns) == len(test_df.columns), "Column count changed unexpectedly"
        
        # Scenario-specific assertions
        if scenario == "clean":
            assert result_df.shape == original_shape, "Clean data shouldn't change"
        elif scenario == "missing" and "drop_missing" in operation_func.__name__:
            assert len(result_df) < len(test_df), "Should remove rows with missing data"

# Example usage
def test_drop_missing_values():
    """Test missing value removal"""
    from scrubpy.core import drop_missing_values
    test_core_operation(drop_missing_values, ["clean", "missing", "mixed"])
```

### 2. Quality Analyzer Testing

```python
def test_quality_analyzer_comprehensive():
    """Comprehensive quality analyzer testing"""
    from scrubpy.quality_analyzer import SmartDataQualityAnalyzer, QualityIssue
    
    # Test with known quality issues
    problematic_df = create_test_dataframe("mixed")
    
    analyzer = SmartDataQualityAnalyzer(problematic_df)
    score, issues = analyzer.get_quality_score()
    
    # Validate score range
    assert 0 <= score <= 100, f"Quality score {score} outside valid range"
    
    # Validate issues structure
    assert isinstance(issues, list), "Issues should be a list"
    
    for issue in issues:
        assert isinstance(issue, QualityIssue), "Each issue should be QualityIssue instance"
        assert issue.column in problematic_df.columns, f"Issue column {issue.column} not in DataFrame"
        assert issue.severity in ['low', 'medium', 'high', 'critical'], f"Invalid severity: {issue.severity}"
        assert 0 <= issue.confidence <= 1, f"Confidence {issue.confidence} outside valid range"
    
    # Test specific issue detection
    issue_types = [issue.issue_type for issue in issues]
    assert 'missing_data' in issue_types, "Should detect missing data"
    assert 'duplicates' in issue_types, "Should detect duplicates"

def test_quality_score_consistency():
    """Test quality score consistency across runs"""
    test_df = create_test_dataframe("mixed")
    
    analyzer1 = SmartDataQualityAnalyzer(test_df)
    analyzer2 = SmartDataQualityAnalyzer(test_df.copy())
    
    score1, _ = analyzer1.get_quality_score()
    score2, _ = analyzer2.get_quality_score()
    
    assert abs(score1 - score2) < 0.1, "Quality scores should be consistent"
```

### 3. AI Integration Testing

```python
def test_llm_integration_graceful_degradation():
    """Test AI features work with and without LLM availability"""
    from scrubpy.llm_utils import LLMAssistant
    
    test_df = create_test_dataframe("mixed")
    
    try:
        # Test with LLM available
        assistant = LLMAssistant(test_df, model="mistral")
        response = assistant.analyze_dataset("What issues do you see?")
        
        assert isinstance(response, str), "Response should be string"
        assert len(response) > 0, "Response should not be empty"
        
    except Exception as e:
        # Test graceful degradation
        pytest.skip(f"LLM not available, skipping AI tests: {e}")

def test_chat_assistant_conversation_flow():
    """Test chat assistant maintains conversation context"""
    from scrubpy.chat_assistant import DatasetChatAssistant
    
    test_df = create_test_dataframe("mixed")
    assistant = DatasetChatAssistant(test_df)
    
    # Test initialization
    assert assistant.df is not None
    assert assistant.conversation_history == []
    
    # Test context building (without LLM)
    context = assistant.get_dataset_context_summary()
    assert "rows" in context.lower()
    assert "columns" in context.lower()
```

### 4. Performance Testing

```python
import time
import psutil
import pytest

class PerformanceTester:
    """Performance testing utilities"""
    
    def __init__(self):
        self.metrics = {}
    
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure function execution time"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        self.metrics['execution_time'] = execution_time
        
        return result, execution_time
    
    def measure_memory_usage(self, func, *args, **kwargs):
        """Measure memory usage during function execution"""
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        result = func(*args, **kwargs)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        self.metrics['memory_used'] = memory_used
        return result, memory_used

def test_large_file_performance():
    """Test performance with large datasets"""
    from scrubpy.core import get_dataset_summary, drop_missing_values
    
    # Create large test dataset
    large_df = create_large_test_dataframe(50000)  # 50k rows
    
    tester = PerformanceTester()
    
    # Test summary generation performance
    _, summary_time = tester.measure_execution_time(get_dataset_summary, large_df)
    assert summary_time < 5.0, f"Dataset summary took too long: {summary_time}s"
    
    # Test cleaning operation performance  
    _, cleaning_time = tester.measure_execution_time(drop_missing_values, large_df)
    assert cleaning_time < 10.0, f"Cleaning operation took too long: {cleaning_time}s"
    
    # Test memory usage
    _, memory_used = tester.measure_memory_usage(drop_missing_values, large_df)
    assert memory_used < 500, f"Used too much memory: {memory_used}MB"

@pytest.mark.slow
def test_streaming_performance():
    """Test streaming operations for very large files"""
    from scrubpy.large_file_handler import LargeFileHandler
    
    # This test would use actual large files or mock streaming
    handler = LargeFileHandler(chunk_size=1000)
    
    # Test chunk processing
    test_chunks = [create_test_dataframe("mixed") for _ in range(10)]
    
    start_time = time.time()
    processed_chunks = []
    
    for chunk in test_chunks:
        processed_chunk = handler.process_chunk(chunk, operations=['drop_missing'])
        processed_chunks.append(processed_chunk)
    
    total_time = time.time() - start_time
    
    assert total_time < 5.0, f"Chunk processing took too long: {total_time}s"
    assert len(processed_chunks) == len(test_chunks), "All chunks should be processed"
```

### 5. Interface Testing

```python
def test_web_interface_components():
    """Test web interface components in isolation"""
    import streamlit as st
    from web_app import render_data_quality_score, get_ai_insights
    
    test_df = create_test_dataframe("mixed")
    
    # Test quality score rendering (mock streamlit)
    with patch('streamlit.metric') as mock_metric:
        render_data_quality_score(test_df)
        mock_metric.assert_called()
    
    # Test AI insights (with graceful degradation)
    try:
        insights = get_ai_insights(test_df, "overview")
        assert isinstance(insights, str)
    except Exception:
        # Should gracefully handle AI unavailability
        pass

def test_cli_interface_menu_structure():
    """Test CLI interface menu structure"""
    from scrubpy.enhanced_cli import ScrubPyConfig
    
    config = ScrubPyConfig()
    assert isinstance(config.config, dict)
    
    # Test config loading/saving
    test_value = "test_model"
    config.set("llm.model", test_value)
    assert config.get("llm.model") == test_value
```

---

## 🏆 Quality Assurance Process

### 1. Pre-Commit Checklist
```bash
# Before committing code, run these checks:

# 1. Run all tests
python -m pytest tests/ -v

# 2. Check code formatting (if using black)
black --check scrubpy/

# 3. Run type checking (if using mypy)
mypy scrubpy/

# 4. Check import sorting (if using isort)
isort --check-only scrubpy/

# 5. Run linting (if using flake8)
flake8 scrubpy/

# 6. Test manual functionality
python main.py --cli  # Basic functionality test
```

### 2. Code Review Guidelines

#### Review Criteria
- [ ] **Functionality**: Does the code do what it's supposed to do?
- [ ] **Tests**: Are there appropriate tests for new functionality?
- [ ] **Documentation**: Is the code well-documented?
- [ ] **Performance**: Are there any obvious performance issues?
- [ ] **Security**: Are there any security vulnerabilities?
- [ ] **Style**: Does the code follow project conventions?

#### Review Template
```markdown
## Code Review Checklist

### Functionality ✅/❌
- [ ] Feature works as described
- [ ] Edge cases handled appropriately
- [ ] Error handling is appropriate

### Testing ✅/❌
- [ ] Unit tests added for new functionality
- [ ] Tests cover edge cases
- [ ] All tests pass locally

### Documentation ✅/❌
- [ ] Docstrings added/updated
- [ ] README updated if needed
- [ ] API documentation updated

### Code Quality ✅/❌
- [ ] Code follows project style guidelines
- [ ] No obvious performance issues
- [ ] No security vulnerabilities
- [ ] Appropriate logging added

### Comments
[Reviewer feedback here]
```

### 3. Release Testing Process

#### Pre-Release Testing
1. **Full Test Suite**: Run all tests with fresh environment
2. **Manual Testing**: Test all three interfaces (Web, CLI, Chat)
3. **Performance Testing**: Run with large datasets
4. **Integration Testing**: Test with real-world data files
5. **Documentation Review**: Ensure all docs are up-to-date

#### Release Validation
```bash
# Create clean environment for testing
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt

# Test installation process
python setup.py install

# Test entry points
python -m scrubpy --help
python main.py --help

# Test with sample data
python main.py --analyze sample_data.csv
```

---

## 📏 Code Quality Standards

### 1. Python Code Style

#### Function Documentation
```python
def analyze_missing_patterns(df: pd.DataFrame, threshold: float = 0.05) -> Dict[str, Any]:
    """
    Analyze patterns in missing data across DataFrame columns.
    
    This function identifies columns with missing data and categorizes
    the severity based on the percentage of missing values.
    
    Args:
        df (pd.DataFrame): Input DataFrame to analyze
        threshold (float, optional): Threshold for significant missing data. 
                                   Defaults to 0.05 (5%).
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - 'missing_columns': List of columns with missing data
            - 'severity_counts': Count of issues by severity level
            - 'recommendations': List of recommended actions
            
    Raises:
        ValueError: If DataFrame is empty or invalid
        
    Example:
        >>> df = pd.DataFrame({'A': [1, None, 3], 'B': [1, 2, 3]})
        >>> result = analyze_missing_patterns(df)
        >>> print(result['missing_columns'])
        ['A']
    """
    # Implementation here
    pass
```

#### Class Documentation
```python
class SmartDataQualityAnalyzer:
    """
    Comprehensive data quality analyzer with intelligent pattern detection.
    
    This class provides advanced data quality assessment capabilities including
    missing value analysis, duplicate detection, outlier identification, and
    business rule validation.
    
    Attributes:
        df (pd.DataFrame): The DataFrame being analyzed
        issues (List[QualityIssue]): List of detected quality issues
        quality_score (float): Overall quality score (0-100)
        
    Example:
        >>> analyzer = SmartDataQualityAnalyzer(df)
        >>> score, issues = analyzer.get_quality_score()
        >>> print(f"Quality Score: {score}/100")
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the analyzer with a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame to analyze
            
        Raises:
            ValueError: If DataFrame is empty or None
        """
        pass
```

#### Error Handling Standards
```python
def safe_operation_template(df: pd.DataFrame, operation_params: Dict) -> pd.DataFrame:
    """Template for safe operations with proper error handling"""
    
    # 1. Input validation
    if df is None or df.empty:
        raise ValueError("DataFrame cannot be None or empty")
    
    # 2. Parameter validation
    required_params = ['param1', 'param2']
    for param in required_params:
        if param not in operation_params:
            raise ValueError(f"Required parameter '{param}' missing")
    
    # 3. Operation with error handling
    try:
        # Main operation logic here
        result_df = df.copy()  # Always work on copy
        
        # Validate result
        if result_df is None:
            raise RuntimeError("Operation produced None result")
            
        return result_df
        
    except Exception as e:
        # Log error with context
        logger.error(f"Operation failed: {e}", extra={
            'df_shape': df.shape,
            'operation_params': operation_params
        })
        
        # Re-raise with more context
        raise RuntimeError(f"Operation failed: {e}") from e
```

### 2. Testing Standards

#### Test Naming Conventions
```python
# Good test names
def test_remove_outliers_with_zscore_method():
    """Test outlier removal using Z-score method"""
    pass

def test_quality_analyzer_handles_empty_dataframe():
    """Test quality analyzer error handling with empty DataFrame"""
    pass

def test_template_system_loads_customer_data_template():
    """Test template system can load customer data template"""
    pass

# ❌ Poor test names
def test_outliers():
    pass

def test_analyzer():
    pass

def test_template():
    pass
```

#### Test Structure (AAA Pattern)
```python
def test_smart_imputer_fills_missing_values():
    """Test SmartImputer correctly fills missing values"""
    
    # Arrange
    test_df = pd.DataFrame({
        'A': [1, None, 3, None, 5],
        'B': [10, 20, None, 40, 50]
    })
    expected_non_null_count = len(test_df)
    
    # Act
    imputer = SmartImputer(test_df, strategy="mean")
    result_df = imputer.impute_all()
    
    # Assert
    assert result_df.isnull().sum().sum() == 0, "All missing values should be filled"
    assert len(result_df) == expected_non_null_count, "Row count should remain same"
    assert result_df['A'].notna().all(), "Column A should have no missing values"
    assert result_df['B'].notna().all(), "Column B should have no missing values"
```

---

## 🔄 Continuous Integration

### GitHub Actions Workflow Template
```yaml
# .github/workflows/tests.yml
name: ScrubPy Tests

on:
  push:
    branches: [ main, phase-3 ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=scrubpy --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### Local Testing Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black mypy flake8 isort

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Create pytest configuration
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    llm: marks tests that require LLM services
```

---

## Performance Testing

### Benchmarking Framework
```python
import time
import pandas as pd
from typing import Callable, Dict, Any
import matplotlib.pyplot as plt

class PerformanceBenchmark:
    """Framework for performance benchmarking"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_operation(self, 
                          operation: Callable,
                          test_data_sizes: List[int],
                          iterations: int = 3) -> Dict[str, List[float]]:
        """Benchmark operation across different data sizes"""
        
        times = []
        memory_usage = []
        
        for size in test_data_sizes:
            test_df = create_large_test_dataframe(size)
            
            # Run multiple iterations
            iteration_times = []
            for _ in range(iterations):
                start_time = time.time()
                result = operation(test_df)
                end_time = time.time()
                iteration_times.append(end_time - start_time)
            
            # Average time
            avg_time = sum(iteration_times) / len(iteration_times)
            times.append(avg_time)
            
            # Memory usage (approximate)
            memory_mb = test_df.memory_usage(deep=True).sum() / 1024 / 1024
            memory_usage.append(memory_mb)
        
        return {
            'sizes': test_data_sizes,
            'times': times,
            'memory': memory_usage
        }
    
    def plot_results(self, benchmark_results: Dict, operation_name: str):
        """Plot benchmark results"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Time vs Size
        ax1.plot(benchmark_results['sizes'], benchmark_results['times'], 'bo-')
        ax1.set_xlabel('Dataset Size (rows)')
        ax1.set_ylabel('Execution Time (seconds)')
        ax1.set_title(f'{operation_name} - Performance')
        ax1.grid(True)
        
        # Memory vs Size
        ax2.plot(benchmark_results['sizes'], benchmark_results['memory'], 'ro-')
        ax2.set_xlabel('Dataset Size (rows)')
        ax2.set_ylabel('Memory Usage (MB)')
        ax2.set_title(f'{operation_name} - Memory Usage')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'benchmark_{operation_name.lower().replace(" ", "_")}.png')
        plt.show()

# Usage example
def test_performance_benchmarks():
    """Run performance benchmarks for key operations"""
    from scrubpy.core import get_dataset_summary, drop_missing_values
    from scrubpy.quality_analyzer import SmartDataQualityAnalyzer
    
    benchmark = PerformanceBenchmark()
    
    # Test different data sizes
    sizes = [1000, 5000, 10000, 25000, 50000]
    
    # Benchmark core operations
    summary_results = benchmark.benchmark_operation(
        get_dataset_summary, sizes, iterations=3
    )
    
    quality_analysis = lambda df: SmartDataQualityAnalyzer(df).analyze_all()
    quality_results = benchmark.benchmark_operation(
        quality_analysis, sizes, iterations=2
    )
    
    # Performance assertions
    for i, size in enumerate(sizes):
        if size <= 10000:
            assert summary_results['times'][i] < 1.0, f"Summary too slow for {size} rows"
        if size <= 5000:
            assert quality_results['times'][i] < 5.0, f"Quality analysis too slow for {size} rows"
```

---

## 📚 Documentation Standards

### 1. Module Documentation
Each module should have a header describing its purpose:
```python
"""
Advanced Text Cleaning Module
=============================

This module provides sophisticated text cleaning and standardization capabilities
for common data types including phone numbers, email addresses, and names.

Key Features:
- Phone number standardization with international format support
- Email validation with detailed error reporting  
- Fuzzy duplicate detection using multiple algorithms
- Address standardization for US addresses

Usage Example:
    >>> from scrubpy.advanced_text_cleaning import PhoneNumberStandardizer
    >>> standardizer = PhoneNumberStandardizer()
    >>> clean_phone = standardizer.standardize_phone("(555) 123-4567")
    >>> print(clean_phone)  # "+15551234567"

Dependencies:
    - phonenumbers: For international phone number handling
    - fuzzywuzzy: For fuzzy string matching (optional)
    
Author: ScrubPy Team
Version: 1.0.0
"""
```

### 2. README Updates
When adding new features, update relevant sections:
- Features list
- Usage examples  
- Installation requirements
- Architecture diagrams

### 3. API Documentation
Maintain comprehensive API docs with examples:
- All public functions documented
- Parameter types and descriptions
- Return value specifications
- Usage examples
- Error conditions

---

## Testing Checklist for New Features

### Before Implementation
- [ ] Write tests first (TDD approach)
- [ ] Define expected behavior clearly
- [ ] Consider edge cases and error conditions
- [ ] Plan performance implications

### During Implementation  
- [ ] Run tests frequently during development
- [ ] Test with realistic data
- [ ] Verify error handling works correctly
- [ ] Check performance with large datasets

### Before Commit
- [ ] All new tests pass
- [ ] All existing tests still pass
- [ ] Code coverage maintained or improved
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated
- [ ] Manual testing completed

### Integration Testing
- [ ] Test with all three interfaces (Web, CLI, Chat)
- [ ] Verify backward compatibility
- [ ] Test with real-world datasets
- [ ] Validate AI integration (if applicable)

---

**This comprehensive testing and quality guide ensures ScrubPy maintains high standards while growing and evolving. Regular adherence to these practices will keep the codebase robust, performant, and maintainable.**