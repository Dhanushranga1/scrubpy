"""ScrubPy - AI-powered data cleaning assistant

ScrubPy provides a comprehensive suite of tools for cleaning and preprocessing data,
with multiple interfaces (Web, CLI, Chat) and AI-powered guidance.
"""

# Import version information from _version.py
from ._version import (
    __version__, 
    __author__, 
    __email__,
    __description__, 
    __url__,
    __license__,
    get_version_string,
    get_package_info,
    check_dependencies
)

# Core imports for easy access
try:
    from .core import (
        load_dataset,
        get_dataset_summary,
        clean_dataset,
        export_dataset
    )
    from .quality_analyzer import SmartDataQualityAnalyzer
    from .config.settings import settings
    from .utils.logging import logger
    
    # Configuration and setup functions
    from .config.settings import get_config_for_env, validate_environment
    
    __all__ = [
        # Core functions
        'load_dataset',
        'get_dataset_summary', 
        'clean_dataset',
        'export_dataset',
        
        # Main classes
        'SmartDataQualityAnalyzer',
        
        # Configuration
        'settings',
        'get_config_for_env',
        'validate_environment',
        
        # Logging
        'logger',
        
        # Version info and metadata
        '__version__',
        'get_version_string',
        'get_package_info',
        'check_dependencies'
    ]

except ImportError as e:
    # Graceful handling of missing dependencies during setup
    import warnings
    warnings.warn(f"Some ScrubPy components could not be imported: {e}")
    
    __all__ = ['__version__']

def get_version():
    """Get ScrubPy version"""
    return __version__

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import yaml
    except ImportError:
        missing_deps.append("PyYAML")
    
    try:
        import streamlit
    except ImportError:
        missing_deps.append("streamlit (for web interface)")
    
    try:
        import typer
    except ImportError:
        missing_deps.append("typer (for CLI interface)")
    
    try:
        import rich
    except ImportError:
        missing_deps.append("rich (for enhanced CLI)")
    
    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install scrubpy[all]")
        return False
    
    print("Success All dependencies are available")
    return True

def show_info():
    """Show ScrubPy information and status"""
    print(f"""
🧹 ScrubPy v{__version__}
AI-powered data cleaning assistant

Interfaces:
• Web Interface: python -m scrubpy.web
• CLI Interface: python -m scrubpy.cli
• Chat Interface: python -m scrubpy.chat

Configuration: {settings.get_config_path()}
Documentation: https://github.com/Dhanushranga1/scrubpy/tree/main/docs
""")
    
    # Check dependencies
    print("Dependency Status:")
    check_dependencies()

# Initialize configuration and logging on import
try:
    # Validate environment
    env_errors = validate_environment()
    if env_errors:
        import warnings
        warnings.warn(f"Environment validation issues: {'; '.join(env_errors)}")
    
    # Initialize logger with current settings
    logger.info(f"ScrubPy v{__version__} initialized successfully")
    
except Exception as e:
    import warnings
    warnings.warn(f"ScrubPy initialization warning: {e}")

if __name__ == "__main__":
    show_info()