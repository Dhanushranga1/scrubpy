from setuptools import setup, find_packages
import os
from pathlib import Path

# Read version from __init__.py
def get_version():
    """Get version from __init__.py file"""
    init_file = Path(__file__).parent / 'scrubpy' / '__init__.py'
    if init_file.exists():
        with open(init_file) as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

# Read README for long description
def get_long_description():
    """Get long description from README file"""
    readme_file = Path(__file__).parent / 'README.md'
    if readme_file.exists():
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "AI-powered data cleaning assistant with multiple interfaces"

# Read requirements
def get_requirements():
    """Get requirements from requirements.txt"""
    req_file = Path(__file__).parent / 'requirements.txt'
    if req_file.exists():
        with open(req_file) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Fallback requirements if file doesn't exist
    return [
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "streamlit>=1.25.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "PyYAML>=6.0.0",
        "requests>=2.28.0"
    ]

setup(
    name="scrubpy",
    version=get_version(),
    author="Dhanush Ranga",
    author_email="dhanushranga1@gmail.com",
    description="AI-powered data cleaning assistant with multiple interfaces",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Dhanushranga1/scrubpy",
    project_urls={
        "Bug Reports": "https://github.com/Dhanushranga1/scrubpy/issues",
        "Source": "https://github.com/Dhanushranga1/scrubpy",
        "Documentation": "https://github.com/Dhanushranga1/scrubpy/blob/main/docs/README.md",
    },
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="data cleaning, data preprocessing, pandas, AI, machine learning, data science",
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=22.0',
            'flake8>=4.0',
            'mypy>=0.950',
            'pre-commit>=2.15.0'
        ],
        "ai": [
            "ollama>=0.1.0",
            "openai>=1.0.0", 
            "anthropic>=0.3.0",
            "InquirerPy>=0.3.4",
            "psutil>=5.8.0"
        ],
        'advanced': [
            'scikit-learn>=1.0.0',
            'scipy>=1.7.0',
            'plotly>=5.0.0',
            'seaborn>=0.11.0'
        ],
        'web': [
            'streamlit>=1.25.0',
            'plotly>=5.0.0',
            'streamlit-aggrid>=0.3.0'
        ],
        'performance': [
            'polars>=0.18.0',
            'pyarrow>=10.0.0',
            'fastparquet>=0.8.0'
        ],
        'all': [
            'pytest>=6.0', 'pytest-cov>=2.0', 'black>=22.0', 'flake8>=4.0', 'mypy>=0.950',
            'ollama>=0.1.0', 'openai>=1.0.0', 'anthropic>=0.3.0',
            'scikit-learn>=1.0.0', 'scipy>=1.7.0', 'plotly>=5.0.0', 'seaborn>=0.11.0',
            'streamlit>=1.25.0', 'streamlit-aggrid>=0.3.0',
            'polars>=0.18.0', 'pyarrow>=10.0.0', 'fastparquet>=0.8.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'scrubpy=scrubpy.cli:app',
            'scrubpy-web=scrubpy.web.launcher:main',
            'scrubpy-chat=scrubpy.chat_assistant:main',
        ],
    },
    include_package_data=True,
    package_data={
        'scrubpy': [
            'fonts/*', 
            'templates/*',
            'config/*.yaml',
            'config/*.json'
        ],
    },
    zip_safe=False,
    platforms=["any"],
)
