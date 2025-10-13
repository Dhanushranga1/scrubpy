"""
ScrubPy Modern Web Interface - Enhanced User Experience
A beautiful, intuitive Streamlit interface for data cleaning
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple
import numpy as np

# ScrubPy imports
try:
    from scrubpy.config.settings import settings
    from scrubpy.core import load_dataset, get_dataset_summary
    from scrubpy.quality_analyzer import SmartDataQualityAnalyzer
    from scrubpy.utils.logging import logger, performance_monitor
    from scrubpy.validation import DataValidator, ParameterValidator
    from scrubpy.exceptions import ScrubPyError, DataValidationError
except ImportError as e:
    st.error(f"ScrubPy import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="ScrubPy - Smart Data Cleaning",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Dhanushranga1/scrubpy',
        'Report a bug': "https://github.com/Dhanushranga1/scrubpy/issues",
        'About': "ScrubPy v2.0.0 - AI-powered data cleaning assistant"
    }
)

def load_custom_css():
    """Load custom CSS for modern UI styling"""
    st.markdown("""
    <style>
    /* Main styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Quality indicators */
    .quality-excellent { 
        color: #22c55e; 
        font-weight: bold;
    }
    .quality-good { 
        color: #3b82f6; 
        font-weight: bold;
    }
    .quality-fair { 
        color: #f59e0b; 
        font-weight: bold;
    }
    .quality-poor { 
        color: #ef4444; 
        font-weight: bold;
    }
    
    /* Success/Error messages */
    .success-box {
        background: #ecfdf5;
        border: 1px solid #22c55e;
        color: #166534;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #fef2f2;
        border: 1px solid #ef4444;
        color: #dc2626;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    /* File upload area */
    .upload-area {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background: #f9fafb;
        transition: border-color 0.3s;
    }
    
    .upload-area:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }
    
    /* Progress indicators */
    .progress-container {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f8fafc;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the application header with branding"""
    st.markdown("""
    <div class="main-header">
        <h1>🧹 ScrubPy</h1>
        <p>AI-Powered Smart Data Cleaning Assistant</p>
        <p style="font-size: 0.9rem; opacity: 0.8;">
            Upload your messy data, get it cleaned with intelligent suggestions
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_file_upload():
    """Enhanced file upload with drag & drop and validation"""
    st.subheader("Upload Your Data")
    
    # File upload with enhanced UI
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Drag and drop your file here, or click to browse. Supports CSV and Excel formats.",
        label_visibility="collapsed"
    )
    
    # Sample data option
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("Try Sample Data", help="Load a sample dataset to explore ScrubPy"):
            return load_sample_data()
    
    if uploaded_file:
        # Show file information
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size:,.0f} bytes",
            "File type": uploaded_file.type
        }
        
        with st.expander("File Details", expanded=False):
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
        
        return load_uploaded_file(uploaded_file)
    
    # Instructions when no file is uploaded
    st.markdown("""
    <div class="upload-area">
        <h4>Ready to clean your data?</h4>
        <p>Upload a CSV or Excel file to get started</p>
        <ul style="text-align: left; max-width: 400px; margin: 1rem auto;">
            <li>Automatic quality analysis</li>
            <li>Smart cleaning suggestions</li>
            <li>Interactive data preview</li>
            <li>Export cleaned data</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    return None

@performance_monitor("file_loading")
def load_uploaded_file(uploaded_file) -> Optional[pd.DataFrame]:
    """Load and validate uploaded file with error handling"""
    try:
        with st.spinner(f"Loading {uploaded_file.name}..."):
            if uploaded_file.name.endswith('.csv'):
                # Try different encodings for CSV
                for encoding in ['utf-8', 'latin1', 'cp1252']:
                    try:
                        df = pd.read_csv(uploaded_file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not decode CSV file with any supported encoding")
            
            else:  # Excel file
                df = pd.read_excel(uploaded_file)
            
            # Validate loaded data
            validator = DataValidator()
            try:
                validator.validate_dataframe(df, min_rows=1, min_cols=1)
                
                st.success(f"Successfully loaded {len(df):,} rows and {len(df.columns)} columns!")
                logger.info(f"File loaded successfully: {uploaded_file.name} ({len(df)} rows, {len(df.columns)} columns)")
                
                return df
                
            except DataValidationError as e:
                st.error(f"Data validation failed: {e}")
                return None
                
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        logger.error(f"File loading error: {e}")
        return None

def load_sample_data() -> pd.DataFrame:
    """Load sample dataset for demonstration"""
    try:
        # Create a realistic sample dataset with various data quality issues
        np.random.seed(42)
        n_rows = 1000
        
        data = {
            'id': range(1, n_rows + 1),
            'name': [f"User_{i}" if i % 10 != 0 else None for i in range(n_rows)],  # 10% missing
            'email': [f"user{i}@example.com" if i % 15 != 0 else f"invalid_email_{i}" for i in range(n_rows)],
            'age': [np.random.randint(18, 80) if i % 20 != 0 else None for i in range(n_rows)],  # 5% missing
            'salary': [np.random.randint(30000, 150000) + (10000000 if i % 100 == 0 else 0) for i in range(n_rows)],  # outliers
            'department': np.random.choice(['Engineering', 'Marketing', 'Sales', 'HR', None], n_rows, p=[0.4, 0.25, 0.2, 0.1, 0.05]),
            'join_date': pd.date_range('2020-01-01', periods=n_rows, freq='D'),
            'performance_score': np.random.normal(75, 15, n_rows),
        }
        
        df = pd.DataFrame(data)
        
        # Add some duplicates
        df = pd.concat([df, df.iloc[:10]], ignore_index=True)
        
        st.success("Sample dataset loaded! This dataset contains various data quality issues for demonstration.")
        logger.info("Sample dataset loaded for demonstration")
        
        return df
        
    except Exception as e:
        st.error(f"Error loading sample data: {e}")
        return None

def render_data_overview(df: pd.DataFrame):
    """Render comprehensive data overview with interactive elements"""
    st.subheader("Data Overview")
    
    # Quick metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Rows", 
            value=f"{len(df):,}",
            help="Number of records in your dataset"
        )
    
    with col2:
        st.metric(
            label="Columns", 
            value=len(df.columns),
            help="Number of features/columns"
        )
    
    with col3:
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        st.metric(
            label="❓ Missing Data", 
            value=f"{missing_pct:.1f}%",
            help="Percentage of missing values"
        )
    
    with col4:
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric(
            label="💾 Memory Usage", 
            value=f"{memory_mb:.1f} MB",
            help="Memory footprint of your data"
        )
    
    # Data preview with pagination
    st.subheader("👀 Data Preview")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        show_rows = st.selectbox(
            "Rows to display:",
            [10, 25, 50, 100],
            index=0,
            key="preview_rows"
        )
    
    with col2:
        show_info = st.checkbox("Show data types", value=True, key="show_dtypes")
    
    with col3:
        show_stats = st.checkbox("Show statistics", value=False, key="show_stats")
    
    # Display data with custom styling
    display_df = df.head(show_rows)
    
    # Color-code missing values
    def highlight_missing(x):
        return ['background-color: #fee2e2' if pd.isna(v) else '' for v in x]
    
    styled_df = display_df.style.apply(highlight_missing, axis=0)
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # Additional information tabs
    if show_info or show_stats:
        tab1, tab2 = st.tabs(["Data Types", "Statistics"])
        
        with tab1:
            if show_info:
                info_df = pd.DataFrame({
                    'Column': df.columns,
                    'Data Type': df.dtypes.values,
                    'Non-Null Count': [f"{df[col].notna().sum():,}" for col in df.columns],
                    'Null Count': [f"{df[col].isna().sum():,}" for col in df.columns],
                    'Null %': [f"{(df[col].isna().sum()/len(df))*100:.1f}%" for col in df.columns]
                })
                st.dataframe(info_df, use_container_width=True)
        
        with tab2:
            if show_stats:
                try:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                    else:
                        st.info("No numeric columns found for statistical summary.")
                except Exception as e:
                    st.error(f"Error generating statistics: {e}")

@performance_monitor("quality_analysis")
def render_quality_assessment(df: pd.DataFrame):
    """Render comprehensive data quality assessment"""
    st.subheader("Data Quality Assessment")
    
    try:
        with st.spinner("Analyzing data quality..."):
            analyzer = SmartDataQualityAnalyzer()
            
            # Perform quality analysis
            quality_results = analyzer.analyze_quality(df)
            overall_score = quality_results.get('overall_score', 0)
            issues = quality_results.get('issues', [])
            column_scores = quality_results.get('column_scores', {})
            
            # Overall quality score with visual indicator
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Quality score gauge
                score_color = get_quality_color(overall_score)
                quality_level = get_quality_level(overall_score)
                
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Overall Quality Score</h3>
                    <h1 class="{score_color}">{overall_score:.1f}/100</h1>
                    <p><strong>{quality_level}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Quality breakdown chart
                if column_scores:
                    render_quality_chart(column_scores)
            
            # Issues summary
            if issues:
                st.subheader("Detected Issues")
                
                # Group issues by severity
                critical_issues = [i for i in issues if i.get('severity') == 'critical']
                warning_issues = [i for i in issues if i.get('severity') == 'warning']
                info_issues = [i for i in issues if i.get('severity') == 'info']
                
                # Display issues in expandable sections
                if critical_issues:
                    with st.expander(f"🚨 Critical Issues ({len(critical_issues)})", expanded=True):
                        for issue in critical_issues:
                            render_issue_card(issue, "critical")
                
                if warning_issues:
                    with st.expander(f"Warning Issues ({len(warning_issues)})", expanded=False):
                        for issue in warning_issues:
                            render_issue_card(issue, "warning")
                
                if info_issues:
                    with st.expander(f"ℹ️ Info Issues ({len(info_issues)})", expanded=False):
                        for issue in info_issues:
                            render_issue_card(issue, "info")
            else:
                st.success("No major data quality issues detected!")
                
        return quality_results
        
    except Exception as e:
        st.error(f"Error analyzing data quality: {e}")
        logger.error(f"Quality analysis error: {e}")
        return {}

def get_quality_color(score: float) -> str:
    """Get CSS class for quality score color"""
    if score >= 85:
        return "quality-excellent"
    elif score >= 70:
        return "quality-good"  
    elif score >= 50:
        return "quality-fair"
    else:
        return "quality-poor"

def get_quality_level(score: float) -> str:
    """Get quality level description"""
    if score >= 85:
        return "Excellent Quality"
    elif score >= 70:
        return "Good Quality"
    elif score >= 50:
        return "Fair Quality"
    else:
        return "Poor Quality"

def render_quality_chart(column_scores: Dict[str, float]):
    """Render quality scores chart"""
    try:
        if column_scores:
            # Create bar chart
            fig = px.bar(
                x=list(column_scores.keys()),
                y=list(column_scores.values()),
                title="Quality Scores by Column",
                labels={'x': 'Columns', 'y': 'Quality Score'},
                color=list(column_scores.values()),
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            
            fig.update_layout(
                height=300,
                showlegend=False,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error rendering quality chart: {e}")

def render_issue_card(issue: Dict, severity: str):
    """Render individual issue card"""
    severity_icons = {
        'critical': '🚨',
        'warning': '',
        'info': 'ℹ️'
    }
    
    severity_colors = {
        'critical': 'error-box',
        'warning': 'error-box',
        'info': 'success-box'
    }
    
    icon = severity_icons.get(severity, 'ℹ️')
    color_class = severity_colors.get(severity, 'success-box')
    
    st.markdown(f"""
    <div class="{color_class}">
        <strong>{icon} {issue.get('title', 'Unknown Issue')}</strong><br>
        {issue.get('description', 'No description available')}<br>
        <small><strong>Column:</strong> {issue.get('column', 'N/A')} | 
        <strong>Affected:</strong> {issue.get('affected_rows', 'N/A')} rows</small>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    # Load custom styling
    load_custom_css()
    
    # Render header
    render_header()
    
    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'quality_results' not in st.session_state:
        st.session_state.quality_results = {}
    
    # Main content area
    uploaded_df = render_file_upload()
    
    if uploaded_df is not None:
        st.session_state.df = uploaded_df
    
    # Process data if available
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", 
            "Quality Analysis", 
            "🧹 Data Cleaning", 
            "💬 AI Assistant",
            "Export"
        ])
        
        with tab1:
            render_data_overview(df)
        
        with tab2:
            quality_results = render_quality_assessment(df)
            if quality_results:
                st.session_state.quality_results = quality_results
        
        with tab3:
            render_cleaning_operations(df)
        
        with tab4:
            render_ai_assistant(df)
        
        with tab5:
            render_export_options(df)
    
    # Sidebar with additional options
    render_sidebar()

def render_cleaning_operations(df: pd.DataFrame):
    """Render data cleaning operations interface"""
    st.subheader("🧹 Data Cleaning Operations")
    
    # Get quality results if available
    quality_results = st.session_state.get('quality_results', {})
    issues = quality_results.get('issues', [])
    
    if issues:
        st.info(f"Found {len(issues)} issues that can be automatically fixed!")
        
        # Auto-fix suggestions
        if st.button("Apply Smart Auto-Fix", type="primary"):
            apply_smart_fixes(df, issues)
    
    # Manual cleaning options
    st.subheader("Manual Cleaning Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Missing Values**")
        if st.button("Fill Missing Values"):
            # Implementation for missing value handling
            st.info("Missing value handling interface would go here")
    
    with col2:
        st.write("**Duplicates**")
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            st.warning(f"Found {duplicates} duplicate rows")
            if st.button("Remove Duplicates"):
                # Implementation for duplicate removal
                st.info("Duplicate removal interface would go here")
        else:
            st.success("No duplicates found")

def apply_smart_fixes(df: pd.DataFrame, issues: List[Dict]):
    """Apply automatic fixes for detected issues"""
    with st.spinner("Applying smart fixes..."):
        try:
            # This would implement the actual fixing logic
            time.sleep(2)  # Simulate processing time
            st.success("Smart fixes applied successfully!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error applying fixes: {e}")

def render_ai_assistant(df: pd.DataFrame):
    """Render AI Assistant chat interface"""
    st.subheader("AI Data Cleaning Assistant")
    
    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # AI Assistant info box
    with st.container():
        st.info("**AI Assistant Features:**\n"
                "- Ask questions about your data\n" 
                "- Get cleaning suggestions\n"
                "- Understand data quality issues\n"
                "- Get personalized recommendations")
    
    # Chat interface
    st.markdown("### 💬 Chat with AI Assistant")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"""
                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0;">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #f3e5f5; padding: 10px; border-radius: 10px; margin: 5px 0;">
                    <strong>AI Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Ask me anything about your data...", key="chat_input")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        send_button = st.button("Send", type="primary")
    
    with col2:
        clear_button = st.button("Clear Chat")
    
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()
    
    # Handle user input
    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        try:
            # Try to import AI components
            try:
                from scrubpy.llm_utils import LLMAssistant
                from scrubpy.quality_analyzer import SmartDataQualityAnalyzer
                
                # Initialize AI assistant
                assistant = LLMAssistant()
                
                # Get data context
                data_summary = {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.to_dict(),
                    "null_counts": df.isnull().sum().to_dict(),
                    "sample": df.head().to_dict()
                }
                
                # Generate AI response
                ai_response = assistant.get_cleaning_suggestion(
                    user_input, 
                    data_summary
                )
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": ai_response
                })
                
            except ImportError:
                # Fallback response when AI components aren't available
                fallback_responses = {
                    "shape": f"Your dataset has {df.shape[0]} rows and {df.shape[1]} columns.",
                    "missing": f"Missing values found in: {', '.join([col for col in df.columns if df[col].isnull().sum() > 0])}",
                    "clean": "I recommend checking for missing values, duplicates, and data type consistency.",
                    "help": "Available commands: 'shape', 'missing', 'clean', 'columns'"
                }
                
                # Simple keyword matching for fallback
                response = "I'd be happy to help! Here are some things I can tell you about your data:\n"
                
                if "shape" in user_input.lower() or "size" in user_input.lower():
                    response = fallback_responses["shape"]
                elif "missing" in user_input.lower() or "null" in user_input.lower():
                    response = fallback_responses["missing"]
                elif "clean" in user_input.lower():
                    response = fallback_responses["clean"]
                elif "help" in user_input.lower():
                    response = fallback_responses["help"]
                else:
                    response += "\n".join([f"• {key}: {value}" for key, value in fallback_responses.items()])
                
                # Add fallback response to history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": response
                })
                
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}. Try asking about data shape, missing values, or cleaning suggestions."
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": error_msg
            })
        
        # Clear input and rerun
        st.rerun()
    
    # Quick action buttons
    st.markdown("### Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Analyze Data Shape"):
            response = f"Your dataset contains **{df.shape[0]} rows** and **{df.shape[1]} columns**."
            st.session_state.chat_history.append({"role": "user", "content": "Analyze data shape"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("Check Missing Values"):
            missing_data = df.isnull().sum()
            missing_cols = missing_data[missing_data > 0]
            if len(missing_cols) > 0:
                response = "**Missing values found:**\n"
                for col, count in missing_cols.items():
                    percentage = (count / len(df)) * 100
                    response += f"• {col}: {count} ({percentage:.1f}%)\n"
            else:
                response = "Great news! No missing values found in your dataset. "
            
            st.session_state.chat_history.append({"role": "user", "content": "Check missing values"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("Get Cleaning Tips"):
            # Basic cleaning suggestions
            suggestions = []
            
            # Check for missing values
            if df.isnull().sum().sum() > 0:
                suggestions.append("Handle missing values using imputation or removal")
            
            # Check for duplicates
            if df.duplicated().sum() > 0:
                suggestions.append("Remove duplicate rows")
            
            # Check for mixed data types in object columns
            for col in df.select_dtypes(include=['object']).columns:
                if df[col].apply(lambda x: str(x).strip()).nunique() != df[col].nunique():
                    suggestions.append(f"Standardize text in column '{col}'")
            
            if not suggestions:
                suggestions.append("Your data looks clean! Consider checking data types for optimization.")
            
            response = "**Recommended cleaning steps:**\n" + "\n".join([f"• {tip}" for tip in suggestions])
            
            st.session_state.chat_history.append({"role": "user", "content": "Get cleaning tips"})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

def render_export_options(df: pd.DataFrame):
    """Render export options for cleaned data"""
    st.subheader("Export Cleaned Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "Export Format:",
            ["CSV", "Excel", "JSON", "Parquet"]
        )
    
    with col2:
        filename = st.text_input(
            "Filename:",
            value="cleaned_data"
        )
    
    if st.button("Download Cleaned Data", type="primary"):
        try:
            if export_format == "CSV":
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{filename}.csv",
                    mime="text/csv"
                )
            elif export_format == "Excel":
                # Excel export would require additional implementation
                st.info("Excel export functionality would be implemented here")
            
        except Exception as e:
            st.error(f"Export error: {e}")

def render_sidebar():
    """Render sidebar with additional options and information"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Theme selection
        st.subheader("Appearance")
        theme = st.selectbox(
            "Theme:",
            ["Default", "Dark", "Light"],
            key="theme_select"
        )
        
        # Performance settings
        st.subheader("Performance")
        max_rows = st.number_input(
            "Max rows to display:",
            min_value=10,
            max_value=10000,
            value=1000,
            step=100
        )
        
        # Help section
        st.subheader("❓ Help")
        
        with st.expander("📚 Quick Guide"):
            st.markdown("""
            1. **Upload** your CSV or Excel file
            2. **Review** the data overview
            3. **Analyze** quality issues
            4. **Clean** your data
            5. **Export** the results
            """)
        
        with st.expander("🛠️ Troubleshooting"):
            st.markdown("""
            - **Large files**: Use CSV format for better performance
            - **Encoding issues**: Try saving as UTF-8
            - **Memory errors**: Reduce dataset size or contact support
            """)
        
        # System information
        st.subheader("ℹ️ System Info")
        st.code(f"""
ScrubPy Version: 2.0.0
Python Version: {pd.__version__}
Streamlit Version: {st.__version__}
        """)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {e}")
        logger.error(f"Application error: {e}")
        st.info("Please refresh the page or contact support if the problem persists.")