"""
llm_utils.py - Advanced LLM Integration Utilities for ScrubPy

This module serves as the bridge between structured data analysis and language model intelligence.
It transforms dataset metadata and samples into optimized prompts for LLMs, enabling AI-assisted
data cleaning and analysis without exceeding token limits or computational constraints.

Key capabilities:
- Format column insights into token-efficient summaries
- Sample strategic data snapshots to provide context
- Generate specialized prompts for different cleaning tasks
- Execute LLM calls with appropriate backends (Ollama, API)
- Parse and structure LLM responses for further processing
- Generate executable Python code from natural language suggestions
"""

import json
import subprocess
import pandas as pd
import numpy as np
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union


def format_column_insights_for_prompt(
    column_insights_data: Dict[str, Dict[str, Any]], 
    max_cols: int = 15,
    include_sample_values: bool = True
) -> List[str]:
    """
    Convert column insight data into a condensed, token-efficient format for LLM prompts.
    
    Args:
        column_insights_data: Dictionary of column insights from get_column_insights()
        max_cols: Maximum number of columns to include (prioritizes by importance)
        include_sample_values: Whether to include sample values for each column
        
    Returns:
        List of formatted column insight strings
    """
    insights_summary = []
    
    # Handle empty or None column insights gracefully
    if not column_insights_data:
        return ["No column insights available"]
    
    # Sort columns by importance (prioritize ID, categorical, and numeric columns)
    def get_column_priority(col_data):
        role = col_data.get('role', '')
        confidence = col_data.get('confidence', 0)
        if role == 'id':
            return 10 * confidence
        elif role == 'categorical' and col_data.get('insights', {}).get('cardinality', 0) < 10:
            return 8 * confidence
        elif role in ['numeric', 'numeric_score']:
            return 7 * confidence
        elif role == 'datetime':
            return 6 * confidence
        else:
            return 5 * confidence
    
    sorted_columns = sorted(
        column_insights_data.items(), 
        key=lambda x: get_column_priority(x[1]), 
        reverse=True
    )
    
    # Take only the top columns based on max_cols
    top_columns = sorted_columns[:max_cols]
    
    for col, data in top_columns:
        # Basic column info
        summary = f"{col}: role={data['role']}, type={data['type']}, confidence={int(data['confidence'] * 100)}%"
        
        # Add key insights
        insights = data.get("insights", {})
        added_insights = []
        
        # Prioritize important insights
        if insights.get("null_percent", 0) > 0:
            added_insights.append(f"nulls={insights['null_percent']}%")
        
        if insights.get("cardinality") is not None:
            added_insights.append(f"cardinality={insights['cardinality']}")
            
        if insights.get("has_outliers", False):
            added_insights.append("has_outliers=true")
            
        # Add boolean flags for common issues
        for k, v in insights.items():
            if k not in ["null_percent", "cardinality", "has_outliers"] and isinstance(v, bool) and v:
                added_insights.append(f"{k.replace('_', '_')}=true")
        
        # Add sample values if requested and available
        if include_sample_values and "sample_values" in insights:
            samples = insights["sample_values"]
            if samples and len(samples) > 0:
                sample_str = ", ".join(str(s) for s in samples[:3])
                added_insights.append(f"samples=[{sample_str}]")
        
        # Combine everything
        if added_insights:
            summary += ", " + ", ".join(added_insights[:5])  # Limit to top 5 insights
            
        insights_summary.append(summary)
    
    return insights_summary


def sample_dataset_snapshot(
    df: pd.DataFrame, 
    max_rows: int = 5, 
    max_cols: int = 8,
    prioritize_nulls: bool = True,
    include_stats: bool = True
) -> Dict[str, Any]:
    """
    Creates a strategic sample of the dataset for LLM context.
    
    Args:
        df: Pandas DataFrame to sample
        max_rows: Maximum number of rows to include
        max_cols: Maximum number of columns to include
        prioritize_nulls: Whether to include rows with null values
        include_stats: Whether to include basic stats about the dataset
        
    Returns:
        Dictionary with dataset sample and optional statistics
    """
    result = {}
    
    # Basic dataset info
    result["dataset_size"] = {"rows": len(df), "columns": len(df.columns)}
    
    # Column prioritization - select most informative columns
    if len(df.columns) > max_cols:
        # Calculate information density per column (using entropy-like measures)
        col_info = {}
        for col in df.columns:
            # Get unique value count (adjusted for nulls)
            unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
            
            # Nulls percentage
            null_ratio = df[col].isna().mean()
            
            # Calculate info score (higher for columns with moderate cardinality and fewer nulls)
            # We want columns that have some variety but aren't just unique IDs
            if pd.api.types.is_numeric_dtype(df[col]):
                # For numeric: prioritize columns with reasonable distributions
                info_score = (0.5 - abs(0.5 - unique_ratio)) * (1 - null_ratio) * 1.2
            else:
                # For categorical/text: prioritize moderate cardinality
                info_score = (0.3 - abs(0.3 - unique_ratio)) * (1 - null_ratio)
                
            col_info[col] = info_score
            
        # Select top columns
        selected_cols = sorted(col_info.keys(), key=lambda x: col_info[x], reverse=True)[:max_cols]
        df_sample = df[selected_cols]
    else:
        df_sample = df
        
    # Row sampling strategy
    if prioritize_nulls and len(df) > max_rows:
        # Get some rows with nulls and some without
        null_rows = df_sample[df_sample.isna().any(axis=1)].head(max_rows // 2)
        non_null_rows = df_sample[~df_sample.isna().any(axis=1)].head(max_rows - len(null_rows))
        df_sample = pd.concat([null_rows, non_null_rows]).head(max_rows)
    else:
        # Simple random sample
        df_sample = df_sample.sample(min(max_rows, len(df)))
    
    # Add sample rows to result
    result["sample_rows"] = df_sample.replace({np.nan: None}).to_dict(orient="records")
    
    # Add basic statistics if requested
    if include_stats:
        stats = {}
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            stats["numeric"] = df[numeric_cols].describe().to_dict()
        
        # Get null percentages
        null_percent = (df.isna().mean() * 100).to_dict()
        stats["null_percentages"] = {k: f"{v:.1f}%" for k, v in null_percent.items() if v > 0}
        
        # Get duplicate info
        stats["duplicates"] = {
            "count": len(df) - len(df.drop_duplicates()),
            "percentage": f"{(1 - len(df.drop_duplicates()) / len(df)) * 100:.1f}%"
        }
        
        result["statistics"] = stats
    
    return result


def build_llm_prompt(
    insights_summary: List[str],
    dataset_snapshot: Dict[str, Any],
    task: str = "general_advice",
    additional_context: Optional[str] = None,
    user_question: Optional[str] = None
) -> str:
    """
    Build a comprehensive prompt for the LLM based on dataset information and task.
    
    Args:
        insights_summary: Formatted column insights from format_column_insights_for_prompt()
        dataset_snapshot: Dataset sample from sample_dataset_snapshot()
        task: Type of task for the LLM ("general_advice", "cleaning_plan", "code_generation", etc.)
        additional_context: Any additional context about the dataset or problem
        user_question: Optional specific question from the user
        
    Returns:
        Formatted prompt string for the LLM
    """
    # Define task-specific instructions
    task_instructions = {
        "general_advice": "Analyze this dataset and provide useful observations and cleaning suggestions.",
        "cleaning_plan": "Create a step-by-step cleaning plan for this dataset, addressing the main issues.",
        "code_generation": "Generate Python code snippets that would help clean the main issues in this dataset.",
        "column_analysis": "Analyze each column in detail, suggesting appropriate transformations.",
        "validate_data": "Validate this data against common business rules and identify potential errors.",
        "imputation": "Suggest the best strategies for imputing missing values in this dataset.",
        "outlier_detection": "Identify potential outliers in this dataset and recommend handling approaches.",
    }
    
    # Build the prompt
    prompt_parts = [
        "You are a data cleaning and analysis expert helping improve a dataset.",
        f"TASK: {task_instructions.get(task, task_instructions['general_advice'])}"
    ]
    
    # Add user question if provided
    if user_question:
        prompt_parts.append(f"USER QUESTION: {user_question}")
    
    # Add additional context if provided
    if additional_context:
        prompt_parts.append(f"CONTEXT: {additional_context}")
    
    # Add dataset size information
    size_info = dataset_snapshot.get("dataset_size", {})
    if size_info:
        prompt_parts.append(f"DATASET SIZE: {size_info['rows']} rows × {size_info['columns']} columns")
    
    # Add column insights
    prompt_parts.append("COLUMN INSIGHTS:")
    for insight in insights_summary:
        prompt_parts.append(f"- {insight}")
    
    # Add sample rows
    sample_rows = dataset_snapshot.get("sample_rows", [])
    if sample_rows:
        prompt_parts.append("SAMPLE ROWS:")
        sample_json = json.dumps(sample_rows, indent=2)
        prompt_parts.append(sample_json)
    
    # Add statistics if available
    if "statistics" in dataset_snapshot:
        stats = dataset_snapshot["statistics"]
        
        if "null_percentages" in stats and stats["null_percentages"]:
            prompt_parts.append("NULL PERCENTAGES:")
            for col, pct in stats["null_percentages"].items():
                prompt_parts.append(f"- {col}: {pct}")
        
        if "duplicates" in stats:
            dup_info = stats["duplicates"]
            prompt_parts.append(f"DUPLICATES: {dup_info['count']} rows ({dup_info['percentage']})")
    
    # Add task-specific instructions based on task type
    if task == "code_generation":
        prompt_parts.append(
            "Generate executable Python code using pandas and numpy that addresses the main "
            "issues in this dataset. Format each snippet as a function with clear comments."
        )
    elif task == "cleaning_plan":
        prompt_parts.append(
            "Create a numbered list of cleaning steps in priority order. For each step, "
            "explain why it's necessary and what potential impact it would have."
        )
    
    # Final instructions
    prompt_parts.append(
        "Respond with clear, concise, and practical advice. Focus on the most important issues first."
    )
    
    return "\n\n".join(prompt_parts)


def _calculate_adaptive_timeout(prompt: str) -> int:
    """Calculate adaptive timeout based on prompt complexity"""
    base_timeout = 30
    
    # Estimate complexity factors
    prompt_length = len(prompt)
    word_count = len(prompt.split())
    
    # Add time based on length - be more aggressive with longer prompts
    if prompt_length > 2000:
        base_timeout += 60  # Give much more time for very long prompts
    elif prompt_length > 1000:
        base_timeout += 30
    elif prompt_length > 500:
        base_timeout += 15
    
    # Add time for complex operations
    complexity_indicators = [
        "analyze", "generate", "comprehensive", "detailed", 
        "explain", "describe", "quality", "profiling"
    ]
    
    complexity_score = sum(1 for indicator in complexity_indicators 
                          if indicator in prompt.lower())
    
    if complexity_score > 3:
        base_timeout += 60  # Much more time for complex analysis
    elif complexity_score > 1:
        base_timeout += 30
    
    # Maximum timeout to prevent infinite waits
    return min(base_timeout, 180)  # Allow up to 3 minutes for complex queries


def _compress_prompt_for_fallback(prompt: str) -> str:
    """Compress prompt for fallback when timeout occurs"""
    
    # Split into lines and keep essential parts
    lines = prompt.split('\n')
    essential_lines = []
    
    for line in lines:
        line = line.strip()
        # Keep lines with key information
        if any(keyword in line.lower() for keyword in [
            'dataset:', 'shape:', 'columns:', 'question:', 'missing', 'duplicate'
        ]):
            essential_lines.append(line)
        
        # Limit to avoid another timeout
        if len(essential_lines) >= 6:
            break
    
    # Add simple instruction if none found
    if not any('question:' in line.lower() for line in essential_lines):
        essential_lines.append("Question: Brief quality summary")
    
    compressed = '\n'.join(essential_lines)
    
    # Further compress if still too long
    if len(compressed) > 300:
        # Keep only the most essential parts
        key_info = []
        for line in essential_lines:
            if any(keyword in line.lower() for keyword in ['dataset:', 'question:']):
                key_info.append(line)
        
        if len(key_info) >= 2:
            return '\n'.join(key_info)
    
    return compressed


def _create_ultra_simple_query(prompt: str) -> str:
    """Create ultra-simple query for final fallback"""
    import re
    
    # Extract numbers for basic analysis
    missing_match = re.search(r'(\d+)\s+cells?', prompt)
    duplicate_match = re.search(r'(\d+)\s+rows?', prompt)
    
    if missing_match:
        missing_count = int(missing_match.group(1))
        if missing_count > 1000:
            return "High missing data detected. Requires cleaning. One sentence summary."
        else:
            return "Some missing data found. Generally good quality. One sentence."
    
    if duplicate_match:
        dup_count = int(duplicate_match.group(1))
        if dup_count > 100:
            return "Many duplicates found. Needs deduplication. One sentence."
        else:
            return "Few duplicates detected. Good data quality. One sentence."
    
    return "Data quality assessment: one sentence summary."


def _generate_template_response(prompt: str) -> str:
    """Generate template response when all LLM attempts fail"""
    import re
    
    # Analyze prompt to determine appropriate template
    prompt_lower = prompt.lower()
    
    # Extract key metrics for template
    missing_match = re.search(r'(\d+)\s+cells?', prompt)
    duplicate_match = re.search(r'(\d+)\s+rows?', prompt) 
    rows_match = re.search(r'(\d+)\s+rows', prompt)
    cols_match = re.search(r'(\d+)\s+columns?', prompt)
    
    response_parts = []
    
    # Basic info
    if rows_match and cols_match:
        rows = int(rows_match.group(1))
        cols = int(cols_match.group(1))
        response_parts.append(f"Dataset contains {rows:,} rows and {cols} columns.")
    
    # Missing data analysis
    if missing_match:
        missing_count = int(missing_match.group(1))
        if rows_match:
            total_cells = int(rows_match.group(1)) * int(cols_match.group(1)) if cols_match else missing_count * 10
            missing_pct = (missing_count / total_cells) * 100
            
            if missing_pct > 15:
                response_parts.append(f"HIGH missing data: {missing_count:,} cells ({missing_pct:.1f}%) - requires immediate attention.")
            elif missing_pct > 5:
                response_parts.append(f"MODERATE missing data: {missing_count:,} cells ({missing_pct:.1f}%) - manageable with imputation.")
            else:
                response_parts.append(f"LOW missing data: {missing_count:,} cells ({missing_pct:.1f}%) - minimal impact.")
        else:
            response_parts.append(f"Missing data detected: {missing_count:,} cells require attention.")
    
    # Duplicate analysis
    if duplicate_match:
        dup_count = int(duplicate_match.group(1))
        if dup_count > 1000:
            response_parts.append(f"HIGH duplicates: {dup_count:,} rows - significant deduplication needed.")
        elif dup_count > 100:
            response_parts.append(f"MODERATE duplicates: {dup_count:,} rows - standard deduplication recommended.")
        elif dup_count > 0:
            response_parts.append(f"LOW duplicates: {dup_count:,} rows - minor cleanup needed.")
    
    # Quality assessment
    if 'quality' in prompt_lower:
        if missing_match and duplicate_match:
            missing_count = int(missing_match.group(1))
            dup_count = int(duplicate_match.group(1))
            
            if missing_count > 10000 or dup_count > 1000:
                response_parts.append("OVERALL QUALITY: POOR - Major cleaning required before analysis.")
            elif missing_count > 1000 or dup_count > 100:
                response_parts.append("OVERALL QUALITY: FAIR - Standard cleaning workflow recommended.")
            else:
                response_parts.append("OVERALL QUALITY: GOOD - Minor cleaning needed, ready for analysis.")
    
    # Recommendations
    recommendations = []
    if missing_match and int(missing_match.group(1)) > 0:
        recommendations.append("Handle missing values (imputation or removal)")
    if duplicate_match and int(duplicate_match.group(1)) > 0:
        recommendations.append("Remove duplicate entries")
    
    if recommendations:
        response_parts.append(f"🛠️ RECOMMENDED ACTIONS: {', '.join(recommendations)}.")
    
    # Combine response
    if response_parts:
        final_response = " ".join(response_parts)
    else:
        final_response = "Data quality analysis: Dataset appears to have standard characteristics. Recommend basic data profiling and cleaning workflow."
    
    return f"[Template Analysis - Ollama Unavailable] {final_response}"


def execute_llm_query(
    prompt: str, 
    model: str = "mistral",
    use_ollama: bool = True,
    max_tokens: int = 1000,
    temperature: float = 0.3
) -> str:
    """
    Execute a query against an LLM using either Ollama or an API.
    
    Args:
        prompt: The prompt to send to the LLM
        model: Model name to use (default: "mistral")
        use_ollama: Whether to use Ollama (local) or an API
        max_tokens: Maximum tokens in the response
        temperature: Temperature for generation (lower = more focused)
        
    Returns:
        LLM response text
    """
    if use_ollama:
        # Use subprocess to call Ollama with intelligent timeout and robust fallbacks
        try:
            # Calculate adaptive timeout based on prompt complexity
            timeout = _calculate_adaptive_timeout(prompt)
            
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout
            )
            
            if result.returncode != 0:
                error = result.stderr.decode()
                # Log the error and return a helpful message
                return f"Error calling LLM: {error[:200]}... (Is Ollama running?)"
            
            return result.stdout.decode()
            
        except FileNotFoundError:
            return ("Ollama not found! To use AI features, please install Ollama:\n"
                   "1. Visit: https://ollama.com/download\n"
                   "2. Install Ollama for your system\n" 
                   "3. Run: ollama pull mistral\n"
                   "4. Try the AI features again!")
            
        except subprocess.TimeoutExpired:
            # Try fallback strategy 1: compressed prompt
            try:
                compressed_prompt = _compress_prompt_for_fallback(prompt)
                fallback_timeout = min(timeout * 0.6, 60)  # 60% of original timeout, max 60 seconds
                
                result = subprocess.run(
                    ["ollama", "run", model],
                    input=compressed_prompt.encode(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=fallback_timeout
                )
            except FileNotFoundError:
                return ("Ollama not found! To use AI features, please install Ollama:\n"
                       "Visit: https://ollama.com/download")
                
                if result.returncode == 0:
                    response = result.stdout.decode()
                    return f"[Compressed Analysis] {response}"
                
            except subprocess.TimeoutExpired:
                # Try fallback strategy 2: ultra-simple query
                try:
                    simple_prompt = _create_ultra_simple_query(prompt)
                    ultra_timeout = 30
                    
                    result = subprocess.run(
                        ["ollama", "run", model],
                        input=simple_prompt.encode(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=ultra_timeout
                    )
                    
                    if result.returncode == 0:
                        response = result.stdout.decode()
                        return f"[Quick Analysis] {response}"
                
                except:
                    # Final fallback: return template response
                    return _generate_template_response(prompt)
            
            except Exception:
                # Try the ultra-simple query
                try:
                    simple_prompt = _create_ultra_simple_query(prompt)
                    result = subprocess.run(
                        ["ollama", "run", model],
                        input=simple_prompt.encode(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=30
                    )
                except FileNotFoundError:
                    return ("Ollama not found! To use AI features, please install Ollama:\n"
                           "Visit: https://ollama.com/download")
                    
                    if result.returncode == 0:
                        response = result.stdout.decode()
                        return f"[Simple Analysis] {response}"
                
                except:
                    return _generate_template_response(prompt)
            
            # If we reach here, all attempts failed
            return _generate_template_response(prompt)
            
        except Exception as e:
            return f"Error executing LLM query: {str(e)}"
    else:
        # For future API implementation
        return "API execution not yet implemented."


def extract_code_from_llm_response(response: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from LLM response for potential execution.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        List of dictionaries with code blocks, each with 'code', 'language', and 'description'
    """
    # Look for code blocks with markdown formatting
    code_blocks = []
    
    # Pattern to match ```python ... ``` blocks
    pattern = r"```(python|py|)\s*(.*?)```"
    matches = re.finditer(pattern, response, re.DOTALL)
    
    for match in matches:
        language = match.group(1) or "python"
        code = match.group(2).strip()
        
        # Try to extract a description from above the code block
        code_start = match.start()
        prev_text = response[:code_start].strip()
        lines = prev_text.split("\n")
        description = lines[-1] if lines else "Generated code"
        
        # Clean up description
        description = re.sub(r"^[#\d\.\s:-]*", "", description).strip()
        if not description or len(description) < 5:
            description = "Generated data cleaning function"
        
        code_blocks.append({
            "code": code,
            "language": language,
            "description": description
        })
    
    return code_blocks


def execute_generated_code(
    code: str, 
    df: pd.DataFrame, 
    safe_mode: bool = True
) -> Tuple[bool, Union[pd.DataFrame, None], str]:
    """
    Safely execute code generated by the LLM on the DataFrame.
    
    Args:
        code: Python code string to execute
        df: Input DataFrame
        safe_mode: Whether to run in safe mode (prevents certain operations)
        
    Returns:
        Tuple of (success, result_df, message)
    """
    # Safety checks - prevent risky operations
    if safe_mode:
        risky_patterns = [
            r"import\s+(?!pandas|numpy|re|math|scipy|scikit|seaborn|matplotlib)",  # Restrict imports
            r"open\s*\(",  # File operations
            r"exec\s*\(",  # Code execution
            r"eval\s*\(",  # Code evaluation
            r"os\.",  # OS operations
            r"system\s*\(",  # System calls
            r"subprocess",  # Subprocess calls
            r"drop\s*\(\s*(?!columns)",  # Prevent drop() without columns= 
            r"reset_index\s*\(\s*drop\s*=\s*True",  # Prevent index dropping
        ]
        
        for pattern in risky_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, None, f"Safety check failed: Found potentially unsafe operation matching {pattern}"
    
    # Prepare environment for execution
    local_vars = {"df": df.copy(), "pd": pd, "np": np}

    # Modify the code to return the processed dataframe
    # First, check if the code already defines a function
    if re.search(r"def\s+\w+\s*\(", code):
        # Code has a function definition, let's try to extract and call it
        try:
            # Execute code to define the function
            exec(code, globals(), local_vars)
            
            # Find the function name
            func_match = re.search(r"def\s+(\w+)\s*\(", code)
            if func_match:
                func_name = func_match.group(1)
                
                # Call the function with df as argument
                func_code = f"result = {func_name}(df)"
                exec(func_code, globals(), local_vars)
                
                result_df = local_vars.get("result")
                if isinstance(result_df, pd.DataFrame):
                    return True, result_df, "Successfully executed function and applied changes."
                else:
                    return False, None, f"Function {func_name} did not return a DataFrame."
            else:
                return False, None, "Could not identify function name for execution."
                
        except Exception as e:
            return False, None, f"Error executing function: {str(e)}"
    else:
        # No function defined, wrap the code in one
        wrapped_code = f"""
def process_dataframe(df):
    import pandas as pd
    import numpy as np
    
    # Original code
{textwrap.indent(code, '    ')}
    
    # Return dataframe
    return df

result = process_dataframe(df)
"""
        try:
            exec(wrapped_code, globals(), local_vars)
            result_df = local_vars.get("result")
            if isinstance(result_df, pd.DataFrame):
                return True, result_df, "Successfully executed code and applied changes."
            else:
                return False, None, "Code did not return a DataFrame."
                
        except Exception as e:
            return False, None, f"Error executing code: {str(e)}"


def generate_cleaning_plan(df: pd.DataFrame, column_insights: Dict[str, Any]) -> str:
    """
    Generate a comprehensive data cleaning plan using the LLM.
    
    Args:
        df: Input DataFrame
        column_insights: Column insights dictionary
        
    Returns:
        Cleaning plan as text
    """
    # Format column insights
    insights_summary = format_column_insights_for_prompt(column_insights)
    
    # Get dataset snapshot
    dataset_snapshot = sample_dataset_snapshot(df)
    
    # Build prompt specifically for cleaning plan
    prompt = build_llm_prompt(
        insights_summary=insights_summary,
        dataset_snapshot=dataset_snapshot,
        task="cleaning_plan"
    )
    
    # Execute LLM query
    response = execute_llm_query(prompt)
    
    return response


# Helper function to handle column insights when some may be missing
def ensure_column_insights(
    df: pd.DataFrame, 
    column_insights_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Ensure we have column insights data, generating it if needed.
    
    Args:
        df: Input DataFrame
        column_insights_data: Existing column insights if available
        
    Returns:
        Column insights dictionary
    """
    if column_insights_data is None or not column_insights_data:
        # Import here to avoid circular imports
        try:
            from scrubpy.column_insights import get_column_insights
            return get_column_insights(df)
        except Exception as e:
            # If column insights fail, return a minimal fallback
            return {col: {
                'role': 'unknown', 
                'type': str(df[col].dtype), 
                'confidence': 0.5,
                'insights': {'null_percent': df[col].isnull().mean() * 100}
            } for col in df.columns}
    return column_insights_data


import textwrap
import hashlib
import time


class EnhancedLLMClient:
    """
    Enhanced LLM Client for web application integration.
    Provides a simplified interface for LLM operations without requiring pre-initialized data.
    """
    
    def __init__(self, model: str = "mistral", use_ollama: bool = True):
        self.model = model
        self.use_ollama = use_ollama
        self.cached_responses = {}
        
    def process_query(self, prompt: str, timeout: int = 45) -> str:
        """Process a general query with the LLM"""
        try:
            response = execute_llm_query(prompt, self.model, self.use_ollama)
            return response if response else "Sorry, I couldn't process that request."
            
        except Exception as e:
            return f"AI analysis temporarily unavailable: {str(e)}"
    
    def analyze_data(self, df: pd.DataFrame, analysis_type: str = "overview") -> str:
        """Analyze a DataFrame and provide insights"""
        try:
            # Get column insights
            from scrubpy.column_insights import get_column_insights
            insights = get_column_insights(df)
            
            # Format data summary
            summary = {
                "shape": df.shape,
                "columns": list(df.columns)[:10],  # Limit for prompt size
                "missing_values": df.isnull().sum().sum(),
                "duplicates": df.duplicated().sum(),
                "dtypes": dict(df.dtypes.value_counts())
            }
            
            if analysis_type == "overview":
                prompt = f"""
                Analyze this dataset and provide 3 key insights:
                Dataset: {summary['shape'][0]} rows, {summary['shape'][1]} columns
                Missing values: {summary['missing_values']}
                Duplicates: {summary['duplicates']}
                Data types: {summary['dtypes']}
                
                Provide insights in this format:
                1. **Data Structure**: [brief insight about size, columns]
                2. **Data Quality**: [insight about missing values, data types]
                3. **Recommendations**: [1-2 specific cleaning recommendations]
                
                Keep each insight to 1-2 sentences.
                """
            elif analysis_type == "cleaning":
                prompt = f"""
                Based on this dataset analysis, provide specific cleaning recommendations:
                Shape: {summary['shape']}
                Missing values: {summary['missing_values']}
                Duplicates: {summary['duplicates']}
                
                Provide 3 actionable cleaning steps:
                1. **[Action Type]**: [specific recommendation]
                2. **[Action Type]**: [specific recommendation]  
                3. **[Action Type]**: [specific recommendation]
                
                Focus on the most impactful cleaning operations.
                """
            else:
                prompt = f"Analyze this dataset: {summary}"
            
            return self.process_query(prompt)
            
        except Exception as e:
            return f"Data analysis temporarily unavailable: {str(e)}"


class LLMAssistant:
    """
    Interactive LLM Assistant for dataset cleaning and analysis.
    Provides a higher-level interface for working with the LLM utilities.
    """
    
    def __init__(
        self, 
        df: pd.DataFrame, 
        column_insights_data: Optional[Dict[str, Any]] = None,
        model: str = "mistral",
        use_ollama: bool = True
    ):
        self.df = df
        self.column_insights = ensure_column_insights(df, column_insights_data)
        self.model = model
        self.use_ollama = use_ollama
        self.history = []
        self.cached_responses = {}
    
    def ask(self, question: str, task: str = "general_advice") -> str:
        """Ask a question about the dataset"""
        # Format insights and get snapshot
        insights_summary = format_column_insights_for_prompt(self.column_insights)
        dataset_snapshot = sample_dataset_snapshot(self.df)
        
        # Build prompt
        prompt = build_llm_prompt(
            insights_summary=insights_summary,
            dataset_snapshot=dataset_snapshot,
            task=task,
            user_question=question
        )
        
        # Check cache first
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        if cache_key in self.cached_responses:
            response = self.cached_responses[cache_key]
        else:
            # Execute query
            response = execute_llm_query(
                prompt=prompt,
                model=self.model,
                use_ollama=self.use_ollama
            )
            # Cache the response
            self.cached_responses[cache_key] = response
        
        # Store in history
        self.history.append({
            "timestamp": time.time(),
            "question": question,
            "task": task,
            "response": response
        })
        
        return response
    
    def generate_code(self, description: str) -> List[Dict[str, str]]:
        """Generate code to solve a specific data cleaning problem"""
        response = self.ask(description, task="code_generation")
        return extract_code_from_llm_response(response)
    
    def execute_cleaning(self, description: str) -> Tuple[bool, Union[pd.DataFrame, None], str]:
        """Generate and execute code for a cleaning task"""
        code_blocks = self.generate_code(description)
        
        if not code_blocks:
            return False, None, "No valid code was generated"
            
        # Try to execute the first code block
        success, result_df, message = execute_generated_code(
            code=code_blocks[0]["code"],
            df=self.df
        )
        
        if success:
            # Update internal dataframe if successful
            self.df = result_df
            
        return success, result_df, message
    
    def get_cleaning_plan(self) -> str:
        """Get a comprehensive cleaning plan"""
        return generate_cleaning_plan(self.df, self.column_insights)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get interaction history"""
        return self.history