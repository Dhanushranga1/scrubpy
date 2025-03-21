from scrubpy.core import drop_missing_values, fill_missing_values, remove_duplicates, standardize_text

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

    return df_preview
