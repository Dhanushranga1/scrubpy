"""
ScrubPy package metadata and version information.
"""

__version__ = "2.0.0"
__author__ = "Dhanush Ranga"
__email__ = "dhanushranga1@gmail.com"
__description__ = "AI-powered data cleaning assistant with multiple interfaces"
__url__ = "https://github.com/Dhanushranga1/scrubpy"
__license__ = "MIT"

# Package information
PACKAGE_NAME = "scrubpy"
PROJECT_NAME = "ScrubPy"
MINIMUM_PYTHON_VERSION = "3.8"

# Feature flags
FEATURES = {
    'ai': True,          # AI-powered cleaning suggestions
    'web': True,         # Streamlit web interface
    'cli': True,         # Command-line interface
    'chat': True,        # Interactive chat interface
    'advanced': True,    # Advanced statistical operations
}

# Version information
VERSION_INFO = {
    'major': 2,
    'minor': 0,
    'patch': 0,
    'pre_release': None,  # alpha, beta, rc
    'build': None
}

def get_version_string():
    """Get formatted version string."""
    version = f"{VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}"
    if VERSION_INFO['pre_release']:
        version += f"-{VERSION_INFO['pre_release']}"
    if VERSION_INFO['build']:
        version += f"+{VERSION_INFO['build']}"
    return version

def check_dependencies():
    """Check if required dependencies are available."""
    missing_deps = []
    
    try:
        import pandas
    except ImportError:
        missing_deps.append('pandas')
    
    try:
        import numpy
    except ImportError:
        missing_deps.append('numpy')
    
    try:
        import streamlit
    except ImportError:
        missing_deps.append('streamlit')
    
    try:
        import typer
    except ImportError:
        missing_deps.append('typer')
    
    return missing_deps

def get_package_info():
    """Get comprehensive package information."""
    return {
        'name': PACKAGE_NAME,
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'description': __description__,
        'url': __url__,
        'license': __license__,
        'python_version': MINIMUM_PYTHON_VERSION,
        'features': FEATURES,
        'missing_dependencies': check_dependencies()
    }