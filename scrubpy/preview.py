from scrubpy.core import drop_missing_values, fill_missing_values, remove_duplicates, standardize_text, fix_column_names, convert_column_types, remove_outliers

def preview_changes(df, action, **kwargs):
    """Show a preview of how the dataset will change before applying."""
    
    df_preview = df.copy()

    if action == "drop_missing":
        df_preview = drop_missing_values(df_preview)
    elif action == "fill_missing":
        fill_value = kwargs.get("fill_value", "N/A")
        df_preview = fill_missing_values(df_preview, fill_value)
    elif action == "remove_duplicates":
        df_preview = remove_duplicates(df_preview)
    elif action == "standardize_text":
        col = kwargs.get("column")
        df_preview = standardize_text(df_preview, col)
    elif action == "fix_column_names":
        df_preview = fix_column_names(df_preview)
    elif action == "convert_column_types":
        col = kwargs.get("column")
        target_type = kwargs.get("target_type")
        df_preview = convert_column_types(df_preview, col, target_type)
    elif action == "remove_outliers":
        col = kwargs.get("column")
        method = kwargs.get("method", "zscore")
        df_preview = remove_outliers(df_preview, col, method=method)

    return df_preview
