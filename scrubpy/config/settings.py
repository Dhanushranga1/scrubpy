import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
import logging

class ScrubPySettings:
    """Centralized configuration management for ScrubPy"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".scrubpy"
        self.config_file = self.config_dir / "config.yaml"
        self.ensure_config_exists()
        self.config = self.load_config()
    
    def ensure_config_exists(self):
        """Create default config if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        default_config = {
            'llm': {
                'provider': 'ollama',
                'model': 'mistral',
                'base_url': 'http://localhost:11434',
                'timeout': 30,
                'max_retries': 3,
                'temperature': 0.7,
                'max_tokens': 2000
            },
            'performance': {
                'chunk_size': 10000,
                'memory_limit_gb': 4,
                'cache_enabled': True,
                'parallel_processing': True,
                'max_workers': None
            },
            'ui': {
                'theme': 'light',
                'show_advanced_options': False,
                'auto_save': True,
                'default_output_format': 'csv',
                'progress_bars': True
            },
            'web': {
                'port': 8501,
                'host': 'localhost',
                'auto_open': True,
                'upload_max_size_mb': 100
            },
            'cli': {
                'colorful_output': True,
                'interactive_prompts': True,
                'verbose_logging': False
            },
            'chat': {
                'conversation_history': 10,
                'auto_suggest': True,
                'explain_operations': True
            },
            'logging': {
                'level': 'INFO',
                'file_logging': True,
                'log_dir': str(self.config_dir / 'logs'),
                'max_file_size_mb': 10,
                'backup_count': 5
            },
            'quality': {
                'missing_threshold': 0.1,
                'outlier_method': 'iqr',
                'duplicate_threshold': 0.05,
                'quality_score_weights': {
                    'completeness': 0.3,
                    'validity': 0.25,
                    'consistency': 0.2,
                    'uniqueness': 0.15,
                    'accuracy': 0.1
                }
            },
            'cleaning': {
                'missing_data': {
                    'default_strategy': 'auto',
                    'string_fill_value': 'Unknown',
                    'preserve_patterns': True
                },
                'outliers': {
                    'default_action': 'flag',
                    'z_threshold': 3,
                    'iqr_multiplier': 1.5
                },
                'duplicates': {
                    'keep': 'first',
                    'consider_all_columns': True
                },
                'text_cleaning': {
                    'standardize_case': True,
                    'remove_extra_spaces': True,
                    'fix_encodings': True
                }
            },
            'dtypes': {
                'auto_convert': True,
                'date_formats': [
                    '%Y-%m-%d',
                    '%d/%m/%Y', 
                    '%m/%d/%Y',
                    '%Y-%m-%d %H:%M:%S'
                ],
                'boolean_values': {
                    'true_values': ['true', 'yes', 'y', '1', 'on'],
                    'false_values': ['false', 'no', 'n', '0', 'off']
                }
            },
            'export': {
                'include_metadata': True,
                'compression': 'infer',
                'preserve_dtypes': True,
                'add_timestamp': True
            },
            'advanced': {
                'enable_ml_imputation': False,
                'enable_anomaly_detection': False,
                'enable_profiling': True,
                'cache_ml_models': True
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not create default config: {e}")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            else:
                return {}
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return {}
    
    def get(self, key: str, default=None):
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def validate_config(self) -> bool:
        """Validate current configuration"""
        required_sections = ['llm', 'performance', 'ui', 'logging']
        for section in required_sections:
            if section not in self.config:
                return False
        return True
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        if self.config_file.exists():
            self.config_file.unlink()
        self.create_default_config()
        self.config = self.load_config()
    
    def get_config_path(self) -> Path:
        """Get path to configuration file"""
        return self.config_file
    
    def backup_config(self) -> Path:
        """Create a backup of current configuration"""
        from datetime import datetime
        backup_path = self.config_dir / f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        try:
            if self.config_file.exists():
                import shutil
                shutil.copy2(self.config_file, backup_path)
                return backup_path
        except Exception as e:
            print(f"Warning: Could not create config backup: {e}")
        return None

# Global settings instance
settings = ScrubPySettings()

def get_config_for_env() -> ScrubPySettings:
    """Get configuration based on environment variables"""
    # Check for custom config path
    custom_config_path = os.environ.get('SCRUBPY_CONFIG_PATH')
    if custom_config_path:
        custom_settings = ScrubPySettings()
        custom_settings.config_file = Path(custom_config_path)
        if custom_settings.config_file.exists():
            custom_settings.config = custom_settings.load_config()
            return custom_settings
    
    return settings

def validate_environment():
    """Validate the current environment and configuration"""
    errors = []
    
    # Check Python version
    import sys
    if sys.version_info < (3, 8):
        errors.append("Python 3.8+ is required")
    
    # Check required packages
    try:
        import pandas
    except ImportError:
        errors.append("pandas is required")
    
    try:
        import yaml
    except ImportError:
        errors.append("PyYAML is required")
    
    # Check configuration
    if not settings.validate_config():
        errors.append("Invalid configuration file")
    
    return errors