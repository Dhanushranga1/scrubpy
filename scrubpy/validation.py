"""Input validation module for ScrubPy

This module provides comprehensive validation functions for data,
files, and parameters used throughout the ScrubPy application.
"""

import pandas as pd
from pathlib import Path
from typing import Union, List, Optional, Any, Dict, Tuple
import numpy as np

from .exceptions import (
    DataValidationError, 
    FileHandlingError,
    create_data_validation_error,
    ValidationWarning
)


class DataValidator:
    """Comprehensive data validation for ScrubPy operations"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, 
                          min_rows: int = 1, 
                          min_cols: int = 1,
                          max_rows: Optional[int] = None,
                          max_cols: Optional[int] = None,
                          required_columns: Optional[List[str]] = None) -> None:
        """Validate DataFrame meets basic requirements
        
        Args:
            df: DataFrame to validate
            min_rows: Minimum number of rows required
            min_cols: Minimum number of columns required
            max_rows: Maximum number of rows allowed (optional)
            max_cols: Maximum number of columns allowed (optional)
            required_columns: List of required column names (optional)
            
        Raises:
            DataValidationError: If DataFrame doesn't meet requirements
        """
        if df is None:
            raise DataValidationError("DataFrame cannot be None")
        
        if not isinstance(df, pd.DataFrame):
            raise DataValidationError(f"Expected pandas DataFrame, got {type(df)}")
        
        # Get DataFrame info for error context
        data_info = {
            'shape': df.shape,
            'dtypes': df.dtypes.to_dict(),
            'missing_pct': (df.isnull().sum().sum() / df.size) * 100 if df.size > 0 else 0
        }
        
        if df.empty:
            raise create_data_validation_error("DataFrame cannot be empty", data_info)
        
        if len(df) < min_rows:
            raise create_data_validation_error(
                f"DataFrame must have at least {min_rows} rows, got {len(df)}", 
                data_info
            )
        
        if len(df.columns) < min_cols:
            raise create_data_validation_error(
                f"DataFrame must have at least {min_cols} columns, got {len(df.columns)}", 
                data_info
            )
        
        if max_rows and len(df) > max_rows:
            raise create_data_validation_error(
                f"DataFrame has too many rows: {len(df)} > {max_rows}", 
                data_info
            )
        
        if max_cols and len(df.columns) > max_cols:
            raise create_data_validation_error(
                f"DataFrame has too many columns: {len(df.columns)} > {max_cols}", 
                data_info
            )
        
        if required_columns:
            DataValidator.validate_columns(df, required_columns)
    
    @staticmethod
    def validate_file_path(filepath: Union[str, Path], 
                          check_exists: bool = True,
                          allowed_extensions: Optional[List[str]] = None) -> Path:
        """Validate file path exists and is readable
        
        Args:
            filepath: Path to validate
            check_exists: Whether to check if file exists
            allowed_extensions: List of allowed file extensions
            
        Returns:
            Validated Path object
            
        Raises:
            FileHandlingError: If file validation fails
        """
        filepath = Path(filepath)
        
        if check_exists and not filepath.exists():
            raise FileHandlingError(f"File does not exist: {filepath}")
        
        if check_exists and not filepath.is_file():
            raise FileHandlingError(f"Path is not a file: {filepath}")
        
        # Default allowed extensions for data files
        if allowed_extensions is None:
            allowed_extensions = ['.csv', '.xlsx', '.xls', '.json', '.parquet']
        
        if filepath.suffix.lower() not in allowed_extensions:
            raise FileHandlingError(
                f"Unsupported file format: {filepath.suffix}. "
                f"Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Check file readability if it exists
        if check_exists:
            try:
                with open(filepath, 'r') as f:
                    # Try to read first few bytes
                    f.read(100)
            except PermissionError:
                raise FileHandlingError(f"Permission denied reading file: {filepath}")
            except Exception as e:
                # For binary files like Excel, this is expected
                if filepath.suffix.lower() in ['.xlsx', '.xls', '.parquet']:
                    pass  # These are binary formats
                else:
                    raise FileHandlingError(f"Cannot read file: {filepath} - {e}")
        
        return filepath
    
    @staticmethod
    def validate_columns(df: pd.DataFrame, 
                        columns: List[str],
                        allow_missing: bool = False) -> None:
        """Validate columns exist in DataFrame
        
        Args:
            df: DataFrame to check
            columns: List of required column names
            allow_missing: If True, warn instead of error for missing columns
            
        Raises:
            DataValidationError: If required columns are missing
        """
        if not columns:
            return
        
        missing_cols = set(columns) - set(df.columns)
        
        if missing_cols:
            message = f"Missing required columns: {sorted(missing_cols)}"
            available = f"Available columns: {list(df.columns)}"
            
            if allow_missing:
                import warnings
                warnings.warn(f"{message}. {available}", ValidationWarning)
            else:
                raise DataValidationError(f"{message}. {available}")
    
    @staticmethod
    def validate_column_types(df: pd.DataFrame, 
                             expected_types: Dict[str, Union[str, type, List]]) -> Dict[str, str]:
        """Validate column data types
        
        Args:
            df: DataFrame to check
            expected_types: Dict mapping column names to expected types
            
        Returns:
            Dict of validation issues found
        """
        issues = {}
        
        for col, expected_type in expected_types.items():
            if col not in df.columns:
                issues[col] = f"Column not found"
                continue
            
            actual_dtype = df[col].dtype
            
            # Handle different type specifications
            if isinstance(expected_type, str):
                if expected_type == 'numeric':
                    if not pd.api.types.is_numeric_dtype(actual_dtype):
                        issues[col] = f"Expected numeric, got {actual_dtype}"
                elif expected_type == 'datetime':
                    if not pd.api.types.is_datetime64_any_dtype(actual_dtype):
                        issues[col] = f"Expected datetime, got {actual_dtype}"
                elif expected_type == 'string':
                    if not pd.api.types.is_string_dtype(actual_dtype) and actual_dtype != 'object':
                        issues[col] = f"Expected string, got {actual_dtype}"
            elif isinstance(expected_type, type):
                if not isinstance(df[col].iloc[0] if len(df) > 0 else None, expected_type):
                    issues[col] = f"Expected {expected_type.__name__}, got {actual_dtype}"
            elif isinstance(expected_type, list):
                # Multiple acceptable types
                type_names = [t.__name__ if isinstance(t, type) else t for t in expected_type]
                if not any(DataValidator._check_type_match(actual_dtype, t) for t in expected_type):
                    issues[col] = f"Expected one of {type_names}, got {actual_dtype}"
        
        return issues
    
    @staticmethod
    def _check_type_match(actual_dtype: Any, expected_type: Union[str, type]) -> bool:
        """Helper to check if actual dtype matches expected type"""
        if isinstance(expected_type, str):
            if expected_type == 'numeric':
                return pd.api.types.is_numeric_dtype(actual_dtype)
            elif expected_type == 'datetime':
                return pd.api.types.is_datetime64_any_dtype(actual_dtype)
            elif expected_type == 'string':
                return pd.api.types.is_string_dtype(actual_dtype) or actual_dtype == 'object'
        elif isinstance(expected_type, type):
            return str(actual_dtype).startswith(expected_type.__name__.lower())
        
        return False
    
    @staticmethod
    def validate_data_quality(df: pd.DataFrame, 
                             max_missing_pct: float = 0.5,
                             max_duplicate_pct: float = 0.1,
                             min_unique_values: int = 2) -> Dict[str, List[str]]:
        """Validate basic data quality requirements
        
        Args:
            df: DataFrame to validate
            max_missing_pct: Maximum allowed percentage of missing values
            max_duplicate_pct: Maximum allowed percentage of duplicate rows
            min_unique_values: Minimum unique values per column
            
        Returns:
            Dict with quality issues found
        """
        issues = {
            'missing_data': [],
            'duplicates': [],
            'low_variance': [],
            'warnings': []
        }
        
        # Check missing data per column
        for col in df.columns:
            missing_pct = df[col].isnull().sum() / len(df)
            if missing_pct > max_missing_pct:
                issues['missing_data'].append(
                    f"{col}: {missing_pct:.1%} missing (>{max_missing_pct:.1%} threshold)"
                )
        
        # Check duplicate rows
        duplicate_pct = df.duplicated().sum() / len(df)
        if duplicate_pct > max_duplicate_pct:
            issues['duplicates'].append(
                f"{duplicate_pct:.1%} duplicate rows (>{max_duplicate_pct:.1%} threshold)"
            )
        
        # Check low variance columns
        for col in df.select_dtypes(include=[np.number, 'object']).columns:
            unique_count = df[col].nunique()
            if unique_count < min_unique_values:
                issues['low_variance'].append(
                    f"{col}: only {unique_count} unique values (minimum {min_unique_values})"
                )
        
        # Additional warnings for very small datasets
        if len(df) < 10:
            issues['warnings'].append(f"Very small dataset: {len(df)} rows")
        
        if len(df.columns) < 2:
            issues['warnings'].append(f"Very few columns: {len(df.columns)}")
        
        return issues
    
    @staticmethod
    def validate_memory_requirements(df: pd.DataFrame, 
                                   max_memory_mb: float = 1000) -> Tuple[float, bool]:
        """Validate DataFrame memory usage
        
        Args:
            df: DataFrame to check
            max_memory_mb: Maximum allowed memory usage in MB
            
        Returns:
            Tuple of (current_memory_mb, within_limit)
        """
        memory_usage = df.memory_usage(deep=True).sum()
        memory_mb = memory_usage / 1024 / 1024
        
        within_limit = memory_mb <= max_memory_mb
        
        return memory_mb, within_limit
    
    @staticmethod
    def validate_configuration(config: Dict[str, Any]) -> List[str]:
        """Validate ScrubPy configuration
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            List of validation errors found
        """
        errors = []
        
        # Required sections
        required_sections = ['performance', 'logging', 'ui']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required configuration section: {section}")
        
        # Validate performance settings
        if 'performance' in config:
            perf = config['performance']
            
            if 'chunk_size' in perf:
                if not isinstance(perf['chunk_size'], int) or perf['chunk_size'] <= 0:
                    errors.append("performance.chunk_size must be a positive integer")
            
            if 'memory_limit_gb' in perf:
                if not isinstance(perf['memory_limit_gb'], (int, float)) or perf['memory_limit_gb'] <= 0:
                    errors.append("performance.memory_limit_gb must be a positive number")
        
        # Validate LLM settings if present
        if 'llm' in config:
            llm = config['llm']
            
            if 'provider' in llm:
                allowed_providers = ['ollama', 'openai', 'anthropic', 'local']
                if llm['provider'] not in allowed_providers:
                    errors.append(f"llm.provider must be one of {allowed_providers}")
            
            if 'timeout' in llm:
                if not isinstance(llm['timeout'], (int, float)) or llm['timeout'] <= 0:
                    errors.append("llm.timeout must be a positive number")
        
        return errors


class ParameterValidator:
    """Validator for function parameters and operation settings"""
    
    @staticmethod
    def validate_cleaning_strategy(strategy: str, 
                                 column_dtype: Optional[str] = None) -> None:
        """Validate data cleaning strategy
        
        Args:
            strategy: Cleaning strategy name
            column_dtype: Data type of the column being cleaned
            
        Raises:
            DataValidationError: If strategy is invalid
        """
        numeric_strategies = ['mean', 'median', 'mode', 'forward_fill', 'backward_fill']
        text_strategies = ['mode', 'constant', 'forward_fill', 'backward_fill']
        general_strategies = ['drop', 'auto']
        
        all_strategies = set(numeric_strategies + text_strategies + general_strategies)
        
        if strategy not in all_strategies:
            raise DataValidationError(
                f"Invalid cleaning strategy: {strategy}. "
                f"Available strategies: {sorted(all_strategies)}"
            )
        
        # Type-specific validation
        if column_dtype:
            if column_dtype in ['int64', 'float64'] and strategy not in numeric_strategies + general_strategies:
                raise DataValidationError(
                    f"Strategy '{strategy}' not suitable for numeric column. "
                    f"Use one of: {numeric_strategies + general_strategies}"
                )
            elif column_dtype == 'object' and strategy in ['mean', 'median']:
                raise DataValidationError(
                    f"Strategy '{strategy}' not suitable for text column. "
                    f"Use one of: {text_strategies + general_strategies}"
                )
    
    @staticmethod
    def validate_threshold(value: float, 
                          min_val: float = 0.0, 
                          max_val: float = 1.0,
                          parameter_name: str = "threshold") -> None:
        """Validate threshold parameter
        
        Args:
            value: Threshold value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            parameter_name: Name of the parameter for error messages
        """
        if not isinstance(value, (int, float)):
            raise DataValidationError(f"{parameter_name} must be a number")
        
        if not (min_val <= value <= max_val):
            raise DataValidationError(
                f"{parameter_name} must be between {min_val} and {max_val}, got {value}"
            )
    
    @staticmethod
    def validate_file_format(format_name: str) -> None:
        """Validate export file format
        
        Args:
            format_name: Format name to validate
        """
        supported_formats = ['csv', 'xlsx', 'json', 'parquet', 'pickle']
        
        if format_name.lower() not in supported_formats:
            raise DataValidationError(
                f"Unsupported file format: {format_name}. "
                f"Supported formats: {supported_formats}"
            )


# Convenience functions for common validations
def quick_validate_dataframe(df: pd.DataFrame, operation_name: str = "operation") -> None:
    """Quick validation for most common DataFrame requirements"""
    try:
        DataValidator.validate_dataframe(df, min_rows=1, min_cols=1)
    except DataValidationError as e:
        raise DataValidationError(f"Cannot perform {operation_name}: {e}")


def validate_column_for_operation(df: pd.DataFrame, column: str, 
                                operation: str, required_type: str = None) -> None:
    """Validate a specific column exists and is suitable for an operation"""
    DataValidator.validate_columns(df, [column])
    
    if required_type:
        type_issues = DataValidator.validate_column_types(df, {column: required_type})
        if type_issues:
            raise DataValidationError(
                f"Column '{column}' not suitable for {operation}: {type_issues[column]}"
            )