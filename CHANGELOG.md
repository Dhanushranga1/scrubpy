# Changelog

All notable changes to ScrubPy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-11

### Added
- **AI-Powered Data Cleaning**: Advanced LLM integration for intelligent data cleaning and validation
- **Interactive Chat Assistant**: AI chat interface for guided data cleaning workflows
- **Modern Web Interface**: Streamlit-based web app with drag-and-drop file upload
- **Enhanced CLI**: Rich terminal interface with interactive prompts and progress indicators
- **Quality Analysis Engine**: Comprehensive data quality scoring and insights
- **Smart EDA**: Automated exploratory data analysis with PDF report generation
- **Advanced Text Processing**: Sophisticated text cleaning and normalization
- **Email and Phone Validation**: Built-in validation for contact information
- **Template System**: Pre-configured cleaning templates for common data types
- **Professional Documentation**: Complete API reference and usage guides
- **Console Script Entry Points**: Easy installation with `pip install scrubpy`
  - `scrubpy` - Main CLI interface
  - `scrubpy-web` - Launch web interface
  - `scrubpy-chat` - AI chat assistant

### Enhanced
- **Core Engine**: Complete rewrite with modern Python patterns and type hints
- **Performance**: Optimized algorithms for faster processing on large datasets
- **Error Handling**: Robust error management with informative messages
- **Logging**: Comprehensive logging system for debugging and monitoring
- **Configuration**: Flexible YAML-based configuration system
- **Validation**: Advanced data validation with customizable rules
- **Export Options**: Multiple output formats (CSV, Excel, JSON, PDF reports)

### Technical
- **Python 3.8+ Support**: Modern Python compatibility
- **Type Safety**: Full type annotations throughout codebase
- **Testing**: Comprehensive test suite with pytest
- **Packaging**: Modern Python packaging with pyproject.toml
- **Dependencies**: Curated dependency management with version constraints
- **Documentation**: Sphinx-based documentation with examples

### Fixed
- **Memory Usage**: Optimized memory handling for large datasets
- **Unicode Support**: Improved handling of international characters
- **Platform Compatibility**: Cross-platform compatibility improvements
- **Performance**: Various performance optimizations and bottleneck fixes

### Removed
- **Legacy Code**: Removed deprecated functions and outdated patterns
- **Unused Dependencies**: Cleaned up dependency tree for smaller installation

## [1.x.x] - Previous Versions

Earlier versions focused on basic data cleaning functionality. See git history for detailed changes.

---

For upgrade guides and migration information, see [UPGRADING.md](docs/UPGRADING.md)