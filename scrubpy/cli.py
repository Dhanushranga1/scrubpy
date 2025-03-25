import typer
from rich.console import Console
from InquirerPy import inquirer
import os
import pandas as pd
from scrubpy.core import (
    load_dataset, get_dataset_summary, drop_missing_values, fill_missing_values,
    remove_duplicates, standardize_text, fix_column_names, convert_column_types,
    remove_outliers, save_dataset
)
from scrubpy.preview import preview_changes
from scrubpy.profiling import DataProfiler
from scrubpy.export_profiling_report import export_profiling_report
from scrubpy.smart_eda import generate_smart_eda_pdf  # ✅ NEW

app = typer.Typer()
console = Console()
previous_states = []  # 🔄 Stores previous versions for undo feature


def clean_text_for_pdf(text):
    text = text.replace("•", "-")
    return re.sub(r"[^\x00-\x7F]+", "", text)

# 🎨 Banner
def show_banner():
    console.print("\n[bold cyan]🔥 ScrubPy - The Smartest Data Cleaner 🔥[/bold cyan]")
    console.print("[italic dim]Make your data shine in seconds![/italic dim]\n")

# 📂 Choose Dataset
def choose_dataset():
    files = [f for f in os.listdir() if f.endswith(".csv")]
    if not files:
        console.print("[bold red]❌ No CSV files found in the current directory![/bold red]")
        raise typer.Exit()

    dataset = inquirer.select(
        message="📂 Choose a dataset to clean:",
        choices=files,
        default=files[0]
    ).execute()

    return dataset

# 🔄 Store Previous State (for Undo)
def save_previous_state(df):
    """Save a copy of the current state before making changes."""
    previous_states.append(df.copy())

# 🧹 Cleaning Menu
def clean_data(df, dataset):
    while True:
        action = inquirer.select(
            message="🛠️ Choose a cleaning operation:",
            choices=[
                "📊 View Data Summary",
                "📋 Profile My Dataset",
                "🧠 Generate Smart EDA Report",  # ✅ NEW
                "🚮 Handle Missing Values",
                "🗑️ Remove Duplicates",
                "🔡 Standardize Text",
                "🔠 Fix Column Names",
                "🔢 Convert Column Types",
                "📉 Remove Outliers",
                "↩️ Undo Last Change",
                "💾 Save & Exit"
            ],
        ).execute()

        if action == "📊 View Data Summary":
            console.clear()
            console.print(get_dataset_summary(df))

        elif action == "📋 Profile My Dataset":
            profiler = DataProfiler(df)
            profiler.display_rich_summary()
            recommend = inquirer.confirm("Would you like ScrubPy to suggest cleaning actions?").execute()
            if recommend:
                issues = profiler.suggest_cleaning_actions()
                console.print("\n[bold cyan]🔎 Cleaning Recommendations:[/bold cyan]")
                for issue in issues:
                    console.print(f"- {issue}")

            export = inquirer.confirm("📝 Export this profiling report to .txt?").execute()
            if export:
                export_profiling_report(df, dataset_name=dataset)
                console.print("[bold green]✅ Profiling report exported successfully![/bold green]")

        elif action == "🧠 Generate Smart EDA Report":
            console.print("\n[bold cyan]📊 Generating Smart EDA PDF...[/bold cyan]")
            generate_smart_eda_pdf(df, dataset_name=dataset)
            console.print("[bold green]✅ EDA report generated as SmartEDA_Report.pdf![/bold green]")

        elif action == "🚮 Handle Missing Values":
            missing_percentage = (df.isnull().sum().sum() / df.size) * 100
            console.print(f"⚠️ [bold yellow]Warning:[/bold yellow] {missing_percentage:.2f}% of data is missing.")

            missing_choice = inquirer.select(
                message="How do you want to handle missing values?",
                choices=[
                    "❌ Drop Rows with Missing Values",
                    "📏 Drop Columns with > X% Missing Values",
                    "📝 Fill Missing Values (Recommended)",
                    "⬅️ Cancel"
                ],
            ).execute()

            if missing_choice == "❌ Drop Rows with Missing Values":
                preview = preview_changes(df, "drop_missing")
                console.print("[bold cyan]🔍 Preview:[/bold cyan]")
                console.print(get_dataset_summary(preview))
                confirm = inquirer.confirm("Do you want to proceed?").execute()
                if confirm:
                    save_previous_state(df)
                    df = drop_missing_values(df)
                    console.print("[bold yellow]🧹 Missing values removed![/bold yellow]")

            elif missing_choice == "📏 Drop Columns with > X% Missing Values":
                threshold = float(inquirer.text("Enter threshold percentage (e.g., 50 for 50%)").execute())
                cols_to_drop = df.columns[df.isnull().mean() * 100 > threshold]
                if cols_to_drop.empty:
                    console.print("[bold red]No columns have that much missing data![/bold red]")
                else:
                    preview = df.drop(columns=cols_to_drop)
                    console.print(f"[bold cyan]🔍 Preview: Dropping columns {list(cols_to_drop)}[/bold cyan]")
                    confirm = inquirer.confirm("Do you want to proceed?").execute()
                    if confirm:
                        save_previous_state(df)
                        df = df.drop(columns=cols_to_drop)
                        console.print(f"[bold yellow]📏 Dropped columns {list(cols_to_drop)}![/bold yellow]")

            elif missing_choice == "📝 Fill Missing Values (Recommended)":
                fill_value = inquirer.text(message="Enter a value to fill missing cells:").execute()
                preview = preview_changes(df, "fill_missing", fill_value=fill_value)
                console.print("[bold cyan]🔍 Preview:[/bold cyan]")
                console.print(get_dataset_summary(preview))
                confirm = inquirer.confirm("Do you want to proceed?").execute()
                if confirm:
                    save_previous_state(df)
                    df = fill_missing_values(df, fill_value)
                    console.print(f"[bold yellow]🖊️ Filled missing values with '{fill_value}'![/bold yellow]")

        elif action == "🗑️ Remove Duplicates":
            preview = preview_changes(df, "remove_duplicates")
            console.print("[bold cyan]🔍 Preview:[/bold cyan]")
            console.print(get_dataset_summary(preview))
            confirm = inquirer.confirm("Do you want to proceed?").execute()
            if confirm:
                save_previous_state(df)
                df = remove_duplicates(df)
                console.print("[bold yellow]♻️ Duplicates removed![/bold yellow]")

        elif action == "🔡 Standardize Text":
            col = inquirer.select(message="📌 Choose a column:", choices=list(df.columns)).execute()
            preview = preview_changes(df, "standardize_text", column=col)
            console.print("[bold cyan]🔍 Preview:[/bold cyan]")
            console.print(get_dataset_summary(preview))
            confirm = inquirer.confirm("Do you want to proceed?").execute()
            if confirm:
                save_previous_state(df)
                df = standardize_text(df, col)
                console.print(f"[bold yellow]🔤 Standardized text in '{col}'![/bold yellow]")

        elif action == "↩️ Undo Last Change":
            if previous_states:
                df = previous_states.pop()
                console.print("[bold green]↩️ Reverted to the last state![/bold green]")
            else:
                console.print("[bold red]❌ No previous state found![/bold red]")

        elif action == "💾 Save & Exit":
            output_file = "cleaned_" + dataset
            save_dataset(df, output_file)
            console.print(f"[bold green]✅ Cleaned data saved as {output_file}![/bold green]")
            break

    return df

# 🚀 Main CLI Entry Point
@app.command()
def clean():
    show_banner()
    dataset = choose_dataset()
    df = load_dataset(dataset)
    console.print(get_dataset_summary(df))
    df = clean_data(df, dataset)

if __name__ == "__main__":
    app()