import pandas as pd
import numpy as np
import re
from typing import Dict

def detect_column_roles(df: pd.DataFrame) -> Dict[str, dict]:
    roles = {}

    for col in df.columns:
        col_info = {}
        series = df[col].dropna()
        unique_vals = series.nunique()
        dtype = str(series.dtype)

        sample_values = series.astype(str).head(10).tolist()
        pattern_flags = {
            "currency": any(re.match(r"^\$?[\d.,]+[MK]?$", val) for val in sample_values),
            "date": any(re.match(r"^\d{4}-\d{2}-\d{2}$", val) for val in sample_values),
            "percentage": any(re.match(r"^\d+(\.\d+)?%$", val) for val in sample_values),
            "id_like": bool(re.search(r"id", col.lower())),
        }

        # Detect role
        if pattern_flags["currency"]:
            role = "currency"
            suggestion = "convert_currency_to_float"
        elif pattern_flags["date"]:
            role = "date"
            suggestion = "parse_dates"
        elif pattern_flags["percentage"]:
            role = "percentage"
            suggestion = "convert_percentage_to_float"
        elif pattern_flags["id_like"]:
            role = "identifier"
            suggestion = "no_action"
        elif dtype == "object":
            if unique_vals < 30:
                role = "category"
                suggestion = "standardize_categories"
            elif any(len(val.split()) > 2 for val in sample_values):
                role = "text"
                suggestion = "standardize_text"
            else:
                role = "mixed_text"
                suggestion = "review_column"
        elif np.issubdtype(series.dtype, np.number):
            role = "numeric"
            suggestion = "check_for_outliers"
        else:
            role = "unknown"
            suggestion = "manual_review"

        col_info["role"] = role
        col_info["dtype"] = dtype
        col_info["unique"] = int(unique_vals)
        col_info["suggestion"] = suggestion

        roles[col] = col_info

    return roles


# 🧪 Example usage for testing
if __name__ == "__main__":
    df = pd.DataFrame({
        "user_id": [101, 102, 103],
        "Gross": ["$1.5M", "$3.2M", "$900K"],
        "Date": ["2022-01-01", "2022-01-02", "2022-01-03"],
        "Rating": [8.1, 7.5, 6.9],
        "Genre": ["Action", "Sci-Fi", "Action"]
    })

    insights = detect_column_roles(df)
    for col, info in insights.items():
        print(f"{col}: {info}")
