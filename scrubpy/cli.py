import typer
from rich.console import Console
from rich.table import Table
from InquirerPy import inquirer
import os
import pandas as pd
import re
import subprocess
import json
from scrubpy.core import (
    load_dataset, get_dataset_summary, drop_missing_values, fill_missing_values,
    remove_duplicates, standardize_text, fix_column_names, convert_column_types,
    remove_outliers, save_dataset
)
from scrubpy.preview import preview_changes
from scrubpy.profiling import DataProfiler
from scrubpy.export_profiling_report import export_profiling_report
from scrubpy.smart_eda import generate_smart_eda_pdf
from scrubpy.column_insights import get_column_insights, suggest_transformations  # Import the new module

app = typer.Typer()
console = Console()

previous_states = []  # Stores previous versions for undo feature


def clean_text_for_pdf(text):
    text = text.replace("•", "-")
    return re.sub(r"[^\x00-\x7F]+", "", text)


# Banner
def show_banner():
    console.print("\n[bold cyan]ScrubPy - The Smartest Data Cleaner[/bold cyan]")
    console.print("[italic dim]Make your data shine in seconds![/italic dim]\n")


# Choose Dataset
def choose_dataset():
    files = [f for f in os.listdir() if f.endswith(".csv")]
    if not files:
        console.print("[bold red]No CSV files found in the current directory![/bold red]")
        raise typer.Exit()

    dataset = inquirer.select(
        message="Choose a dataset to clean:",
        choices=files,
        default=files[0]
    ).execute()

    return dataset


# Store Previous State (for Undo)
def save_previous_state(df):
    """Save a copy of the current state before making changes."""
    previous_states.append(df.copy())


# Display Column Insights
def display_column_insights(df):
    """Display the inferred roles of columns in a rich table"""
    console.print("\n[bold cyan]Analyzing Column Roles...[/bold cyan]")
    
    # Get column insights
    insights = get_column_insights(df)
    
    # Create a table to display results
    table = Table(title="Column Role Insights")
    table.add_column("Column", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Confidence", style="magenta")
    table.add_column("Key Insights", style="blue")
    
    # Add rows for each column
    for col, data in insights.items():
        # Format the key insights
        insight_details = []
        if "insights" in data:
            for k, v in data["insights"].items():
                if isinstance(v, bool) and v:
                    insight_details.append(k.replace("_", " "))
                elif k == "null_percent" and v > 0:
                    insight_details.append(f"{v}% null")
                elif k == "cardinality" and v is not None:
                    insight_details.append(f"cardinality: {v}")
        
        insights_text = ", ".join(insight_details[:3])  # Limit to top 3 insights
        
        # Add a row with colorized confidence value
        confidence_str = f"{data['confidence'] * 100:.0f}%"
        confidence_color = "[red]" if data['confidence'] < 0.5 else "[yellow]" if data['confidence'] < 0.8 else "[green]"
        formatted_confidence = f"{confidence_color}{confidence_str}[/]"
        
        table.add_row(
            col,
            data["role"].capitalize(),
            data["type"],
            formatted_confidence,
            insights_text
        )
    
    console.print(table)
    
    # Get and display transformation suggestions
    suggestions = suggest_transformations(insights)
    if suggestions:
        console.print("\n[bold cyan]Suggested Transformations:[/bold cyan]")
        for col, suggestion_list in suggestions.items():
            if suggestion_list:
                console.print(f"[bold]{col}[/bold]:")
                for suggestion in suggestion_list:
                    console.print(f"  - {suggestion}")
    
    # Ask if user wants to include in EDA
    include_in_eda = inquirer.confirm(
        "Include these column insights in Smart EDA report?",
        default=True
    ).execute()
    
    return insights, include_in_eda


# Talk to Dataset with LLM
def talk_to_dataset_with_llm(df, column_insights_data):
    console.print("\n[bold cyan]Talking to your dataset with Mistral LLM...[/bold cyan]")

    # Prepare insights summary
    insights_summary = []
    for col, data in column_insights_data.items():
        summary = f"{col}: {data['role']}, {data['type']}, {int(data['confidence'] * 100)}% confidence"
        insights = data.get("insights", {})
        for k, v in insights.items():
            if isinstance(v, bool) and v:
                summary += f", {k.replace('_', ' ')}"
            elif isinstance(v, (int, float)) and k in ["null_percent", "cardinality"]:
                summary += f", {k.replace('_', ' ')}: {v}"
        insights_summary.append(summary)

    # Sample data rows
    sample_rows = df.sample(min(5, len(df))).to_dict(orient="records")

    # Build prompt
    prompt = f"""You are a data assistant helping analyze and clean datasets.
Below is a summary of the dataset and sample rows. Suggest intelligent cleaning steps.

Column Insights:
{chr(10).join(insights_summary)}

Sample Rows:
{json.dumps(sample_rows, indent=2)}

Respond with your suggestions only."""
    
    # Run the prompt using Mistral
    result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=prompt.encode(),
        stdout=subprocess.PIPE
    )

    response = result.stdout.decode()
    console.print("\n[bold green]LLM Suggestions:[/bold green]")
    console.print(response)


# Cleaning Menu
def clean_data(df, dataset):
    column_insights_data = None  # Store insights for later use in EDA
    
    while True:
        action = inquirer.select(
            message="Choose a cleaning operation:",
            choices=[
                "View Data Summary",
                "Profile My Dataset",
                "Detect Column Roles",  # NEW
                "Generate Smart EDA Report",
                "Ask the AI Assistant (LLM)",
                "Handle Missing Values",
                "Remove Duplicates",
                "Standardize Text",
                "Fix Column Names",
                "Convert Column Types",
                "Remove Outliers",
                "Undo Last Change",
                "Save & Exit"
            ],
        ).execute()

        if action == "View Data Summary":
            console.clear()
            console.print(get_dataset_summary(df))

        elif action == "Profile My Dataset":
            profiler = DataProfiler(df)
            profiler.display_rich_summary()
            recommend = inquirer.confirm("Would you like ScrubPy to suggest cleaning actions?").execute()
            if recommend:
                issues = profiler.suggest_cleaning_actions()
                console.print("\n[bold cyan]Cleaning Recommendations:[/bold cyan]")
                for issue in issues:
                    console.print(f"- {issue}")

            export = inquirer.confirm("Export this profiling report to .txt?").execute()
            if export:
                export_profiling_report(df, dataset_name=dataset)
                console.print("[bold green]Profiling report exported successfully![/bold green]")
        
        elif action == "Detect Column Roles":
            # Call the new function to display column insights
            column_insights_data, include_in_eda = display_column_insights(df)
            console.print("[bold green]Column roles detected successfully![/bold green]")

        elif action == "Generate Smart EDA Report":
            console.print("\n[bold cyan]Generating Smart EDA PDF...[/bold cyan]")
            # Pass column insights if available
            extra_data = {}
            if column_insights_data:
                extra_data["column_insights"] = column_insights_data
            generate_smart_eda_pdf(df, dataset_name=dataset, extra_data=extra_data)
            console.print("[bold green]EDA report generated as SmartEDA_Report.pdf![/bold green]")
        
        elif action == "Ask the AI Assistant (LLM)":
            if column_insights_data:
                talk_to_dataset_with_llm(df, column_insights_data)
            else:
                console.print("[bold red]Please run 'Detect Column Roles' first![/bold red]")

        elif action == "Handle Missing Values":
            missing_percentage = (df.isnull().sum().sum() / df.size) * 100
            console.print(f"[bold yellow]Warning:[/bold yellow] {missing_percentage:.2f}% of data is missing.")

            missing_choice = inquirer.select(
                message="How do you want to handle missing values?",
                choices=[
                    "Drop Rows with Missing Values",
                    "Drop Columns with > X% Missing Values",
                    "Fill Missing Values (Recommended)",
                    "Cancel"
                ],
            ).execute()

            if missing_choice == "Drop Rows with Missing Values":
                preview = preview_changes(df, "drop_missing")
                console.print("[bold cyan]Preview:[/bold cyan]")
                console.print(get_dataset_summary(preview))
                confirm = inquirer.confirm("Do you want to proceed?").execute()
                if confirm:
                    save_previous_state(df)
                    df = drop_missing_values(df)
                    console.print("[bold yellow]Missing values removed![/bold yellow]")

            elif missing_choice == "Drop Columns with > X% Missing Values":
                threshold = float(inquirer.text("Enter threshold percentage (e.g., 50 for 50%)").execute())
                cols_to_drop = df.columns[df.isnull().mean() * 100 > threshold]
                if cols_to_drop.empty:
                    console.print("[bold red]No columns have that much missing data![/bold red]")
                else:
                    preview = df.drop(columns=cols_to_drop)
                    console.print(f"[bold cyan]Preview: Dropping columns {list(cols_to_drop)}[/bold cyan]")
                    confirm = inquirer.confirm("Do you want to proceed?").execute()
                    if confirm:
                        save_previous_state(df)
                        df = df.drop(columns=cols_to_drop)
                        console.print(f"[bold yellow]Dropped columns {list(cols_to_drop)}![/bold yellow]")

            elif missing_choice == "Fill Missing Values (Recommended)":
                fill_value = inquirer.text(message="Enter a value to fill missing cells:").execute()
                preview = preview_changes(df, "fill_missing", fill_value=fill_value)
                console.print("[bold cyan]Preview:[/bold cyan]")
                console.print(get_dataset_summary(preview))
                confirm = inquirer.confirm("Do you want to proceed?").execute()
                if confirm:
                    save_previous_state(df)
                    df = fill_missing_values(df, fill_value)
                    console.print(f"[bold yellow]Filled missing values with '{fill_value}'![/bold yellow]")

        elif action == "Remove Duplicates":
            preview = preview_changes(df, "remove_duplicates")
            console.print("[bold cyan]Preview:[/bold cyan]")
            console.print(get_dataset_summary(preview))
            confirm = inquirer.confirm("Do you want to proceed?").execute()
            if confirm:
                save_previous_state(df)
                df = remove_duplicates(df)
                console.print("[bold yellow]Duplicates removed![/bold yellow]")

        elif action == "Standardize Text":
            col = inquirer.select(message="Choose a column:", choices=list(df.columns)).execute()
            preview = preview_changes(df, "standardize_text", column=col)
            console.print("[bold cyan]Preview:[/bold cyan]")
            console.print(get_dataset_summary(preview))
            confirm = inquirer.confirm("Do you want to proceed?").execute()
            if confirm:
                save_previous_state(df)
                df = standardize_text(df, col)
                console.print(f"[bold yellow]Standardized text in '{col}'![/bold yellow]")

        elif action == "Fix Column Names":
            preview = preview_changes(df, "fix_column_names")
            console.print("[bold cyan]Preview new column names:[/bold cyan]")
            for old, new in zip(df.columns, preview.columns):
                console.print(f"{old} → {new}")
            confirm = inquirer.confirm("Do you want to proceed?").execute()
            if confirm:
                save_previous_state(df)
                df = fix_column_names(df)
                console.print("[bold yellow]Column names standardized![/bold yellow]")

        elif action == "Convert Column Types":
            col = inquirer.select(message="Choose a column to convert:", choices=list(df.columns)).execute()
            target_type = inquirer.select(
                message="Convert to which type?",
                choices=["string", "integer", "float", "datetime", "category", "boolean"]
            ).execute()
            try:
                preview = preview_changes(df, "convert_column_types", column=col, target_type=target_type)
                console.print("[bold cyan]Preview:[/bold cyan]")
                console.print(get_dataset_summary(preview))
                confirm = inquirer.confirm("Do you want to proceed?").execute()
                if confirm:
                    save_previous_state(df)
                    df = convert_column_types(df, col, target_type)
                    console.print(f"[bold yellow]Converted '{col}' to {target_type}![/bold yellow]")
            except Exception as e:
                console.print(f"[bold red]Conversion failed: {str(e)}[/bold red]")

        elif action == "Remove Outliers":
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if not numeric_cols:
                console.print("[bold red]No numeric columns found for outlier removal![/bold red]")
                continue
            
            col = inquirer.select(message="Choose a numeric column:", choices=numeric_cols).execute()
            method = inquirer.select(
                message="Choose outlier detection method:",
                choices=["IQR (Interquartile Range)", "Z-Score", "Percentile"]
            ).execute()
            
            try:
                preview = preview_changes(df, "remove_outliers", column=col, method=method.split(" ")[0].lower())
                console.print("[bold cyan]Preview:[/bold cyan]")
                console.print(get_dataset_summary(preview))
                confirm = inquirer.confirm("Do you want to proceed?").execute()
                if confirm:
                    save_previous_state(df)
                    df = remove_outliers(df, col, method.split(" ")[0].lower())
                    console.print(f"[bold yellow]Removed outliers from '{col}'![/bold yellow]")
            except Exception as e:
                console.print(f"[bold red]Outlier removal failed: {str(e)}[/bold red]")

        elif action == "Undo Last Change":
            if previous_states:
                df = previous_states.pop()
                console.print("[bold green]Reverted to the last state![/bold green]")
            else:
                console.print("[bold red]No previous state found![/bold red]")

        elif action == "Save & Exit":
            output_file = "cleaned_" + dataset
            save_dataset(df, output_file)
            console.print(f"[bold green]Cleaned data saved as {output_file}![/bold green]")
            break

    return df


# Main CLI Entry Point
@app.command()
def clean():
    show_banner()
    dataset = choose_dataset()
    df = load_dataset(dataset)
    console.print(get_dataset_summary(df))
    df = clean_data(df, dataset)


if __name__ == "__main__":
    app()