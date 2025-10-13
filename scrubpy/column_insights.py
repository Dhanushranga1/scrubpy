from typing import Dict, Any, List, Tuple
import pandas as pd
import re
import numpy as np
from collections import Counter

# Define comprehensive patterns and heuristics for column roles
ROLE_PATTERNS = {
    "identifier": [
        "id", "uuid", "guid", "_id", "key", "code", 
        "user_id", "customer_id", "employee_id", "student_id", 
        "transaction_id", "order_id", "product_id", "record_id"
    ],
    "datetime": [
        "date", "time", "timestamp", "created", "updated", "modified",
        "dob", "birth", "created_at", "updated_at", "start", "end",
        "year", "month", "day", "hour", "minute", "second"
    ],
    "monetary": [
        "price", "amount", "cost", "fee", "tax", "expense", "revenue", 
        "income", "salary", "gross", "net", "profit", "margin", 
        "budget", "payment", "balance", "total", "discount", "value"
    ],
    "categorical": [
        "category", "type", "class", "group", "label", "status", "tag", 
        "genre", "department", "division", "sector", "segment", "tier",
        "level", "priority", "severity", "stage", "phase", "state", "region"
    ],
    "text": [
        "description", "comment", "message", "review", "feedback", "text", 
        "summary", "title", "name", "address", "email", "note", "detail",
        "content", "bio", "about", "overview", "remark", "observation"
    ],
    "numeric_score": [
        "rating", "score", "rank", "grade", "marks", "points", "percentile",
        "metric", "index", "ratio", "rate", "weight", "average", "mean", 
        "count", "number", "quantity", "frequency", "percentage"
    ],
    "boolean": [
        "is_", "has_", "can_", "should_", "was_", "will_", "did_", 
        "flag", "active", "enabled", "valid", "verified", "approved", 
        "confirmed", "completed", "deleted", "featured", "required"
    ],
    "geographic": [
        "location", "address", "city", "state", "country", "postal", 
        "zip", "latitude", "longitude", "geo", "coord", "region", 
        "province", "territory", "continent", "area"
    ],
    "contact": [
        "phone", "email", "contact", "mobile", "fax", "website", 
        "url", "link", "address", "social", "username"
    ],
    "personal": [
        "name", "first", "last", "middle", "full", "gender", 
        "age", "sex", "title", "prefix", "suffix", "nationality", 
        "ethnicity", "language", "education", "occupation"
    ]
}


def analyze_values(series: pd.Series) -> Dict[str, Any]:
    """Analyze series values to provide additional insights"""
    value_insights = {}
    
    # Skip analysis for columns with too many nulls
    null_percent = series.isna().mean()
    value_insights["null_percent"] = round(null_percent * 100, 2)
    
    if null_percent > 0.9:
        return value_insights
    
    non_null = series.dropna()
    
    # If empty after dropping nulls, return early
    if len(non_null) == 0:
        return value_insights
    
    # For numeric columns
    if pd.api.types.is_numeric_dtype(non_null):
        value_insights["min"] = non_null.min()
        value_insights["max"] = non_null.max()
        value_insights["mean"] = round(non_null.mean(), 2)
        
        # Check if likely boolean (just 0s and 1s)
        unique_vals = set(non_null.unique())
        if unique_vals.issubset({0, 1}) or unique_vals.issubset({0.0, 1.0}):
            value_insights["likely_boolean"] = True
        
        # Check if likely ID (sequential with no gaps or high cardinality)
        if series.nunique() / len(series) > 0.9 and non_null.dtype in (np.int64, np.int32, np.int16):
            value_insights["likely_id"] = True
    
    # For string/object columns
    elif pd.api.types.is_string_dtype(non_null) or pd.api.types.is_object_dtype(non_null):
        # Sample values for pattern detection
        sample = non_null.sample(min(100, len(non_null)))
        
        # Check length statistics
        lengths = sample.astype(str).str.len()
        value_insights["avg_length"] = round(lengths.mean(), 1)
        
        # Detect patterns
        # Email pattern
        if any(bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(x))) for x in sample):
            value_insights["contains_emails"] = True
            
        # URL pattern
        if any(bool(re.match(r'^https?://\S+$', str(x))) for x in sample):
            value_insights["contains_urls"] = True
            
        # Date-like strings
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',    # YYYY-MM-DD
            r'\d{1,2}-\d{1,2}-\d{4}'     # DD-MM-YYYY
        ]
        if any(any(bool(re.match(pattern, str(x))) for x in sample) for pattern in date_patterns):
            value_insights["contains_date_strings"] = True
        
        # Cardinality check
        cardinality = series.nunique() / len(series)
        value_insights["cardinality"] = round(cardinality, 3)
        
        if cardinality < 0.01:
            value_insights["low_cardinality"] = True
        elif cardinality > 0.9:
            value_insights["high_cardinality"] = True
    
    return value_insights


def infer_column_role(column: str, series: pd.Series) -> Dict[str, Any]:
    """Infer column role using name, data type, and value analysis"""
    col = column.lower()
    matches = []
    
    # 1. Check for pattern matches in column name
    for role, keywords in ROLE_PATTERNS.items():
        for keyword in keywords:
            # Match whole words or surrounded by underscores
            if re.search(rf'\b{keyword}\b', col) or f"_{keyword}_" in col or col.startswith(f"{keyword}_") or col.endswith(f"_{keyword}"):
                matches.append((role, keyword))
    
    # Count matches by role
    role_counts = Counter([role for role, _ in matches])
    
    # Start with moderate confidence
    confidence = 0.5
    
    # Get initial role based on name patterns
    if role_counts:
        # Take most frequently matched role
        role = role_counts.most_common(1)[0][0]
        # Add confidence based on number of matched patterns
        confidence += 0.1 * min(len(matches), 3)
    else:
        role = "unknown"
    
    # 2. Analyze and adjust based on data type
    dtype = series.dtype
    
    # Get value insights
    value_analysis = analyze_values(series)
    
    # 3. Adjust role and confidence based on dtype and value analysis
    if pd.api.types.is_numeric_dtype(dtype):
        if role == "identifier" or value_analysis.get("likely_id", False):
            confidence += 0.2
        elif role == "monetary" and not value_analysis.get("likely_boolean", False):
            confidence += 0.2
        elif role == "numeric_score" and not value_analysis.get("likely_boolean", False):
            confidence += 0.2
        elif value_analysis.get("likely_boolean", False):
            if role == "boolean":
                confidence += 0.3
            else:
                role = "boolean"
                confidence = 0.7
    
    elif pd.api.types.is_string_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
        if role == "text" and value_analysis.get("avg_length", 0) > 20:
            confidence += 0.2
        elif role == "categorical" and value_analysis.get("low_cardinality", False):
            confidence += 0.2
        elif role == "identifier" and value_analysis.get("high_cardinality", False):
            confidence += 0.2
        elif value_analysis.get("contains_emails", False):
            role = "contact"
            confidence = 0.8
        elif value_analysis.get("contains_urls", False):
            role = "contact"
            confidence = 0.7
        elif value_analysis.get("contains_date_strings", False):
            role = "datetime"
            confidence = 0.8
    
    elif pd.api.types.is_datetime64_dtype(dtype):
        role = "datetime"
        confidence = 0.9
    
    elif pd.api.types.is_bool_dtype(dtype):
        role = "boolean"
        confidence = 0.9
    
    # Cap confidence at 1.0
    confidence = min(round(confidence, 2), 1.0)
    
    # Build result
    result = {
        "role": role,
        "type": str(dtype),
        "confidence": confidence,
        "insights": value_analysis
    }
    
    return result


def get_column_insights(df: pd.DataFrame, sample_size: int = 1000) -> Dict[str, Dict[str, Any]]:
    """
    Analyze all columns in a dataframe to determine their likely roles and characteristics
    
    Args:
        df: Pandas DataFrame to analyze
        sample_size: Number of rows to sample for large dataframes
    
    Returns:
        Dictionary of column insights
    """
    # Sample the DataFrame if it's large
    if len(df) > sample_size:
        df_sample = df.sample(sample_size, random_state=42)
    else:
        df_sample = df
    
    insights = {}
    for col in df.columns:
        insights[col] = infer_column_role(col, df_sample[col])
    
    return insights


def suggest_transformations(insights: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """Suggest possible transformations based on column insights"""
    suggestions = {}
    
    for col, data in insights.items():
        col_suggestions = []
        role = data["role"]
        insights_data = data.get("insights", {})
        
        # Suggestions based on role and insights
        if role == "datetime" and "contains_date_strings" in insights_data:
            col_suggestions.append(f"Convert '{col}' to datetime using pd.to_datetime()")
        
        elif role == "monetary":
            col_suggestions.append(f"Format '{col}' as currency, e.g.: df['{col}'].map(lambda x: f\"${{x:,.2f}}\")")

        
        elif role == "identifier" and insights_data.get("null_percent", 0) > 0:
            col_suggestions.append(f"Check missing values in identifier column '{col}'")
        
        elif role == "text" and insights_data.get("avg_length", 0) > 100:
            col_suggestions.append(f"Consider text summarization for long text in '{col}'")
        
        elif role == "categorical" and insights_data.get("cardinality", 0) > 0.5:
            col_suggestions.append(f"High cardinality in '{col}' - may need grouping of less frequent categories")
        
        # Type-specific suggestions
        if "object" in data["type"] and role != "text":
            col_suggestions.append(f"Consider encoding '{col}' if it's categorical")
        
        if col_suggestions:
            suggestions[col] = col_suggestions
    
    return suggestions