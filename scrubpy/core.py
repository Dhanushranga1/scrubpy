import pandas as pd
import os
from scipy.stats import zscore

# 📂 Load Dataset
def load_dataset(filepath):
    """Load dataset safely with error handling."""
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None

# 📊 Dataset Summary
def get_dataset_summary(df):
    """Generate a summary of the dataset."""
    missing_count = df.isnull().sum().sum()
    duplicate_count = df.duplicated().sum()

    summary = f"""
    📊 [bold cyan]Data Summary:[/bold cyan]
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
        print(f"⚠️ Warning: {percent_missing:.2f}% of data is missing. Consider filling values instead.")
        confirm = input("Are you sure you want to drop missing values? (yes/no): ").strip().lower()
        if confirm != "yes":
            return df

    return df.dropna().reset_index(drop=True)

# 📝 Fill Missing Values
def fill_missing_values(df, value):
    """Fill missing values with user-specified input."""
    return df.fillna(value)

# 🗑️ Remove Duplicates
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
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    return df

# 🔢 Convert Column Types (Safe Conversion)
def convert_column_types(df, column, dtype):
    """Convert a column to a specific data type safely."""
    try:
        if dtype == "Integer":
            df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
        elif dtype == "Float":
            df[column] = pd.to_numeric(df[column], errors='coerce').astype(float)
        elif dtype == "String":
            df[column] = df[column].astype(str)
        return df
    except Exception as e:
        print(f"❌ Error converting '{column}' to {dtype}: {e}")
        return df

# 📉 Remove Outliers (Z-Score)
def remove_outliers(df, column):
    """Remove outliers from a numeric column using Z-score method."""
    if column not in df.columns:
        print(f"❌ Column '{column}' not found!")
        return df

    if df[column].dtype not in ["int64", "float64"]:
        print(f"⚠️ Column '{column}' is not numeric! Skipping outlier removal.")
        return df

    df["z_score"] = zscore(df[column].dropna())  # Compute Z-scores
    df = df[df["z_score"].abs() < 3]  # Keep only data within 3 standard deviations
    df.drop(columns=["z_score"], inplace=True)  # Remove temp column
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
    print(f"✅ Cleaned data saved as {file_name}!")
    return df
