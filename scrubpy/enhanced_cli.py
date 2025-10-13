# Enhanced CLI with batch processing and smart workflows
import typer
from typing import Optional, List
from pathlib import Path
import json
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from InquirerPy import inquirer
import pandas as pd

from scrubpy.core import load_dataset, get_dataset_summary, save_dataset
from scrubpy.chat_assistant import start_dataset_chat
from scrubpy.quality_analyzer import analyze_data_quality
from scrubpy.column_insights import get_column_insights
from scrubpy.smart_eda import generate_smart_eda_pdf

app = typer.Typer(rich_markup_mode="rich")
console = Console()

class ScrubPyConfig:
    """Configuration management for ScrubPy"""
    
    def __init__(self):
        self.config_file = Path.home() / ".scrubpy" / "config.yaml"
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            'llm': {
                'model': 'mistral',
                'use_ollama': True,
                'temperature': 0.3
            },
            'cleaning': {
                'auto_preview': True,
                'backup_enabled': True,
                'default_fill_value': 'N/A'
            },
            'output': {
                'default_format': 'csv',
                'include_timestamp': True,
                'generate_report': True
            },
            'ui': {
                'show_welcome': True,
                'color_theme': 'blue'
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

# Global config instance
config = ScrubPyConfig()

@app.command()
def chat(
    file: Optional[str] = typer.Argument(None, help="CSV file to analyze"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model to use")
):
    """💬 Start an interactive chat session with your dataset"""
    
    if not file:
        # Auto-discover CSV files
        csv_files = list(Path(".").glob("*.csv"))
        if not csv_files:
            console.print("[red]No CSV files found in current directory[/red]")
            raise typer.Exit(1)
        
        if len(csv_files) == 1:
            file = str(csv_files[0])
        else:
            file = inquirer.select(
                message="Choose a dataset:",
                choices=[str(f) for f in csv_files]
            ).execute()
    
    # Load dataset
    console.print(f"[blue]Loading {file}...[/blue]")
    df = load_dataset(file)
    if df is None:
        console.print("[red]Failed to load dataset[/red]")
        raise typer.Exit(1)
    
    # Update LLM model if specified
    if model:
        config.set('llm.model', model)
    
    # Start chat session
    start_dataset_chat(df, Path(file).stem)

@app.command()
def analyze(
    file: str = typer.Argument(..., help="CSV file to analyze"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for analysis report"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, yaml, or txt")
):
    """Run comprehensive data quality analysis"""
    
    # Load dataset
    console.print(f"[blue]File Loading {file}...[/blue]")
    df = load_dataset(file)
    if df is None:
        console.print("[red]Error Failed to load dataset[/red]")
        raise typer.Exit(1)
    
    # Run analysis with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing data quality...", total=None)
        analysis_result = analyze_data_quality(df)
        progress.update(task, completed=100)
    
    # Display summary
    summary = analysis_result['summary']
    console.print(f"\n[bold cyan]Data Data Quality Analysis Results[/bold cyan]")
    console.print(f"Overall Score: [bold]{summary['overall_score']}/100[/bold] ({analysis_result['quality_grade']})")
    console.print(f"Total Issues: {summary['total_issues']}")
    
    # Show issues by severity
    issues_table = Table(title="Issues by Severity")
    issues_table.add_column("Severity", style="bold")
    issues_table.add_column("Count", justify="right")
    
    for severity, count in summary['issues_by_severity'].items():
        if count > 0:
            color = {"critical": "red", "high": "orange1", "medium": "yellow", "low": "blue"}.get(severity, "white")
            issues_table.add_row(severity.title(), str(count), style=color)
    
    console.print(issues_table)
    
    # Show top recommendations
    if analysis_result['recommendations']:
        console.print(f"\n[bold cyan]Tools Top Recommendations:[/bold cyan]")
        for i, rec in enumerate(analysis_result['recommendations'][:5], 1):
            priority_color = {"critical": "red", "high": "orange1", "medium": "yellow"}.get(rec['priority'], "blue")
            console.print(f"{i}. [{priority_color}]{rec['priority'].upper()}[/] - {rec['column']}: {rec['issue']}")
            console.print(f"   Tip {rec['fix']}")
    
    # Save report if requested
    if output or config.get('output.generate_report', True):
        if not output:
            output = f"{Path(file).stem}_quality_report.{format}"
        
        try:
            if format == "json":
                with open(output, 'w') as f:
                    json.dump(analysis_result, f, indent=2, default=str)
            elif format == "yaml":
                with open(output, 'w') as f:
                    yaml.dump(analysis_result, f, default_flow_style=False)
            elif format == "txt":
                with open(output, 'w') as f:
                    f.write(f"Data Quality Analysis Report\\n")
                    f.write(f"Generated: {summary['analysis_timestamp']}\\n\\n")
                    f.write(f"Overall Score: {summary['overall_score']}/100 ({analysis_result['quality_grade']})\\n")
                    f.write(f"Total Issues: {summary['total_issues']}\\n\\n")
                    f.write("Issues by Severity:\\n")
                    for severity, count in summary['issues_by_severity'].items():
                        if count > 0:
                            f.write(f"  {severity.title()}: {count}\\n")
                    f.write("\\nTop Recommendations:\\n")
                    for i, rec in enumerate(analysis_result['recommendations'][:10], 1):
                        f.write(f"{i}. {rec['priority'].upper()} - {rec['column']}: {rec['issue']}\\n")
                        f.write(f"   Fix: {rec['fix']}\\n")
            
            console.print(f"[green]Success Analysis report saved to {output}[/green]")
        except Exception as e:
            console.print(f"[red]Error Failed to save report: {e}[/red]")

@app.command()
def batch(
    directory: str = typer.Argument(".", help="Directory containing CSV files"),
    pattern: str = typer.Option("*.csv", "--pattern", "-p", help="File pattern to match"),
    output_dir: str = typer.Option("./scrubpy_output", "--output", "-o", help="Output directory"),
    operations: List[str] = typer.Option(["analyze", "insights"], "--ops", help="Operations to run: analyze, insights, eda, chat")
):
    """Process Process multiple datasets in batch mode"""
    
    input_path = Path(directory)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Find matching files
    csv_files = list(input_path.glob(pattern))
    if not csv_files:
        console.print(f"[red]Error No files matching '{pattern}' found in {directory}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[blue]Found {len(csv_files)} files to process[/blue]")
    
    # Process each file
    with Progress(console=console) as progress:
        main_task = progress.add_task("Processing files...", total=len(csv_files))
        
        for file_path in csv_files:
            progress.update(main_task, description=f"Processing {file_path.name}")
            
            try:
                # Load dataset
                df = load_dataset(str(file_path))
                if df is None:
                    console.print(f"[red]Error Failed to load {file_path.name}[/red]")
                    continue
                
                file_stem = file_path.stem
                
                # Run requested operations
                if "analyze" in operations:
                    analysis = analyze_data_quality(df)
                    with open(output_path / f"{file_stem}_analysis.json", 'w') as f:
                        json.dump(analysis, f, indent=2, default=str)
                
                if "insights" in operations:
                    insights = get_column_insights(df)
                    with open(output_path / f"{file_stem}_insights.json", 'w') as f:
                        json.dump(insights, f, indent=2, default=str)
                
                if "eda" in operations:
                    generate_smart_eda_pdf(df, dataset_name=file_stem, extra_data={"batch_mode": True})
                
                console.print(f"[green]Success Processed {file_path.name}[/green]")
                
            except Exception as e:
                console.print(f"[red]Error Error processing {file_path.name}: {e}[/red]")
            
            progress.advance(main_task)
    
    console.print(f"[green]Complete Batch processing complete! Results saved to {output_path}[/green]")

@app.command()
def config_cmd(
    key: Optional[str] = typer.Argument(None, help="Configuration key to get/set"),
    value: Optional[str] = typer.Argument(None, help="Value to set"),
    list_all: bool = typer.Option(False, "--list", "-l", help="List all configuration")
):
    """Config Manage ScrubPy configuration"""
    
    if list_all:
        console.print("[bold cyan]Current Configuration:[/bold cyan]")
        console.print(yaml.dump(config.config, default_flow_style=False))
        return
    
    if not key:
        console.print("[yellow]Available configuration keys:[/yellow]")
        console.print("- llm.model")
        console.print("- llm.use_ollama")
        console.print("- llm.temperature")
        console.print("- cleaning.auto_preview")
        console.print("- cleaning.backup_enabled")
        console.print("- output.default_format")
        console.print("- ui.show_welcome")
        return
    
    if value is None:
        # Get value
        current_value = config.get(key)
        console.print(f"{key} = {current_value}")
    else:
        # Set value
        # Try to parse as appropriate type
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        config.set(key, value)
        console.print(f"[green]Success Set {key} = {value}[/green]")

@app.command()
def insights(
    file: str = typer.Argument(..., help="CSV file to analyze"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for insights"),
    show_suggestions: bool = typer.Option(True, "--suggestions", help="Show transformation suggestions")
):
    """AI Generate intelligent column insights and suggestions"""
    
    # Load dataset
    console.print(f"[blue]File Loading {file}...[/blue]")
    df = load_dataset(file)
    if df is None:
        console.print("[red]Error Failed to load dataset[/red]")
        raise typer.Exit(1)
    
    # Generate insights
    console.print("[blue]AI Analyzing column roles and patterns...[/blue]")
    insights = get_column_insights(df)
    
    # Display insights table
    table = Table(title=f"Column Insights for {file}")
    table.add_column("Column", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Confidence", style="magenta")
    table.add_column("Key Insights", style="blue")
    
    for col, data in insights.items():
        # Format insights
        insight_details = []
        if "insights" in data:
            for k, v in data["insights"].items():
                if isinstance(v, bool) and v:
                    insight_details.append(k.replace("_", " "))
                elif k == "null_percent" and v > 0:
                    insight_details.append(f"{v}% null")
        
        insights_text = ", ".join(insight_details[:3])
        confidence_pct = f"{data['confidence'] * 100:.0f}%"
        
        table.add_row(
            col,
            data["role"].title(),
            data["type"],
            confidence_pct,
            insights_text
        )
    
    console.print(table)
    
    # Show suggestions if requested
    if show_suggestions:
        from scrubpy.column_insights import suggest_transformations
        suggestions = suggest_transformations(insights)
        
        if suggestions:
            console.print("\n[bold cyan]Analysis Transformation Suggestions:[/bold cyan]")
            for col, suggestion_list in suggestions.items():
                if suggestion_list:
                    console.print(f"[bold]{col}[/bold]:")
                    for suggestion in suggestion_list:
                        console.print(f"  • {suggestion}")
    
    # Save insights if requested
    if output:
        try:
            with open(output, 'w') as f:
                json.dump(insights, f, indent=2, default=str)
            console.print(f"[green]Success Insights saved to {output}[/green]")
        except Exception as e:
            console.print(f"[red]Error Failed to save insights: {e}[/red]")

@app.command()
def quick_clean(
    file: str = typer.Argument(..., help="CSV file to clean"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    operations: List[str] = typer.Option(["duplicates", "missing"], "--ops", help="Quick operations: duplicates, missing, outliers, types")
):
    """Quick automated cleaning with sensible defaults"""
    
    # Load dataset
    console.print(f"[blue]File Loading {file}...[/blue]")
    df = load_dataset(file)
    if df is None:
        console.print("[red]Error Failed to load dataset[/red]")
        raise typer.Exit(1)
    
    original_shape = df.shape
    console.print(f"[blue]Data Original shape: {original_shape[0]} rows × {original_shape[1]} columns[/blue]")
    
    # Apply quick operations
    if "duplicates" in operations:
        before_dups = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        removed_dups = before_dups - len(df)
        if removed_dups > 0:
            console.print(f"[green]Success Removed {removed_dups} duplicate rows[/green]")
    
    if "missing" in operations:
        # Simple strategy: drop columns with >50% missing, fill others with mode/median
        high_missing_cols = df.columns[df.isnull().mean() > 0.5]
        if len(high_missing_cols) > 0:
            df = df.drop(columns=high_missing_cols)
            console.print(f"[green]Success Dropped {len(high_missing_cols)} columns with >50% missing data[/green]")
        
        # Fill remaining missing values
        for col in df.columns:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown')
        console.print("[green]Success Filled remaining missing values[/green]")
    
    if "outliers" in operations:
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            q1, q3 = df[col].quantile([0.25, 0.75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            before_outliers = len(df)
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            removed_outliers = before_outliers - len(df)
            if removed_outliers > 0:
                console.print(f"[green]Success Removed {removed_outliers} outliers from {col}[/green]")
    
    if "types" in operations:
        # Auto-convert obvious type mismatches
        for col in df.columns:
            if pd.api.types.is_object_dtype(df[col]):
                # Try numeric conversion
                try:
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    if numeric_series.notna().sum() / len(df) > 0.8:  # 80% successfully converted
                        df[col] = numeric_series
                        console.print(f"[green]Success Converted {col} to numeric[/green]")
                        continue
                except:
                    pass
                
                # Try datetime conversion
                try:
                    datetime_series = pd.to_datetime(df[col], errors='coerce')
                    if datetime_series.notna().sum() / len(df) > 0.8:
                        df[col] = datetime_series
                        console.print(f"[green]Success Converted {col} to datetime[/green]")
                except:
                    pass
    
    final_shape = df.shape
    console.print(f"[blue]Data Final shape: {final_shape[0]} rows × {final_shape[1]} columns[/blue]")
    console.print(f"[blue]Changes: {original_shape[0] - final_shape[0]} rows removed, {original_shape[1] - final_shape[1]} columns removed[/blue]")
    
    # Save cleaned dataset
    if not output:
        output = f"cleaned_{Path(file).name}"
    
    try:
        df.to_csv(output, index=False)
        console.print(f"[green]Complete Cleaned dataset saved to {output}[/green]")
    except Exception as e:
        console.print(f"[red]Error Failed to save cleaned dataset: {e}[/red]")

@app.command()
def interactive():
    """🎮 Launch the full interactive cleaning interface (original CLI)"""
    from scrubpy.cli import clean
    clean()

if __name__ == "__main__":
    app()
