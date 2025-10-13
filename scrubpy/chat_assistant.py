# Interactive Dataset Chat Assistant
import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from InquirerPy import inquirer
from scrubpy.llm_utils import LLMAssistant
from scrubpy.column_insights import get_column_insights
from scrubpy.core import get_dataset_summary

console = Console()

class DatasetChatAssistant:
    """
    Interactive chat interface for exploring and understanding datasets
    through natural language conversations with LLM
    """
    
    def __init__(self, df: pd.DataFrame, dataset_name: str = "dataset"):
        self.df = df
        self.dataset_name = dataset_name
        self.conversation_history = []
        self.insights_cache = {}
        self.llm_assistant = None
        self.session_stats = {
            "questions_asked": 0,
            "insights_generated": 0,
            "code_executed": 0
        }
        
    def initialize_llm(self):
        """Initialize LLM assistant with dataset context"""
        try:
            console.print("[yellow]Initializing AI assistant...[/yellow]")
            column_insights = get_column_insights(self.df)
            self.llm_assistant = LLMAssistant(
                df=self.df, 
                column_insights_data=column_insights,
                model="mistral",
                use_ollama=True
            )
            self.insights_cache["column_insights"] = column_insights
            console.print("[green]AI assistant ready![/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to initialize LLM: {str(e)}[/red]")
            return False
    
    def get_dataset_context_summary(self) -> str:
        """Generate a brief context about the dataset for conversation"""
        summary = []
        summary.append(f"Dataset: {self.dataset_name}")
        summary.append(f"📏 Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        
        # Data types summary
        dtypes = self.df.dtypes.value_counts()
        summary.append(f"🔢 Types: {dict(dtypes)}")
        
        # Missing data
        missing_pct = (self.df.isnull().sum().sum() / self.df.size) * 100
        summary.append(f"❓ Missing: {missing_pct:.1f}%")
        
        # Column insights preview
        if "column_insights" in self.insights_cache:
            roles = {}
            for col, data in self.insights_cache["column_insights"].items():
                role = data["role"]
                roles[role] = roles.get(role, 0) + 1
            summary.append(f"Detected roles: {dict(roles)}")
        
        return " | ".join(summary)
    
    def display_welcome(self):
        """Display welcome message and dataset overview"""
        welcome_text = f"""
# Dataset Chat Assistant

Welcome! I'm here to help you explore and understand your dataset through conversation.

**What I can help with:**
- Explain patterns and trends in your data
- Answer questions about specific columns or values
- Suggest data cleaning strategies based on your data's characteristics
- Generate insights and recommendations
- 🐍 Create Python code for custom analysis
- Identify data quality issues

**Dataset Overview:**
{self.get_dataset_context_summary()}

**Quick Start Commands:**
- "describe [column]" - Get detailed info about a column
- "find patterns in [column]" - Discover data patterns
- "suggest cleaning steps" - Get cleaning recommendations
- "show me outliers" - Identify anomalous data
- "generate code for [task]" - Create Python code
- "help" - Show all available commands
"""
        console.print(Panel(Markdown(welcome_text), title="Dataset Chat Assistant", border_style="blue"))
    
    def process_quick_commands(self, user_input: str) -> Optional[str]:
        """Handle predefined quick commands"""
        input_lower = user_input.lower().strip()
        
        # Help command
        if input_lower in ["help", "?", "commands"]:
            return """
**Available Quick Commands:**
- `describe [column]` - Detailed column analysis
- `find patterns in [column]` - Pattern discovery
- `suggest cleaning` - Cleaning recommendations  
- `show outliers` - Outlier detection
- `data quality score` - Overall quality assessment
- `missing values analysis` - Missing data insights
- `correlation analysis` - Find relationships
- `generate code for [task]` - Python code generation
- `export insights` - Save conversation insights
- `stats` - Show session statistics
"""
        
        # Column description
        if input_lower.startswith("describe "):
            col_name = user_input[9:].strip()
            if col_name in self.df.columns:
                return self.describe_column(col_name)
            else:
                return f"Column '{col_name}' not found. Available columns: {list(self.df.columns)}"
        
        # Show statistics
        if input_lower == "stats":
            return f"""
**Session Statistics:**
- Questions asked: {self.session_stats['questions_asked']}
- Insights generated: {self.session_stats['insights_generated']}
- Code blocks executed: {self.session_stats['code_executed']}
- Conversation length: {len(self.conversation_history)} exchanges
"""
        
        # Data quality score
        if "data quality" in input_lower:
            return self.calculate_data_quality_score()
        
        return None
    
    def describe_column(self, column: str) -> str:
        """Generate detailed description of a specific column"""
        if column not in self.df.columns:
            return f"Column '{column}' not found."
        
        series = self.df[column]
        description = []
        
        # Basic stats
        description.append(f"**Column: {column}**")
        description.append(f"- Type: {series.dtype}")
        description.append(f"- Non-null values: {series.count()}/{len(series)} ({series.count()/len(series)*100:.1f}%)")
        description.append(f"- Unique values: {series.nunique()}")
        
        # Type-specific analysis
        if pd.api.types.is_numeric_dtype(series):
            description.append(f"- Range: {series.min()} to {series.max()}")
            description.append(f"- Mean: {series.mean():.2f}")
            description.append(f"- Std: {series.std():.2f}")
            
            # Outliers
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            outliers = series[(series < q1 - 1.5*iqr) | (series > q3 + 1.5*iqr)]
            description.append(f"- Outliers (IQR): {len(outliers)} values")
        
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            description.append(f"- Most common: '{series.mode().iloc[0] if not series.mode().empty else 'N/A'}'")
            description.append(f"- Average length: {series.astype(str).str.len().mean():.1f} characters")
            
            # Show top values
            top_values = series.value_counts().head(3)
            description.append("- Top values:")
            for val, count in top_values.items():
                description.append(f"  • '{val}': {count} times")
        
        # Column insights if available
        if "column_insights" in self.insights_cache:
            col_insight = self.insights_cache["column_insights"].get(column, {})
            if col_insight:
                role = col_insight.get("role", "unknown")
                confidence = col_insight.get("confidence", 0) * 100
                description.append(f"- Detected role: {role} ({confidence:.0f}% confidence)")
        
        return "\n".join(description)
    
    def calculate_data_quality_score(self) -> str:
        """Calculate and explain data quality score"""
        score_components = {}
        
        # Missing data score (0-25 points)
        missing_pct = (self.df.isnull().sum().sum() / self.df.size) * 100
        missing_score = max(0, 25 - missing_pct)
        score_components["Missing Data"] = f"{missing_score:.1f}/25 ({missing_pct:.1f}% missing)"
        
        # Duplicate score (0-20 points)
        dup_pct = (self.df.duplicated().sum() / len(self.df)) * 100
        dup_score = max(0, 20 - dup_pct)
        score_components["Duplicates"] = f"{dup_score:.1f}/20 ({dup_pct:.1f}% duplicates)"
        
        # Column naming score (0-15 points)
        good_names = sum(1 for col in self.df.columns if col == col.lower().replace(' ', '_'))
        naming_score = (good_names / len(self.df.columns)) * 15
        score_components["Column Names"] = f"{naming_score:.1f}/15 ({good_names}/{len(self.df.columns)} good names)"
        
        # Type consistency score (0-20 points)
        type_score = 20  # Start with perfect score
        for col in self.df.columns:
            if pd.api.types.is_object_dtype(self.df[col]):
                # Check if numeric data is stored as strings
                try:
                    pd.to_numeric(self.df[col].dropna().sample(min(100, len(self.df[col].dropna()))))
                    type_score -= 2  # Penalty for potential numeric data as string
                except:
                    pass
        type_score = max(0, type_score)
        score_components["Type Consistency"] = f"{type_score:.1f}/20"
        
        # Data balance score (0-20 points)
        balance_score = 20
        for col in self.df.select_dtypes(include=['object']).columns:
            if self.df[col].nunique() == 1:
                balance_score -= 3  # Penalty for constant columns
        balance_score = max(0, balance_score)
        score_components["Data Balance"] = f"{balance_score:.1f}/20"
        
        total_score = sum(float(score.split('/')[0]) for score in score_components.values())
        
        result = f"""
**Data Quality Score: {total_score:.1f}/100**

**Component Breakdown:**
"""
        for component, score in score_components.items():
            result += f"- {component}: {score}\n"
        
        # Quality rating
        if total_score >= 85:
            rating = "🟢 Excellent"
        elif total_score >= 70:
            rating = "🟡 Good"
        elif total_score >= 50:
            rating = "🟠 Fair"
        else:
            rating = "🔴 Poor"
        
        result += f"\n**Overall Rating: {rating}**"
        
        return result
    
    def ask_llm(self, question: str, context: str = "") -> str:
        """Ask LLM a question with proper context"""
        if not self.llm_assistant:
            return "AI assistant not initialized. Please restart the chat."
        
        try:
            # Add dataset context to question
            enhanced_question = f"""
Dataset Context: {self.get_dataset_context_summary()}

User Question: {question}

{context}

Please provide a clear, actionable response that helps the user understand their data better.
"""
            response = self.llm_assistant.ask(enhanced_question, task="dataset_chat")
            self.session_stats["questions_asked"] += 1
            return response
        except Exception as e:
            return f"Error communicating with AI: {str(e)}"
    
    def save_conversation(self) -> str:
        """Save conversation history to file"""
        filename = f"chat_session_{self.dataset_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        conversation_data = {
            "dataset_name": self.dataset_name,
            "dataset_shape": self.df.shape,
            "session_stats": self.session_stats,
            "conversation": self.conversation_history,
            "insights_cache": self.insights_cache
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(conversation_data, f, indent=2, default=str)
            return f"💾 Conversation saved to {filename}"
        except Exception as e:
            return f"Failed to save conversation: {str(e)}"
    
    def run_chat_session(self):
        """Main chat loop"""
        if not self.initialize_llm():
            console.print("[red]Cannot start chat without LLM. Please check your Ollama installation.[/red]")
            return
        
        self.display_welcome()
        
        while True:
            try:
                # Get user input
                user_input = inquirer.text(
                    message="💬 Ask me about your data (or 'quit' to exit):"
                ).execute()
                
                if not user_input or user_input.lower().strip() in ['quit', 'exit', 'q']:
                    break
                
                # Check for quick commands first
                quick_response = self.process_quick_commands(user_input)
                if quick_response:
                    console.print(Panel(Markdown(quick_response), border_style="green"))
                    self.conversation_history.append({
                        "user": user_input,
                        "assistant": quick_response,
                        "type": "quick_command"
                    })
                    continue
                
                # Send to LLM
                console.print("[yellow]🤔 Thinking...[/yellow]")
                response = self.ask_llm(user_input)
                
                # Display response
                console.print(Panel(Markdown(response), title="AI Assistant", border_style="blue"))
                
                # Store in history
                self.conversation_history.append({
                    "user": user_input,
                    "assistant": response,
                    "type": "llm_response"
                })
                
                # Ask if user wants to save insights or generate code
                if len(self.conversation_history) % 5 == 0:  # Every 5 exchanges
                    save_option = inquirer.confirm(
                        "💾 Would you like to save this conversation session?",
                        default=False
                    ).execute()
                    if save_option:
                        save_result = self.save_conversation()
                        console.print(f"[green]{save_result}[/green]")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
        
        # Final save offer
        if self.conversation_history:
            final_save = inquirer.confirm(
                "💾 Save this conversation before exiting?",
                default=True
            ).execute()
            if final_save:
                save_result = self.save_conversation()
                console.print(f"[green]{save_result}[/green]")
        
        console.print("\n[blue]👋 Thanks for chatting! Your insights have been preserved.[/blue]")


def start_dataset_chat(df: pd.DataFrame, dataset_name: str = "dataset"):
    """Entry point for starting a dataset chat session"""
    chat_assistant = DatasetChatAssistant(df, dataset_name)
    chat_assistant.run_chat_session()


def main():
    """Main entry point for console script"""
    import sys
    from scrubpy.core import load_dataset
    
    if len(sys.argv) < 2:
        print("Usage: scrubpy-chat <dataset.csv>")
        print("Example: scrubpy-chat data.csv")
        sys.exit(1)
    
    dataset_file = sys.argv[1]
    try:
        df = load_dataset(dataset_file)
        if df is None:
            print(f"Failed to load dataset: {dataset_file}")
            sys.exit(1)
        
        start_dataset_chat(df, dataset_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
