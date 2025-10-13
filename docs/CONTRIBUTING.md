# 🤝 Contributing to ScrubPy

> **Welcome contributors! ScrubPy is built by the community, for the community.**

Thank you for your interest in contributing to ScrubPy! This guide will help you get started with contributing to our AI-powered data cleaning assistant.

## **Quick Contribution Guide**

### **Getting Started** (5 minutes)
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/scrubpy.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `pytest tests/`
5. Start coding! 🚀

### **Before You Submit**
- [ ] Tests pass: `pytest tests/`
- [ ] Code formatted: `black scrubpy/`
- [ ] No linting errors: `flake8 scrubpy/`
- [ ] Documentation updated (if needed)

---

## **Types of Contributions We Need**

### 🐛 **Bug Reports** (Always Welcome!)
Found something broken? Help us fix it!
- Use the GitHub Issues template
- Include steps to reproduce
- Share sample data (anonymized)
- Mention your environment (OS, Python version)

### ✨ **Feature Requests** (Community-Driven!)
Got ideas to make ScrubPy better?
- Check existing issues first
- Describe the use case clearly
- Propose implementation approach
- Consider multiple user types (web/CLI/chat users)

### **Code Contributions** (Most Impactful!)
Ready to code? Here's what we need most:

#### **High Priority Areas**
- **Performance**: Make large datasets faster to process
- **New Cleaning Operations**: Add domain-specific cleaning functions
- **UI/UX Improvements**: Make interfaces more intuitive
- **AI Integration**: Improve LLM integration and responses
- **Testing**: Increase test coverage and reliability

#### **Good First Issues** (Perfect for beginners)
- Documentation improvements
- Example dataset additions
- Error message enhancements
- Configuration options
- Minor bug fixes

---

## 🏗️ **Development Setup**

### **Prerequisites**
- Python 3.8 or higher
- Git for version control
- Basic knowledge of pandas and data cleaning concepts

### **Detailed Setup**
```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/scrubpy.git
cd scrubpy

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install pytest black flake8 mypy

# 5. Install ScrubPy in development mode
pip install -e .

# 6. Run tests to verify setup
pytest tests/ -v

# 7. Test all interfaces
python main.py --help  # CLI
python main.py  # Web (opens browser)
python main.py --chat sample_data.csv  # Chat (if LLM configured)
```

### **Development Dependencies**
```bash
# Code formatting
pip install black isort

# Linting
pip install flake8 pylint

# Type checking
pip install mypy

# Testing
pip install pytest pytest-cov pytest-mock

# Documentation
pip install mkdocs mkdocs-material mkdocstrings[python]
```

---

## 🎨 **Code Style & Standards**

### **Python Code Style**
We follow **PEP 8** with some adjustments:

```python
# Use Black formatter (line length: 88)
black scrubpy/

# Import sorting
isort scrubpy/

# Type hints for new code
def clean_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Clean a specific column in the DataFrame"""
    pass

# Docstrings in Google style
def smart_imputation(df: pd.DataFrame, strategy: str = "auto") -> pd.DataFrame:
    """
    Intelligently impute missing values in DataFrame.
    
    Args:
        df: Input DataFrame to clean
        strategy: Imputation strategy ("auto", "mean", "median", "mode")
        
    Returns:
        DataFrame with imputed values
        
    Raises:
        ValueError: If strategy is not supported
        
    Example:
        >>> df = pd.DataFrame({"A": [1, None, 3]})
        >>> cleaned = smart_imputation(df, strategy="mean")
        >>> print(cleaned)
    """
    pass
```

### **File Structure Conventions**
```
scrubpy/
├── core.py                 # Main data processing functions
├── quality_analyzer.py     # Data quality assessment
├── interfaces/
│   ├── web_app.py         # Streamlit web interface
│   ├── cli.py             # Typer CLI interface
│   └── chat.py            # AI chat interface
├── cleaning/
│   ├── missing_data.py    # Missing value operations
│   ├── outliers.py        # Outlier detection/removal
│   └── text_cleaning.py   # Text standardization
├── ai/
│   ├── llm_utils.py       # LLM integration
│   └── prompts.py         # AI prompts and templates
└── utils/
    ├── validation.py      # Input validation
    ├── logging.py         # Logging setup
    └── config.py          # Configuration management
```

---

## 🧪 **Testing Guidelines**

### **Testing Philosophy**
- **Test user-facing functionality** first
- **Test edge cases** and error conditions
- **Test with real-world data patterns**
- **Keep tests fast and reliable**

### **Test Categories**
```bash
# Unit tests (fast, isolated)
pytest tests/unit/ -v

# Integration tests (slower, multiple components)
pytest tests/integration/ -v

# Interface tests (UI/CLI behavior)
pytest tests/interfaces/ -v

# Performance tests (large datasets)
pytest tests/performance/ -v --slow
```

### **Writing Good Tests**
```python
# Good test example
def test_smart_imputation_with_numeric_data():
    """Test imputation works correctly with numeric columns"""
    # Arrange
    df = pd.DataFrame({
        "numeric_col": [1.0, None, 3.0, None, 5.0],
        "other_col": ["a", "b", "c", "d", "e"]
    })
    
    # Act
    result = smart_imputation(df, strategy="mean")
    
    # Assert
    assert result["numeric_col"].isna().sum() == 0
    assert result["numeric_col"].iloc[1] == 3.0  # mean of [1, 3, 5]
    assert result["other_col"].equals(df["other_col"])  # unchanged

# Test with realistic data
def test_cleaning_pipeline_with_movies_dataset():
    """Test full pipeline with realistic movie dataset"""
    df = load_test_dataset("movies_with_issues.csv")
    
    cleaned = full_cleaning_pipeline(df)
    
    # Verify improvements
    assert get_quality_score(cleaned) > get_quality_score(df)
    assert cleaned.duplicated().sum() == 0
    assert cleaned["release_year"].dtype in ["int64", "Int64"]
```

### **Test Data**
Use the provided test datasets:
- `tests/data/movies_sample.csv` - Small movie dataset for quick tests
- `tests/data/messy_data.csv` - Intentionally problematic dataset
- `tests/data/large_dataset.csv` - Performance testing (10K+ rows)

---

## 📝 **Documentation Guidelines**

### **Documentation Types**
1. **Code Documentation** - Docstrings and comments
2. **User Documentation** - How-to guides and tutorials
3. **API Documentation** - Function and class references
4. **Architecture Documentation** - System design and patterns

### **Writing Guidelines**
- **User-focused**: Write for the user, not yourself
- **Example-driven**: Include practical examples
- **Scannable**: Use headers, bullet points, and formatting
- **Up-to-date**: Update docs when changing functionality

### **Documentation Structure**
```markdown
# Feature Name

> **Brief description of what this does and why it's useful**

## Quick Start
[Minimal example that works immediately]

## Examples
[Real-world usage patterns]

## API Reference
[Detailed parameter descriptions]

## Common Issues
[Known problems and solutions]
```

---

## 🔄 **Contribution Workflow**

### **Standard Process**
1. **Create an Issue** (for new features) or find an existing one
2. **Fork & Branch**: Create a feature branch from `main`
3. **Develop**: Write code following our standards
4. **Test**: Ensure all tests pass and add new ones
5. **Document**: Update relevant documentation
6. **Submit PR**: Create pull request with clear description

### **Branch Naming**
```bash
# Feature branches
git checkout -b feature/smart-imputation-ml
git checkout -b feature/web-ui-improvements

# Bug fixes
git checkout -b fix/cli-crash-on-empty-data
git checkout -b fix/memory-leak-large-files

# Documentation
git checkout -b docs/api-reference-update
git checkout -b docs/contributing-guide
```

### **Commit Messages**
```bash
# Good commit messages
git commit -m "feat: add ML-based imputation for numeric columns"
git commit -m "fix: resolve CLI crash when file not found"
git commit -m "docs: update API reference for new functions"
git commit -m "test: add integration tests for chat interface"

# Use conventional commit format
# type(scope): description
# 
# Types: feat, fix, docs, style, refactor, test, chore
```

---

## **Pull Request Guidelines**

### **PR Template Checklist**
When submitting a PR, ensure:

- [ ] **Clear Title**: Summarizes the change in one line
- [ ] **Description**: Explains what and why, not just how
- [ ] **Issue Reference**: Links to relevant issues (`Fixes #123`)
- [ ] **Test Coverage**: New code is tested
- [ ] **Documentation**: Updated if user-facing changes
- [ ] **Breaking Changes**: Clearly marked and explained

### **PR Description Template**
```markdown
## What this PR does
Brief description of the change and motivation.

## 🔗 Related Issues
Fixes #123
Related to #456

## 🧪 Testing
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Tested manually with sample data
- [ ] Performance impact assessed

## 📝 Documentation
- [ ] Updated docstrings
- [ ] Updated user guide
- [ ] Updated API reference
- [ ] Added examples

## 🚨 Breaking Changes
None / List any breaking changes

## 📷 Screenshots
[If UI changes, include before/after screenshots]

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

---

## 🏆 **Recognition & Community**

### **Contributor Recognition**
- Contributors are listed in `CONTRIBUTORS.md`
- Significant contributions featured in release notes
- Active contributors invited to maintainer discussions

### **Community Guidelines**
- **Be Respectful**: Treat everyone with kindness and professionalism
- **Be Constructive**: Focus on improving the project
- **Be Patient**: Remember everyone is learning
- **Be Inclusive**: Welcome contributors of all backgrounds and skill levels

### **Getting Help**
- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Code Reviews**: Learning opportunity, not judgment
- **Documentation**: Check docs first, ask questions if unclear

---

## **Contribution Areas by Skill Level**

### **🟢 Beginner-Friendly**
- **Documentation**: Fix typos, improve examples
- **Examples**: Add new sample datasets or use cases
- **Error Messages**: Make error messages more helpful
- **Tests**: Add test cases for existing functionality
- **Configuration**: Add new configuration options

### **🟡 Intermediate**
- **New Cleaning Functions**: Implement domain-specific cleaners
- **UI Improvements**: Enhance web/CLI interfaces
- **Performance**: Optimize slow operations
- **Integration**: Add new export formats or data sources
- **AI Prompts**: Improve LLM interaction patterns

### **🔴 Advanced**
- **Architecture**: Design new subsystems
- **AI Integration**: Advanced LLM features
- **Distributed Processing**: Handle very large datasets
- **Plugin System**: Extensibility framework
- **Performance**: Core algorithm optimization

---

## 🎉 **Thank You!**

Every contribution makes ScrubPy better for the entire data community. Whether you:
- Report a bug 🐛
- Suggest a feature 💡
- Submit code 💻
- Improve documentation 📝
- Help other users 🤝

**You're making data cleaning accessible to everyone!** 🧹✨

---

## 📞 **Quick Links**
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community standards
- **[Architecture Guide](ARCHITECTURE.md)** - System design
- **[API Reference](API_REFERENCE.md)** - Function documentation
- **[Development Setup](DEVELOPER_ONBOARDING.md)** - Detailed setup guide

**Happy Contributing!** 🚀