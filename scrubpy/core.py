import pandas as pd
import os
from scipy.stats import zscore
import numpy as np
import re

def load_dataset(filepath):
    """
    Load dataset safely with comprehensive error handling.
    
    Args:
        filepath: Path to the dataset file (CSV, Excel, JSON)
    
    Returns:
        pandas DataFrame or None if loading fails
        
    Example:
        >>> df = load_dataset('data/movies.csv')
        >>> if df is not None:
        ...     print(f"Loaded {df.shape[0]} rows")
    
    Raises:
        TypeError: If filepath is not a string
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported
    """
    # Input validation
    if not isinstance(filepath, str):
        raise TypeError(f"Expected string filepath, got {type(filepath).__name__}")
    
    if not filepath.strip():
        raise ValueError("Filepath cannot be empty")
    
    import os
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    print(f"Loading dataset from: {filepath}")
    
    try:
        # Determine file format and load accordingly
        file_ext = filepath.lower().split('.')[-1]
        
        if file_ext == 'csv':
            df = pd.read_csv(filepath)
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(filepath)
        elif file_ext == 'json':
            df = pd.read_json(filepath)
        elif file_ext == 'parquet':
            df = pd.read_parquet(filepath)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. "
                           f"Supported formats: csv, xlsx, xls, json, parquet")
        
        print(f"Dataset loaded successfully: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Performance recommendations
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        print(f"Memory usage: {memory_mb:.1f} MB")
        
        if df.shape[0] > 1000000:
            print(f"Large dataset detected - consider using df.sample() for quick analysis")
        elif df.shape[0] > 100000:
            print(f"Medium dataset: Operations should complete in seconds")
        
        if memory_mb > 1000:
            print(f"High memory usage detected")
            print(f"Consider reducing data types or processing subset of columns")
        
        return df
        
    except pd.errors.EmptyDataError:
        print(f"Error: File is empty: {filepath}")
        return None
    except pd.errors.ParserError as e:
        print(f"Error parsing file: {e}")
        print(f"Suggestion: Check if the file format matches the extension")
        return None
    except PermissionError:
        print(f"Error: Permission denied accessing file: {filepath}")
        return None
    except Exception as e:
        print(f"Unexpected error loading dataset: {e}")
        print(f"Suggestion: Verify file exists and is not corrupted")
        return None

# Dataset Summary
def get_dataset_summary(df):
    """Generate a summary of the dataset."""
    missing_count = df.isnull().sum().sum()
    duplicate_count = df.duplicated().sum()

    summary = f"""
    [bold cyan]Data Summary:[/bold cyan]
    Total Rows: {df.shape[0]}
    Total Columns: {df.shape[1]}
    Missing Values: {missing_count} ({(missing_count / df.size) * 100:.2f}%)
    Duplicate Rows: {duplicate_count}
    Memory Usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB
    """
    return summary

# 🚮 Drop Missing Values (with Confirmation)
def drop_missing_values(df):
    """Drop rows with missing values after user confirmation."""
    missing_before = df.isnull().sum().sum()
    percent_missing = (missing_before / df.size) * 100

    if percent_missing > 20:
        print(f"Warning: {percent_missing:.2f}% of data is missing. Consider filling values instead.")
        confirm = input("Are you sure you want to drop missing values? (yes/no): ").strip().lower()
        if confirm != "yes":
            return df

    return df.dropna().reset_index(drop=True)

# Fill Missing Values
def fill_missing_values(df, value):
    """Fill missing values with user-specified input."""
    return df.fillna(value)

# Remove Duplicates
def remove_duplicates(df):
    """Remove duplicate rows."""
    return df.drop_duplicates().reset_index(drop=True)

# 🔡 Standardize Text
def standardize_text(df, column):
    """Standardize text in a column (lowercase, trimmed)."""
    df[column] = df[column].astype(str).str.lower().str.strip()
    return df

# 🔠 Fix Column Names
def fix_column_names(df):
    """Fix column names (lowercase, underscores)."""
    df.columns = (pd.Index(df.columns)
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .str.replace(r"\s+", "_", regex=True))
    return df

# 🔢 Convert Column Types (Safe Conversion)
def convert_column_types(df, column, dtype):
    """Convert a column to a specific data type safely.
    dtype: one of {'string','integer','float','datetime','category','boolean'} (case-insensitive)
    """
    try:
        target = str(dtype).strip().lower()
        if target in ("integer", "int"):
            df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
        elif target in ("float", "double"):
            df[column] = pd.to_numeric(df[column], errors='coerce').astype(float)
        elif target in ("string", "str", "text"):
            df[column] = df[column].astype("string")
        elif target in ("datetime", "date", "timestamp"):
            df[column] = pd.to_datetime(df[column], errors="coerce", infer_datetime_format=True)
        elif target in ("category", "categorical"):
            df[column] = df[column].astype("category")
        elif target in ("boolean", "bool"):
            # Map common truthy/falsey tokens, else coerce
            truthy = {"true","1","yes","y","t"}
            falsey = {"false","0","no","n","f"}
            df[column] = (df[column]
                          .astype(str)
                          .str.strip()
                          .str.lower()
                          .map(lambda v: True if v in truthy else False if v in falsey else np.nan)
                          .astype("boolean"))
        else:
            print(f"Unknown target type '{dtype}'. No conversion applied.")
        return df
    except Exception as e:
        print(f"Error converting '{column}' to {dtype}: {e}")
        return df

# 📉 Remove Outliers with selectable method
def remove_outliers(df, column, method="zscore", iqr_factor=1.5, lower_pct=0.01, upper_pct=0.99):
    """Remove outliers from a numeric column.
    method: 'zscore' | 'iqr' | 'percentile'
    """
    if column not in df.columns:
        print(f"Column '{column}' not found!")
        return df

    if not pd.api.types.is_numeric_dtype(df[column]):
        print(f"Column '{column}' is not numeric! Skipping outlier removal.")
        return df

    series = df[column].astype(float)
    method = str(method).lower()

    try:
        if method == "zscore":
            z = (series - series.mean()) / series.std(ddof=0)
            mask = z.abs() < 3
        elif method == "iqr":
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - iqr_factor * iqr, q3 + iqr_factor * iqr
            mask = (series >= lower) & (series <= upper)
        elif method == "percentile":
            lower, upper = series.quantile([lower_pct, upper_pct])
            mask = (series >= lower) & (series <= upper)
        else:
            print(f"Unknown method '{method}', defaulting to zscore.")
            z = (series - series.mean()) / series.std(ddof=0)
            mask = z.abs() < 3

        return df.loc[mask].reset_index(drop=True)
    except Exception as e:
        print(f"Error removing outliers: {e}")
        return df

# 💾 Save Dataset (Smart Versioning)
def save_dataset(df, dataset):
    """Save the cleaned dataset with a versioned filename."""
    base_name = f"cleaned_{dataset}"
    counter = 1
    file_name = base_name

    while os.path.exists(file_name):
        file_name = f"{base_name.split('.')[0]}_{counter}.csv"
        counter += 1

    df.to_csv(file_name, index=False)
    print(f"Cleaned data saved as {file_name}")
    return df

def clean_dataset(df, operations=None):
    """
    Clean dataset with specified operations.
    
    Args:
        df: DataFrame to clean
        operations: List of cleaning operations to apply
        
    Returns:
        Cleaned DataFrame
        
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': [1, 2, 2, 3], 'B': [1, None, 3, 4]})
        >>> operations = ['remove_duplicates', 'smart_impute']
        >>> cleaned = clean_dataset(df, operations)
        >>> print(f"Shape before: {df.shape}, after: {cleaned.shape}")
    
    Raises:
        TypeError: If df is not a pandas DataFrame
        ValueError: If df is empty
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}. "
                       f"Convert your data using: pd.DataFrame(your_data)")
    
    if df.empty:
        raise ValueError("DataFrame is empty. Please provide data to clean.")
    
    if operations is None:
        operations = []
    
    if not isinstance(operations, list):
        raise TypeError(f"Expected list of operations, got {type(operations).__name__}. "
                       f"Use: ['remove_duplicates', 'smart_impute', ...]")
    
    print(f"Starting data cleaning pipeline...")
    print(f"Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Operations: {len(operations)} steps")
    
    cleaned_df = df.copy()
    
    for operation in operations:
        try:
            if operation == 'remove_duplicates':
                cleaned_df = remove_duplicates(cleaned_df)
            elif operation == 'drop_missing':
                cleaned_df = drop_missing_values(cleaned_df)
            elif operation == 'fix_column_names':
                cleaned_df = fix_column_names(cleaned_df)
            elif operation.startswith('fill_missing:'):
                fill_value = operation.split(':')[1]
                cleaned_df = fill_missing_values(cleaned_df, fill_value)
            else:
                print(f"Unknown operation: {operation}")
        except Exception as e:
            print(f"Error in operation {operation}: {e}")
    
    return cleaned_df

def export_dataset(df, filepath, format='csv'):
    """
    Export dataset in specified format.
    
    Args:
        df: DataFrame to export
        filepath: Output file path
        format: Export format ('csv', 'excel', 'json')
    """
    try:
        if format.lower() == 'csv':
            df.to_csv(filepath, index=False)
        elif format.lower() in ['excel', 'xlsx']:
            df.to_excel(filepath, index=False)
        elif format.lower() == 'json':
            df.to_json(filepath, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"Dataset exported to {filepath}")
        return True
        
    except Exception as e:
        print(f"Error exporting dataset: {e}")
        return False

def validate_email_series(email_series, remove_invalid=False):
    """
    Validate email addresses in a pandas Series.
    
    Args:
        email_series: pandas Series containing email addresses
        remove_invalid: If True, remove invalid emails; if False, mark them as invalid
    
    Returns:
        tuple: (validated_series, validation_report_df)
        
    Example:
        >>> import pandas as pd
        >>> emails = pd.Series(['user@example.com', 'invalid.email', 'test@domain.org'])
        >>> validated, report = validate_email_series(emails)
        >>> print(f"Valid emails: {report['is_valid'].sum()}/{len(emails)}")
    
    Raises:
        TypeError: If email_series is not a pandas Series
        ValueError: If email_series is empty
    """
    # Input validation
    if not isinstance(email_series, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(email_series).__name__}. "
                       f"Convert your data using: pd.Series(your_data)")
    
    if len(email_series) == 0:
        raise ValueError("Email series is empty. Please provide data to validate.")
    
    print(f"Validating {len(email_series)} email addresses...")
    
    # Simple but comprehensive email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    validated_emails = []
    validation_results = []
    
    for email in email_series:
        if pd.isna(email):
            validated_emails.append(email)
            validation_results.append({'original': email, 'is_valid': None, 'reason': 'Missing value'})
        else:
            email_str = str(email).strip()
            is_valid = bool(re.match(email_pattern, email_str))
            
            if is_valid:
                validated_emails.append(email_str)
                validation_results.append({'original': email_str, 'is_valid': True, 'reason': 'Valid'})
            else:
                if remove_invalid:
                    validated_emails.append(None)
                else:
                    validated_emails.append(email_str)
                validation_results.append({'original': email_str, 'is_valid': False, 'reason': 'Invalid format'})
    
    validated_series = pd.Series(validated_emails, index=email_series.index)
    validation_df = pd.DataFrame(validation_results)
    
    return validated_series, validation_df

def standardize_text_case(text_series, case_type='title'):
    """
    Standardize text case across a pandas Series.
    
    Args:
        text_series: pandas Series containing text
        case_type: 'title', 'upper', 'lower', 'sentence'
    
    Returns:
        pandas Series with standardized case
    """
    if case_type == 'title':
        return text_series.str.title()
    elif case_type == 'upper':
        return text_series.str.upper()
    elif case_type == 'lower':
        return text_series.str.lower()
    elif case_type == 'sentence':
        return text_series.str.capitalize()
    else:
        print(f"Unknown case type: {case_type}, returning original series")
        return text_series

def load_excel_with_sheet_info(filepath):
    """
    Load Excel file and analyze all sheets.
    
    Args:
        filepath: Path to Excel file
    
    Returns:
        dict: Sheet information and analysis
    """
    try:
        excel_file = pd.ExcelFile(filepath)
        sheet_info = {}
        
        for sheet_name in excel_file.sheet_names:
            try:
                # Read sample to analyze structure
                df_sample = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=5)
                
                sheet_info[sheet_name] = {
                    'columns': len(df_sample.columns),
                    'sample_rows': len(df_sample),
                    'column_names': list(df_sample.columns),
                    'data_types': df_sample.dtypes.astype(str).to_dict(),
                    'has_data': len(df_sample.dropna(how='all')) > 0,
                    'sample_data': df_sample.head(2).to_dict()
                }
                
            except Exception as e:
                sheet_info[sheet_name] = {
                    'error': str(e),
                    'has_data': False
                }
        
        return {
            'success': True,
            'sheet_count': len(excel_file.sheet_names),
            'sheet_names': excel_file.sheet_names,
            'sheet_info': sheet_info
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def load_specific_excel_sheet(filepath, sheet_name):
    """
    Load a specific sheet from Excel file.
    
    Args:
        filepath: Path to Excel file
        sheet_name: Name of the sheet to load
    
    Returns:
        pandas.DataFrame: Loaded data from the specified sheet
    """
    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        print(f"Loaded sheet '{sheet_name}' from {filepath}")
        print(f"Shape: {df.shape}")
        return df
        
    except Exception as e:
        print(f"Error loading sheet '{sheet_name}': {e}")
        return None

def load_large_csv_chunked(filepath, chunk_size=10000, max_chunks=None):
    """
    Load large CSV files in chunks for memory-efficient processing.
    
    Args:
        filepath: Path to CSV file
        chunk_size: Number of rows per chunk
        max_chunks: Maximum number of chunks to process (None for all)
    
    Returns:
        generator: Iterator of DataFrame chunks
    """
    import os
    
    try:
        # Check file size
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"Processing large file: {file_size_mb:.1f} MB")
        print(f"Using chunk size: {chunk_size:,} rows")
        
        # Try different encodings
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        reader = None
        
        for encoding in encodings_to_try:
            try:
                reader = pd.read_csv(filepath, chunksize=chunk_size, encoding=encoding)
                print(f"Using encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if reader is None:
            raise ValueError("Could not determine file encoding")
        
        chunk_count = 0
        for chunk in reader:
            chunk_count += 1
            print(f"Processing chunk {chunk_count}, Shape: {chunk.shape}")
            
            yield chunk
            
            if max_chunks and chunk_count >= max_chunks:
                print(f"🛑 Reached maximum chunks limit: {max_chunks}")
                break
                
    except Exception as e:
        print(f"Error processing large file: {e}")
        raise

def get_file_info(filepath):
    """
    Get comprehensive information about a file.
    
    Args:
        filepath: Path to file
    
    Returns:
        dict: File information including size, type, etc.
    """
    import os
    from pathlib import Path
    
    try:
        file_path = Path(filepath)
        file_stats = os.stat(filepath)
        
        return {
            'filename': file_path.name,
            'extension': file_path.suffix,
            'size_bytes': file_stats.st_size,
            'size_mb': file_stats.st_size / (1024 * 1024),
            'size_gb': file_stats.st_size / (1024 ** 3),
            'is_large_file': file_stats.st_size > 100 * 1024 * 1024,  # >100MB
            'exists': file_path.exists(),
            'readable': os.access(filepath, os.R_OK)
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'exists': False
        }

def analyze_missing_data(df):
    """
    Analyze missing data patterns and recommend imputation strategies.
    
    Args:
        df: pandas DataFrame
    
    Returns:
        dict: Analysis results with recommendations for each column
    """
    analysis = {}
    
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        
        if missing_count == 0:
            continue
            
        missing_pct = (missing_count / len(df)) * 100
        
        # Determine column type
        if pd.api.types.is_numeric_dtype(df[col]):
            col_type = 'numeric'
            recommended_strategy = 'median' if missing_pct < 20 else 'mean'
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            col_type = 'datetime'
            recommended_strategy = 'forward_fill'
        else:
            col_type = 'categorical'
            recommended_strategy = 'mode'
        
        # Adjust strategy based on missing percentage
        if missing_pct > 50:
            recommended_strategy = 'consider_dropping'
        elif missing_pct > 30:
            recommended_strategy = f'advanced_{recommended_strategy}'
        
        analysis[col] = {
            'missing_count': missing_count,
            'missing_percentage': round(missing_pct, 2),
            'column_type': col_type,
            'recommended_strategy': recommended_strategy
        }
    
    return analysis

def smart_impute_missing(df, strategy_dict=None, use_advanced_ml=True):
    """
    Perform smart imputation of missing values with advanced ML methods.
    
    Args:
        df: pandas DataFrame with missing values
        strategy_dict: Dict mapping column names to imputation strategies
                      If None, uses automatic strategy selection
        use_advanced_ml: If True, uses advanced ML imputation when sklearn available
    
    Returns:
        pandas DataFrame: DataFrame with imputed values
        
    Example:
        >>> import pandas as pd, numpy as np
        >>> df = pd.DataFrame({'A': [1, 2, np.nan, 4], 'B': [1, np.nan, 3, 4]})
        >>> imputed_df = smart_impute_missing(df, use_advanced_ml=True)
        >>> print(f"Missing values before: {df.isnull().sum().sum()}")
        >>> print(f"Missing values after: {imputed_df.isnull().sum().sum()}")
    
    Raises:
        TypeError: If df is not a pandas DataFrame
        ValueError: If df is empty or contains no missing values
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}. "
                       f"Convert your data using: pd.DataFrame(your_data)")
    
    if df.empty:
        raise ValueError("DataFrame is empty. Please provide data to process.")
    
    missing_count = df.isnull().sum().sum()
    if missing_count == 0:
        print("No missing values found in the DataFrame")
        return df.copy()
    
    total_cells = df.shape[0] * df.shape[1]
    missing_pct = (missing_count / total_cells) * 100
    
    print(f"Smart imputation starting...")
    print(f"Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Missing: {missing_count:,} values ({missing_pct:.1f}% of data)")
    
    # Performance recommendations
    if df.shape[0] > 100000:
        print(f"Large dataset detected - consider using sample for strategy testing")
        if use_advanced_ml:
            print(f"ML imputation may take several minutes")
    
    if missing_pct > 30:
        print(f"High missing data percentage ({missing_pct:.1f}%)")
        print(f"Consider if imputation is appropriate")
    
    if use_advanced_ml:
        print(f"Advanced ML imputation enabled")
    
    df_imputed = df.copy()
    imputation_log = {}
    
    # Check sklearn availability for advanced methods
    sklearn_available = False
    knn_available = False
    iterative_available = False
    
    if use_advanced_ml:
        try:
            from sklearn.impute import KNNImputer
            knn_available = True
            sklearn_available = True
        except ImportError:
            pass
            
        try:
            from sklearn.experimental import enable_iterative_imputer
            from sklearn.impute import IterativeImputer
            iterative_available = True
        except ImportError:
            pass
    
    # Get automatic recommendations if no strategy provided
    if strategy_dict is None:
        analysis = analyze_missing_data_advanced(df, sklearn_available)
        strategy_dict = {col: info['recommended_strategy'] 
                        for col, info in analysis.items()}
    
    for col, strategy in strategy_dict.items():
        if col not in df.columns or df[col].isnull().sum() == 0:
            continue
            
        original_missing = df[col].isnull().sum()
        
        # Show ML method transparency
        if strategy in ['knn', 'iterative']:
            reason = "high correlation with other features" if strategy == 'knn' else "many missing values in numeric data"
            print(f"Using {strategy.upper()} imputation for '{col}': {reason}")
        elif strategy in ['mean', 'median', 'mode']:
            print(f"Using {strategy} imputation for '{col}': standard statistical method")
        
        try:
            if strategy == 'mean':
                df_imputed[col] = df_imputed[col].fillna(df[col].mean())
            elif strategy == 'median':
                df_imputed[col] = df_imputed[col].fillna(df[col].median())
            elif strategy == 'mode':
                mode_value = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
                df_imputed[col] = df_imputed[col].fillna(mode_value)
            elif strategy == 'forward_fill':
                df_imputed[col] = df_imputed[col].fillna(method='ffill').fillna(method='bfill')
            elif strategy == 'backward_fill':
                df_imputed[col] = df_imputed[col].fillna(method='bfill')
            elif strategy == 'zero':
                df_imputed[col] = df_imputed[col].fillna(0)
            elif strategy == 'knn' and knn_available:
                df_imputed = _apply_knn_imputation(df_imputed, col)
            elif strategy == 'iterative' and iterative_available:
                df_imputed = _apply_iterative_imputation(df_imputed, col)
            elif 'advanced' in strategy:
                # For advanced strategies, fall back to basic method
                base_strategy = strategy.replace('advanced_', '')
                if base_strategy == 'mean':
                    df_imputed[col] = df_imputed[col].fillna(df[col].mean())
                elif base_strategy == 'median':
                    df_imputed[col] = df_imputed[col].fillna(df[col].median())
                else:
                    mode_value = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
                    df_imputed[col] = df_imputed[col].fillna(mode_value)
            
            final_missing = df_imputed[col].isnull().sum()
            imputation_log[col] = {
                'strategy': strategy,
                'original_missing': original_missing,
                'final_missing': final_missing,
                'imputed_count': original_missing - final_missing,
                'ml_method_used': strategy in ['knn', 'iterative'] and sklearn_available
            }
            
        except Exception as e:
            imputation_log[col] = {
                'strategy': strategy,
                'error': str(e),
                'original_missing': original_missing
            }
    
    # Print summary
    total_imputed = sum([log.get('imputed_count', 0) for log in imputation_log.values()])
    ml_methods_used = sum([1 for log in imputation_log.values() if log.get('ml_method_used', False)])
    
    print(f"Smart imputation completed: {total_imputed} values imputed across {len(imputation_log)} columns")
    if ml_methods_used > 0:
        print(f"Advanced ML methods used on {ml_methods_used} columns")
    
    return df_imputed

def analyze_missing_data_advanced(df, sklearn_available=False):
    """
    Advanced missing data analysis with correlation and pattern detection.
    
    Args:
        df: pandas DataFrame
        sklearn_available: Whether sklearn is available for advanced methods
    
    Returns:
        dict: Enhanced analysis results with ML recommendations
    """
    analysis = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        
        if missing_count == 0:
            continue
            
        missing_pct = (missing_count / len(df)) * 100
        
        # Determine column type
        if pd.api.types.is_numeric_dtype(df[col]):
            col_type = 'numeric'
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            col_type = 'datetime'
        else:
            col_type = 'categorical'
        
        # Calculate correlations with other columns for numeric data
        correlations = {}
        if col_type == 'numeric' and col in numeric_cols:
            for other_col in numeric_cols:
                if other_col != col and df[other_col].isnull().sum() < len(df) * 0.5:
                    corr = df[col].corr(df[other_col])
                    if abs(corr) > 0.3:  # Moderate correlation
                        correlations[other_col] = round(corr, 3)
        
        # Advanced strategy recommendation
        if missing_pct > 50:
            recommended_strategy = 'consider_dropping'
        elif col_type == 'numeric':
            if sklearn_available and len(correlations) > 0:
                if missing_pct < 20:
                    recommended_strategy = 'knn'
                else:
                    recommended_strategy = 'iterative'
            elif missing_pct < 10:
                recommended_strategy = 'median'
            else:
                recommended_strategy = 'mean'
        elif col_type == 'categorical':
            unique_ratio = df[col].nunique() / len(df.dropna())
            if unique_ratio < 0.1 and sklearn_available and missing_pct > 10:
                recommended_strategy = 'knn'
            else:
                recommended_strategy = 'mode'
        else:
            recommended_strategy = 'forward_fill'
        
        analysis[col] = {
            'missing_count': missing_count,
            'missing_percentage': round(missing_pct, 2),
            'column_type': col_type,
            'correlations': correlations,
            'recommended_strategy': recommended_strategy,
            'ml_applicable': sklearn_available and len(correlations) > 0,
            'correlation_strength': 'high' if len([c for c in correlations.values() if abs(c) > 0.5]) > 0 else 'moderate' if correlations else 'low'
        }
    
    return analysis

def _apply_knn_imputation(df, target_col, n_neighbors=5):
    """Apply KNN imputation to a specific column."""
    print(f"Applying KNN imputation to '{target_col}' (k={n_neighbors})")
    try:
        from sklearn.impute import KNNImputer
        from sklearn.preprocessing import LabelEncoder
        
        # Create a working copy
        df_work = df.copy()
        
        # Handle categorical columns by encoding them
        encoders = {}
        categorical_cols = []
        
        for col in df_work.columns:
            if df_work[col].dtype == 'object' and col != target_col:
                if df_work[col].isnull().sum() < len(df_work) * 0.8:  # Only if not too many missing
                    categorical_cols.append(col)
                    encoders[col] = LabelEncoder()
                    # Fill missing values temporarily for encoding
                    df_work[col] = df_work[col].fillna('MISSING_VALUE')
                    df_work[col] = encoders[col].fit_transform(df_work[col])
        
        # Select numeric columns for KNN
        numeric_cols = df_work.select_dtypes(include=[np.number]).columns.tolist()
        if target_col not in numeric_cols:
            # Convert target to numeric if categorical
            if df[target_col].dtype == 'object':
                encoders[target_col] = LabelEncoder()
                non_null_values = df_work[target_col].dropna()
                if len(non_null_values) > 0:
                    encoders[target_col].fit(non_null_values.astype(str))
                    df_work[target_col] = df_work[target_col].astype(str)
                    mask = df_work[target_col] != 'nan'
                    df_work.loc[mask, target_col] = encoders[target_col].transform(df_work.loc[mask, target_col])
                    df_work[target_col] = pd.to_numeric(df_work[target_col], errors='coerce')
                    numeric_cols.append(target_col)
        
        if len(numeric_cols) >= 2:  # Need at least 2 columns for KNN
            # Apply KNN imputation
            imputer = KNNImputer(n_neighbors=min(n_neighbors, len(df_work.dropna())))
            df_work[numeric_cols] = imputer.fit_transform(df_work[numeric_cols])
            
            # Convert back if it was categorical
            if target_col in encoders:
                df_work[target_col] = df_work[target_col].round().astype(int)
                df_work[target_col] = encoders[target_col].inverse_transform(df_work[target_col])
            
            # Update original dataframe
            df[target_col] = df_work[target_col]
        
        return df
        
    except Exception as e:
        print(f"KNN imputation failed for {target_col}: {e}, falling back to median/mode")
        if pd.api.types.is_numeric_dtype(df[target_col]):
            df[target_col] = df[target_col].fillna(df[target_col].median())
        else:
            mode_val = df[target_col].mode()[0] if len(df[target_col].mode()) > 0 else 'Unknown'
            df[target_col] = df[target_col].fillna(mode_val)
        return df

def _apply_iterative_imputation(df, target_col, max_iter=10):
    """Apply Iterative imputation to a specific column."""
    print(f"Applying Iterative imputation to '{target_col}' (max_iter={max_iter})")
    try:
        from sklearn.experimental import enable_iterative_imputer
        from sklearn.impute import IterativeImputer
        
        # Select only numeric columns for iterative imputation
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if target_col in numeric_cols and len(numeric_cols) >= 2:
            imputer = IterativeImputer(max_iter=max_iter, random_state=42)
            df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        
        return df
        
    except Exception as e:
        print(f"Iterative imputation failed for {target_col}: {e}, falling back to KNN")
        return _apply_knn_imputation(df, target_col)
        
    return df

def create_cleaning_workflow(operations_list):
    """
    Create a reusable cleaning workflow from a list of operations.
    
    Args:
        operations_list: List of dicts with 'type' and 'params' keys
        
    Returns:
        dict: Workflow definition that can be saved and reused
    """
    from datetime import datetime
    
    workflow = {
        'name': f'Custom Workflow {datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'description': 'Auto-generated cleaning workflow',
        'created_at': datetime.now().isoformat(),
        'operations': operations_list,
        'version': '1.0'
    }
    
    return workflow

def validate_workflow(workflow, df=None):
    """
    Validate workflow definition before execution.
    
    Args:
        workflow: Workflow definition dict
        df: Optional DataFrame to validate against
    
    Returns:
        tuple: (is_valid, validation_errors)
    """
    errors = []
    
    # Basic structure validation
    if not isinstance(workflow, dict):
        errors.append("Workflow must be a dictionary")
        return False, errors
    
    if 'operations' not in workflow:
        errors.append("Workflow must contain 'operations' key")
        return False, errors
    
    operations = workflow['operations']
    if not isinstance(operations, list):
        errors.append("'operations' must be a list")
        return False, errors
    
    if len(operations) == 0:
        errors.append("Workflow must contain at least one operation")
        return False, errors
    
    # Valid operation types
    valid_operations = {
        'remove_duplicates', 'handle_missing', 'normalize_case',
        'validate_emails', 'standardize_phones', 'smart_impute'
    }
    
    # Validate each operation
    for i, operation in enumerate(operations):
        if not isinstance(operation, dict):
            errors.append(f"Operation {i+1}: Must be a dictionary")
            continue
        
        if 'type' not in operation:
            errors.append(f"Operation {i+1}: Missing 'type' field")
            continue
        
        op_type = operation['type']
        if op_type not in valid_operations:
            errors.append(f"Operation {i+1}: Unknown operation type '{op_type}'. "
                         f"Valid types: {', '.join(sorted(valid_operations))}")
        
        # Validate operation-specific parameters
        params = operation.get('params', {})
        
        if op_type == 'validate_emails' and df is not None:
            column = params.get('column', 'email')
            if column not in df.columns:
                errors.append(f"Operation {i+1}: Column '{column}' not found in DataFrame")
        
        elif op_type == 'standardize_phones' and df is not None:
            column = params.get('column', 'phone')
            if column not in df.columns:
                errors.append(f"Operation {i+1}: Column '{column}' not found in DataFrame")
        
        elif op_type == 'normalize_case' and df is not None:
            columns = params.get('columns', [])
            if columns:
                missing_cols = [col for col in columns if col not in df.columns]
                if missing_cols:
                    errors.append(f"Operation {i+1}: Columns not found: {missing_cols}")
    
    if errors:
        return False, errors
    
    print("Workflow validation passed")
    return True, []


def execute_cleaning_workflow(df, workflow):
    """
    Execute a cleaning workflow on a DataFrame.
    
    Args:
        df: pandas DataFrame to clean
        workflow: Workflow definition dict
        
    Returns:
        pandas DataFrame: Cleaned DataFrame
        
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': [1, 2, 2], 'B': [1, None, 3]})
        >>> workflow = {'operations': [{'type': 'remove_duplicates'}]}
        >>> cleaned = execute_cleaning_workflow(df, workflow)
    
    Raises:
        TypeError: If df is not a DataFrame or workflow is not a dict
        ValueError: If df is empty or workflow is invalid
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}.")
    
    if df.empty:
        raise ValueError("DataFrame is empty. Please provide data to clean.")
    
    if not isinstance(workflow, dict):
        raise TypeError(f"Expected dict for workflow, got {type(workflow).__name__}.")
    
    if 'operations' not in workflow:
        raise ValueError("Workflow must contain 'operations' key with list of operations.")
    
    if not isinstance(workflow['operations'], list):
        raise ValueError("Workflow 'operations' must be a list.")
    
    # Validate workflow before execution
    print(f"Validating workflow...")
    is_valid, validation_errors = validate_workflow(workflow, df)
    if not is_valid:
        print(f"Workflow validation failed:")
        for error in validation_errors:
            print(f"  - {error}")
        raise ValueError(f"Workflow validation failed: {'; '.join(validation_errors)}")
    
    result_df = df.copy()
    execution_log = []
    
    print(f"Executing workflow: {workflow.get('name', 'Unnamed')}")
    print(f"Description: {workflow.get('description', 'No description')}")
    
    for i, operation in enumerate(workflow.get('operations', [])):
        op_type = operation.get('type')
        params = operation.get('params', {})
        
        try:
            print(f"  Step {i+1}: {op_type}")
            
            if op_type == 'remove_duplicates':
                before_count = len(result_df)
                result_df = result_df.drop_duplicates()
                after_count = len(result_df)
                log_entry = f"Removed {before_count - after_count} duplicates"
                
            elif op_type == 'handle_missing':
                strategy = params.get('strategy', 'drop')
                if strategy == 'drop':
                    before_count = len(result_df)
                    result_df = result_df.dropna()
                    after_count = len(result_df)
                    log_entry = f"Dropped {before_count - after_count} rows with missing values"
                else:
                    result_df = smart_impute_missing(result_df)
                    log_entry = "Applied smart imputation"
                    
            elif op_type == 'normalize_case':
                columns = params.get('columns', [])
                case_type = params.get('case_type', 'title')
                for col in columns:
                    if col in result_df.columns and result_df[col].dtype == 'object':
                        result_df[col] = standardize_text_case(result_df[col], case_type)
                log_entry = f"Normalized case for {len(columns)} columns"
                
            elif op_type == 'validate_emails':
                column = params.get('column')
                if column and column in result_df.columns:
                    result_df[column], validation_report = validate_email_series(result_df[column])
                    invalid_count = validation_report['is_valid'].value_counts().get(False, 0)
                    log_entry = f"Validated emails in {column}, found {invalid_count} invalid"
                    
            elif op_type == 'standardize_phones':
                column = params.get('column')
                format_type = params.get('format_type', 'international')
                if column and column in result_df.columns:
                    result_df[column], validation_report = standardize_phone_numbers(
                        result_df[column], format_type=format_type
                    )
                    valid_count = validation_report['is_valid'].value_counts().get(True, 0)
                    log_entry = f"Standardized phones in {column}, {valid_count} valid numbers"
                    
            else:
                log_entry = f"Unknown operation type: {op_type}"
                
            execution_log.append({
                'step': i+1,
                'operation': op_type,
                'result': log_entry,
                'success': True
            })
            print(f"    Success: {log_entry}")
            
        except Exception as e:
            error_msg = f"Error in {op_type}: {e}"
            execution_log.append({
                'step': i+1,
                'operation': op_type,
                'result': error_msg,
                'success': False
            })
            print(f"    Error: {error_msg}")
    
    print(f"Workflow completed: {len([l for l in execution_log if l['success']])}/{len(execution_log)} operations successful")
    
    return result_df

def standardize_phone_numbers(phone_series, format_type='international', default_region='US'):
    """
    Advanced phone number standardization with international support.
    
    Args:
        phone_series: pandas Series containing phone numbers
        format_type: 'international', 'national', or 'e164'
        default_region: Default country code for numbers without country code
    
    Returns:
        tuple: (standardized_series, validation_report_df)
        
    Example:
        >>> import pandas as pd
        >>> phones = pd.Series(['(555) 123-4567', '+1-555-987-6543', '5551234567'])
        >>> standardized, report = standardize_phone_numbers(phones, format_type='international')
        >>> print(f"Standardized: {standardized.head()}")
    
    Raises:
        TypeError: If phone_series is not a pandas Series
        ValueError: If phone_series is empty or invalid format_type
    """
    # Input validation
    if not isinstance(phone_series, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(phone_series).__name__}. "
                       f"Convert your data using: pd.Series(your_data)")
    
    if len(phone_series) == 0:
        raise ValueError("Phone series is empty. Please provide data to standardize.")
    
    valid_formats = ['international', 'national', 'e164']
    if format_type not in valid_formats:
        raise ValueError(f"format_type must be one of {valid_formats}, got: {format_type}")
    
    if not isinstance(default_region, str) or len(default_region) != 2:
        raise ValueError(f"default_region must be a 2-letter ISO code (e.g., 'US', 'GB'), got: {default_region}")
    
    print(f"Standardizing {len(phone_series)} phone numbers to {format_type} format (region: {default_region})")
    
    standardized = []
    validation_results = []
    
    # Try to import phonenumbers library
    try:
        import phonenumbers
        from phonenumbers import geocoder, carrier
        library_available = True
    except ImportError:
        library_available = False
        print("phonenumbers library not available, using basic standardization")
    
    for phone in phone_series:
        if pd.isna(phone):
            standardized.append(phone)
            validation_results.append({
                'original': phone, 
                'standardized': phone, 
                'is_valid': None, 
                'reason': 'Missing value',
                'region': None
            })
            continue
            
        phone_str = str(phone).strip()
        
        if library_available:
            try:
                # Parse the phone number
                parsed = phonenumbers.parse(phone_str, default_region)
                
                if phonenumbers.is_valid_number(parsed):
                    # Format according to requested type
                    if format_type == 'international':
                        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    elif format_type == 'national':
                        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
                    elif format_type == 'e164':
                        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                    else:
                        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    
                    standardized.append(formatted)
                    
                    # Get additional info
                    region = geocoder.description_for_number(parsed, 'en')
                    
                    validation_results.append({
                        'original': phone_str,
                        'standardized': formatted,
                        'is_valid': True,
                        'reason': 'Valid and formatted',
                        'region': region
                    })
                else:
                    standardized.append(phone_str)
                    validation_results.append({
                        'original': phone_str,
                        'standardized': phone_str,
                        'is_valid': False,
                        'reason': 'Invalid number format',
                        'region': None
                    })
                    
            except Exception as e:
                standardized.append(phone_str)
                validation_results.append({
                    'original': phone_str,
                    'standardized': phone_str,
                    'is_valid': False,
                    'reason': f'Parsing error: {str(e)}',
                    'region': None
                })
        else:
            # Basic standardization without phonenumbers library
            cleaned = _basic_phone_standardization(phone_str)
            standardized.append(cleaned)
            validation_results.append({
                'original': phone_str,
                'standardized': cleaned,
                'is_valid': None,
                'reason': 'Basic cleaning (library unavailable)',
                'region': None
            })
    
    standardized_series = pd.Series(standardized, index=phone_series.index)
    validation_df = pd.DataFrame(validation_results)
    
    return standardized_series, validation_df

def _basic_phone_standardization(phone_str):
    """Basic phone number cleaning without external libraries."""
    import re
    
    # Remove all non-digit characters except + at the start
    cleaned = re.sub(r'[^\d+]', '', phone_str)
    
    # If it starts with +, keep it
    if cleaned.startswith('+'):
        return cleaned
    
    # If it's a 10-digit US number, add +1
    if len(cleaned) == 10 and cleaned.isdigit():
        return f'+1{cleaned}'
    
    # If it's 11 digits starting with 1, add +
    if len(cleaned) == 11 and cleaned.startswith('1'):
        return f'+{cleaned}'
    
    return cleaned

def get_common_workflows():
    """
    Get a collection of common cleaning workflows.
    
    Returns:
        dict: Dictionary of common workflows
    """
    workflows = {
        'basic_cleaning': {
            'name': 'Basic Data Cleaning',
            'description': 'Remove duplicates and handle missing values',
            'operations': [
                {'type': 'remove_duplicates', 'params': {}},
                {'type': 'handle_missing', 'params': {'strategy': 'drop'}}
            ]
        },
        
        'comprehensive_cleaning': {
            'name': 'Comprehensive Cleaning',
            'description': 'Full cleaning pipeline with smart imputation',
            'operations': [
                {'type': 'remove_duplicates', 'params': {}},
                {'type': 'handle_missing', 'params': {'strategy': 'smart'}},
                {'type': 'normalize_case', 'params': {'columns': [], 'case_type': 'title'}}
            ]
        },
        
        'contact_data_cleaning': {
            'name': 'Contact Data Cleaning',
            'description': 'Comprehensive contact information cleaning',
            'operations': [
                {'type': 'validate_emails', 'params': {'column': 'email'}},
                {'type': 'standardize_phones', 'params': {'column': 'phone', 'format_type': 'international'}},
                {'type': 'normalize_case', 'params': {'columns': ['first_name', 'last_name'], 'case_type': 'title'}},
                {'type': 'remove_duplicates', 'params': {'subset': ['email', 'phone']}}
            ]
        },
        
        'advanced_ml_cleaning': {
            'name': 'Advanced ML Data Cleaning',
            'description': 'ML-powered comprehensive cleaning pipeline',
            'operations': [
                {'type': 'remove_duplicates', 'params': {}},
                {'type': 'handle_missing', 'params': {'strategy': 'smart', 'use_advanced_ml': True}},
                {'type': 'normalize_case', 'params': {'columns': [], 'case_type': 'title'}}
            ]
        },
        
        'email_validation': {
            'name': 'Email Validation Workflow',
            'description': 'Validate and clean email addresses',
            'operations': [
                {'type': 'validate_emails', 'params': {'column': 'email'}},
                {'type': 'remove_duplicates', 'params': {}}
            ]
        }
    }
    
    return workflows


def save_dataset(df, filepath, format_type='auto'):
    """
    Save DataFrame to file with comprehensive error handling.
    
    Args:
        df: pandas DataFrame to save
        filepath: Path to save the file
        format_type: 'auto' (infer from extension), 'csv', 'excel', 'json', 'parquet'
    
    Returns:
        bool: True if saved successfully, False otherwise
        
    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        >>> success = save_dataset(df, 'output/cleaned_data.csv')
        >>> print(f"Save successful: {success}")
    
    Raises:
        TypeError: If df is not a DataFrame or filepath is not a string
        ValueError: If df is empty or format is not supported
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
    
    if not isinstance(filepath, str):
        raise TypeError(f"Expected string filepath, got {type(filepath).__name__}")
    
    if df.empty:
        raise ValueError("DataFrame is empty. Cannot save empty dataset.")
    
    if not filepath.strip():
        raise ValueError("Filepath cannot be empty")
    
    print(f"💾 Saving dataset to: {filepath}")
    print(f"   Data: {df.shape[0]} rows × {df.shape[1]} columns")
    
    try:
        import os
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   Created directory: {directory}")
        
        # Determine format
        if format_type == 'auto':
            file_ext = filepath.lower().split('.')[-1] if '.' in filepath else 'csv'
        else:
            file_ext = format_type.lower()
        
        # Save based on format
        if file_ext == 'csv':
            df.to_csv(filepath, index=False)
        elif file_ext in ['xlsx', 'excel']:
            df.to_excel(filepath, index=False)
        elif file_ext == 'json':
            df.to_json(filepath, orient='records', indent=2)
        elif file_ext == 'parquet':
            df.to_parquet(filepath, index=False)
        else:
            raise ValueError(f"Unsupported format: {file_ext}. "
                           f"Supported formats: csv, xlsx, json, parquet")
        
        print(f"Dataset saved successfully!")
        return True
        
    except PermissionError:
        print(f"Error: Permission denied writing to: {filepath}")
        print(f"Suggestion: Check file permissions or try a different location")
        return False
    except Exception as e:
        print(f"Error saving dataset: {e}")
        return False
