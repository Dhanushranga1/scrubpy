# utils.py - Handles dataset backup, undo system, and helper functions
import pandas as pd
import shutil
import os
import re

# Store dataset history for undo functionality
data_history = []

def backup_dataset(filepath):
    """Create a backup of the dataset before modifications."""
    backup_path = f"backup_{filepath}"
    shutil.copy(filepath, backup_path)
    print(f"[🔄] Backup created: {backup_path}")

def save_state(df):
    """Save the current state of the dataset before modification."""
    data_history.append(df.copy())

def undo_last_change():
    """Revert to the last saved dataset state."""
    if data_history:
        return data_history.pop()
    else:
        print("[⚠️] No previous state to revert to.")
        return None

def confirm_action(action_name, df_before, df_after):
    """Preview the changes before confirming an action."""
    print(f"\n🔍 Preview Before Applying: {action_name}")
    print("Before:")
    print(get_dataset_summary(df_before))
    print("After:")
    print(get_dataset_summary(df_after))
    confirm = input("Do you want to proceed? (yes/no): ").strip().lower()
    return confirm == "yes"


def clean_text_for_pdf(text):
    import re
    """Remove emojis and non-ASCII characters for PDF compatibility."""
    text = text.replace("•", "-")
    return re.sub(r"[^\x00-\x7F]+", "", text)