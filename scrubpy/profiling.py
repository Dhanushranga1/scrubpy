# profiling.py - ScrubPy Data Profiling Engine
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from rich.console import Console
from rich.table import Table

console = Console()

class DataProfiler:
    def __init__(self, df):
        self.df = df

    def dataset_overview(self):
        """Return basic dataset info"""
        overview = {
            "Total Rows": self.df.shape[0],
            "Total Columns": self.df.shape[1],
            "Memory Usage (KB)": round(self.df.memory_usage(deep=True).sum() / 1024, 2)
        }
        return overview

    def data_types_summary(self):
        """Return column names with their data types"""
        return self.df.dtypes.astype(str).to_dict()

    def summary_statistics(self):
        """Summary stats for numeric columns"""
        return self.df.describe().T.to_dict()

    def missing_values_report(self):
        """Count and percentage of missing values"""
        total = self.df.isnull().sum()
        percent = (total / len(self.df)) * 100
        return pd.DataFrame({"Missing Values": total, "Percentage": percent}).sort_values("Missing Values", ascending=False)

    def duplicate_report(self):
        """Count duplicate rows"""
        return {"Duplicate Rows": self.df.duplicated().sum()}

    def categorical_summary(self):
        """Top categories and cardinality of object columns"""
        summary = {}
        for col in self.df.select_dtypes(include='object').columns:
            value_counts = self.df[col].value_counts().head(3).to_dict()
            summary[col] = {
                "Unique Values": self.df[col].nunique(),
                "Most Common": value_counts
            }
        return summary

    def correlation_matrix(self):
        """Return correlation matrix for numeric columns"""
        return self.df.corr(numeric_only=True).round(2).to_dict()

    def display_rich_summary(self):
        """Print dataset overview in a Rich-styled table."""
        overview = self.dataset_overview()
        table = Table(title="Dataset Overview")  # ✅ No emojis here

        table.add_column("Metric", style="bold cyan")
        table.add_column("Value", style="magenta")

        for key, val in overview.items():
            clean_key = str(key).encode("ascii", "ignore").decode("ascii")  # ✅ Removes emojis/surrogates
            clean_val = str(val).encode("ascii", "ignore").decode("ascii")
            table.add_row(clean_key, clean_val)

        console.print(table)

    def generate_profile_report(self):
        """Generate full profiling dictionary for integration"""
        return {
            "Overview": self.dataset_overview(),
            "Data Types": self.data_types_summary(),
            "Summary Statistics": self.summary_statistics(),
            "Missing Values": self.missing_values_report().to_dict(),
            "Duplicate Info": self.duplicate_report(),
            "Categorical Summary": self.categorical_summary(),
            "Correlations": self.correlation_matrix(),
        }

    def visualize_missing_heatmap(self):
        sns.heatmap(self.df.isnull(), cbar=False, cmap='viridis')
        plt.title("Missing Values Heatmap")
        plt.show()

    def visualize_correlations(self):
        plt.figure(figsize=(10, 6))
        sns.heatmap(self.df.corr(numeric_only=True), annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation Matrix")
        plt.tight_layout()
        plt.show()
    def suggest_cleaning_actions(self):
        """Suggest common cleaning actions based on profiling."""
        suggestions = []

        # Missing Values
        missing = self.df.isnull().sum()
        high_missing_cols = missing[missing > 0]
        if not high_missing_cols.empty:
            suggestions.append("🛠️ Handle missing values (some columns have NaNs).")

        # Duplicate Rows
        if self.df.duplicated().sum() > 0:
            suggestions.append("♻️ Remove duplicate rows.")

        # Column Name Formatting
        bad_colnames = [col for col in self.df.columns if ' ' in col or col != col.lower()]
        if bad_colnames:
            suggestions.append("🔠 Fix column names (spaces/capitalization issues).")

        # Text Columns with inconsistent formatting
        object_cols = self.df.select_dtypes(include="object")
        if not object_cols.empty:
            suggestions.append("🔡 Standardize text columns (e.g., lowercase & trim).")

        # Numeric columns with outliers
        numeric_cols = self.df.select_dtypes(include=["int64", "float64"])
        for col in numeric_cols:
            z_scores = (numeric_cols[col] - numeric_cols[col].mean()) / numeric_cols[col].std()
            if (z_scores.abs() > 3).sum() > 0:
                suggestions.append(f"📉 Consider removing outliers in '{col}'.")

        return suggestions if suggestions else ["✅ No major issues found. Your dataset looks good!"]
