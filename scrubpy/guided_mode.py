from rich.console import Console
from InquirerPy import inquirer
from scrubpy.core import drop_missing_values, fill_missing_values, remove_duplicates

console = Console()

def run_guided_mode(df):
    console.print("\n[bold green]🤖 Guided Cleaning Mode Activated![/bold green]\n")

    # Handling Missing Values
    if df.isnull().sum().sum() > 0:
        missing_option = inquirer.select(
            message="❓ Missing values detected. How would you like to handle them?",
            choices=["Fill with Default", "Remove Rows", "Ignore"]
        ).execute()

        if missing_option == "Fill with Default":
            fill_value = inquirer.text("Enter a default value (e.g., 'NA', 0, 'Unknown')").execute()
            df = fill_missing_values(df, fill_value)
            console.print(f"🖊️ Filled missing values with '{fill_value}'.")

        elif missing_option == "Remove Rows":
            df = drop_missing_values(df)
            console.print("🧹 Dropped rows with missing values.")

    # Handling Duplicates
    if df.duplicated().sum() > 0:
        duplicate_option = inquirer.confirm("♻️ Remove duplicate rows?").execute()
        if duplicate_option:
            df = remove_duplicates(df)
            console.print("♻️ Removed duplicate rows.")

    console.print("\n✅ Guided Cleaning Complete!\n")
    return df
