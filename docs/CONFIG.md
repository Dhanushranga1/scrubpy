# ⚙️ ScrubPy Configuration Reference

> **Complete guide to configuring ScrubPy for your specific needs**

ScrubPy uses a flexible configuration system that allows you to customize behavior, performance settings, AI integration, and interface preferences.

## **Quick Configuration**

### **Default Setup** (Works out of the box)
```bash
# First run creates default configuration
python main.py

# Configuration file created at:
# ~/.scrubpy/config.yaml
```

### **Custom Configuration**
```bash
# Set custom config location
export SCRUBPY_CONFIG_PATH="/path/to/your/config.yaml"

# Or pass config directly
python main.py --config /path/to/config.yaml
```

---

## 📁 **Configuration File Structure**

### **Default Configuration** (`~/.scrubpy/config.yaml`)
```yaml
# ScrubPy Configuration
# Generated automatically on first run

# AI/LLM Integration
llm:
  provider: "ollama"           # ollama, openai, anthropic, local
  model: "mistral"             # Model name (provider-specific)
  base_url: "http://localhost:11434"  # For local providers
  api_key: null                # Set for cloud providers
  timeout: 30                  # Request timeout in seconds
  max_retries: 3               # Maximum retry attempts
  temperature: 0.7             # Response creativity (0.0-1.0)
  max_tokens: 2000             # Maximum response length

# Performance Settings
performance:
  chunk_size: 10000            # Rows per processing chunk
  memory_limit_gb: 4           # Memory limit for large datasets
  cache_enabled: true          # Enable caching for repeated operations
  parallel_processing: true    # Use multiple cores when possible
  max_workers: null            # CPU cores to use (null = auto-detect)
  
# User Interface Settings
ui:
  theme: "light"               # light, dark, auto
  show_advanced_options: false # Show advanced settings by default
  auto_save: true              # Auto-save cleaned data
  default_output_format: "csv" # csv, xlsx, json, parquet
  progress_bars: true          # Show progress indicators
  
# Web Interface Specific
web:
  port: 8501                   # Streamlit port
  host: "localhost"            # Host to bind to
  auto_open: true              # Open browser automatically
  upload_max_size_mb: 100      # Maximum file upload size
  
# CLI Interface Specific  
cli:
  colorful_output: true        # Use colors in terminal
  interactive_prompts: true    # Interactive mode by default
  verbose_logging: false       # Detailed operation logging
  
# Chat Interface Specific
chat:
  conversation_history: 10     # Number of messages to remember
  auto_suggest: true           # Suggest next actions
  explain_operations: true     # Explain what operations do
  
# Logging Configuration
logging:
  level: "INFO"                # DEBUG, INFO, WARNING, ERROR
  file_logging: true           # Write logs to file
  log_dir: "~/.scrubpy/logs"   # Log directory
  max_file_size_mb: 10         # Rotate logs at this size
  backup_count: 5              # Number of backup log files
  
# Data Quality Settings
quality:
  missing_threshold: 0.1       # Flag columns with >10% missing values
  outlier_method: "iqr"        # iqr, zscore, isolation_forest
  duplicate_threshold: 0.05    # Flag if >5% duplicates
  quality_score_weights:       # Quality scoring weights
    completeness: 0.3
    validity: 0.25
    consistency: 0.2
    uniqueness: 0.15
    accuracy: 0.1

# Cleaning Operation Defaults
cleaning:
  missing_data:
    default_strategy: "auto"   # auto, mean, median, mode, drop, forward_fill
    string_fill_value: "Unknown"
    preserve_patterns: true    # Don't impute obvious patterns
    
  outliers:
    default_action: "flag"     # flag, remove, cap, transform
    z_threshold: 3             # Standard deviations for z-score method
    iqr_multiplier: 1.5        # IQR multiplier for outlier detection
    
  duplicates:
    keep: "first"              # first, last, none
    consider_all_columns: true # Use all columns for duplicate detection
    
  text_cleaning:
    standardize_case: true     # Convert to standard case
    remove_extra_spaces: true  # Remove multiple spaces
    fix_encodings: true        # Fix common encoding issues
    
# Data Type Detection
dtypes:
  auto_convert: true           # Automatically convert data types
  date_formats: [             # Date formats to try
    "%Y-%m-%d",
    "%d/%m/%Y", 
    "%m/%d/%Y",
    "%Y-%m-%d %H:%M:%S"
  ]
  boolean_values:             # Values to treat as boolean
    true_values: ["true", "yes", "y", "1", "on"]
    false_values: ["false", "no", "n", "0", "off"]

# Export Settings
export:
  include_metadata: true       # Include cleaning metadata
  compression: "infer"         # auto, gzip, bz2, xz, none
  preserve_dtypes: true        # Maintain data types in export
  add_timestamp: true          # Add timestamp to filename
  
# Advanced Features
advanced:
  enable_ml_imputation: false  # Use ML models for imputation
  enable_anomaly_detection: false  # Advanced anomaly detection
  enable_profiling: true       # Generate data profiling reports
  cache_ml_models: true        # Cache trained models
```

---

## 🎛️ **Configuration Sections Explained**

### **LLM Configuration**
Controls AI assistant behavior and connectivity:

```yaml
llm:
  provider: "ollama"    # Choose your AI provider
  model: "mistral"      # Model for conversations
  base_url: "http://localhost:11434"  # Local AI server
  temperature: 0.7      # Higher = more creative responses
```

**Supported Providers:**
- `ollama` - Local Ollama server (recommended for privacy)
- `openai` - OpenAI GPT models (requires API key)
- `anthropic` - Claude models (requires API key) 
- `local` - Local transformers models

**Example Provider Configurations:**
```yaml
# OpenAI Configuration
llm:
  provider: "openai"
  model: "gpt-4"
  api_key: "sk-your-api-key-here"
  
# Anthropic Configuration  
llm:
  provider: "anthropic"
  model: "claude-3-sonnet-20240229"
  api_key: "your-anthropic-key"
```

### **Performance Configuration**
Optimize ScrubPy for your hardware and datasets:

```yaml
performance:
  chunk_size: 10000      # Smaller = less memory, slower processing
  memory_limit_gb: 4     # Prevents memory overflow
  parallel_processing: true  # Use multiple CPU cores
```

**Memory Guidelines:**
- **Small datasets** (<1MB): `chunk_size: 1000`, `memory_limit_gb: 1`
- **Medium datasets** (1MB-100MB): `chunk_size: 10000`, `memory_limit_gb: 4`
- **Large datasets** (>100MB): `chunk_size: 50000`, `memory_limit_gb: 8+`

### **🎨 UI Configuration**  
Customize interface appearance and behavior:

```yaml
ui:
  theme: "dark"          # Switch to dark mode
  show_advanced_options: true  # Show all options by default
  auto_save: false       # Disable automatic saving
```

**Theme Options:**
- `light` - Light mode (default)
- `dark` - Dark mode  
- `auto` - Follow system preference

### **Quality Configuration**
Control data quality assessment:

```yaml
quality:
  missing_threshold: 0.2     # Flag columns with >20% missing
  outlier_method: "zscore"   # Use z-score instead of IQR
  quality_score_weights:     # Customize quality scoring
    completeness: 0.4        # Emphasize completeness more
    validity: 0.3
    consistency: 0.15
    uniqueness: 0.1
    accuracy: 0.05
```

---

## **Environment Variables**

Override configuration with environment variables:

```bash
# Configuration file location
export SCRUBPY_CONFIG_PATH="/custom/path/config.yaml"

# AI Provider settings
export SCRUBPY_LLM_PROVIDER="openai"
export SCRUBPY_LLM_API_KEY="your-api-key"
export SCRUBPY_LLM_MODEL="gpt-4"

# Performance settings
export SCRUBPY_CHUNK_SIZE="20000"
export SCRUBPY_MEMORY_LIMIT="8"

# Interface settings
export SCRUBPY_WEB_PORT="8080"
export SCRUBPY_THEME="dark"

# Logging
export SCRUBPY_LOG_LEVEL="DEBUG"
```

---

## **Use Case Configurations**

### **🏢 Enterprise Setup** (High performance, security-focused)
```yaml
# Enterprise configuration
llm:
  provider: "local"       # Keep data on-premises
  model: "local-model"
  
performance:
  chunk_size: 50000      # Process larger chunks
  memory_limit_gb: 16    # Use more memory
  parallel_processing: true
  max_workers: 8         # Use 8 CPU cores
  
logging:
  level: "INFO"          # Moderate logging
  file_logging: true
  
security:
  encrypt_cache: true    # Encrypt cached data
  audit_logging: true    # Log all operations
```

### **🎓 Educational Setup** (Learning-focused, detailed feedback)
```yaml
# Educational configuration  
ui:
  show_advanced_options: true    # Show all options
  progress_bars: true           # Visual feedback
  
chat:
  explain_operations: true      # Explain everything
  auto_suggest: true           # Suggest next steps
  conversation_history: 20     # Remember more context
  
logging:
  level: "DEBUG"               # Detailed logging
  verbose_logging: true        # Extra details
```

### **Developer Setup** (Debugging and testing)
```yaml
# Developer configuration
performance:
  cache_enabled: false    # Disable caching for testing
  
logging:
  level: "DEBUG"          # Maximum detail
  file_logging: true
  
advanced:
  enable_profiling: true  # Performance profiling
  
cli:
  verbose_logging: true   # See all operations
```

### **☁️ Cloud/Remote Setup** (Optimized for cloud deployment)
```yaml
# Cloud deployment configuration
web:
  host: "0.0.0.0"        # Accept connections from anywhere
  port: 8080             # Standard cloud port
  
performance:
  memory_limit_gb: 2     # Conservative memory usage
  chunk_size: 5000       # Smaller chunks for stability
  
logging:
  level: "WARNING"       # Minimal logging
  file_logging: false    # Use container logging
```

---

## 🛠️ **Advanced Configuration**

### **Custom Data Type Detection**
```yaml
dtypes:
  auto_convert: true
  custom_patterns:
    phone: "^\\+?1?\\d{9,15}$"    # Phone number pattern
    email: "^[^@]+@[^@]+\\.[^@]+$" # Email pattern
    zip_code: "^\\d{5}(-\\d{4})?$" # US ZIP code
  
  force_types:                     # Force specific columns to types
    "customer_id": "string"
    "order_date": "datetime64[ns]"
    "is_active": "boolean"
```

### **Custom Cleaning Rules**
```yaml
cleaning:
  custom_rules:
    - name: "standardize_phone"
      pattern: "\\(?(\\d{3})\\)?[-. ]?(\\d{3})[-. ]?(\\d{4})"
      replacement: "(\\1) \\2-\\3"
      columns: ["phone", "contact_number"]
      
    - name: "clean_currency"  
      pattern: "[^\\d.]"
      replacement: ""
      columns: ["price", "cost", "amount"]
```

### **ML Model Configuration**
```yaml
advanced:
  enable_ml_imputation: true
  ml_models:
    imputation:
      algorithm: "random_forest"   # random_forest, knn, linear
      n_estimators: 100
      random_state: 42
      
    outlier_detection:
      algorithm: "isolation_forest"
      contamination: 0.1
      
  model_cache:
    enabled: true
    max_models: 10        # Keep last 10 trained models
    cache_dir: "~/.scrubpy/models"
```

---

## 🔒 **Security Configuration**

### **Data Privacy Settings**
```yaml
security:
  encrypt_cache: true           # Encrypt cached data
  audit_logging: true           # Log all data access
  anonymize_logs: true          # Remove sensitive data from logs
  secure_temp_files: true       # Encrypt temporary files
  
privacy:
  disable_telemetry: true       # No usage analytics
  local_processing_only: true   # Never send data externally
  memory_only_mode: false       # Keep data in memory only
```

### **Access Control**
```yaml
access:
  require_auth: false           # Enable authentication
  max_file_size_mb: 100        # Limit upload size
  allowed_file_types: ["csv", "xlsx", "json"]
  blocked_columns: ["ssn", "password", "secret"]  # Never process these
```

---

## 📝 **Configuration Management**

### **Multiple Configurations**
```bash
# Different configs for different projects
python main.py --config configs/project_a.yaml
python main.py --config configs/project_b.yaml

# Environment-specific configs
python main.py --config configs/development.yaml
python main.py --config configs/production.yaml
```

### **Configuration Validation**
```bash
# Validate configuration file
python -c "from scrubpy.config import validate_config; validate_config('config.yaml')"

# Test configuration with sample data
python main.py --config config.yaml --test-config sample_data.csv
```

### **Configuration Templates**
ScrubPy includes preset configurations:

```bash
# Copy template to customize
cp scrubpy/configs/enterprise.yaml ~/.scrubpy/config.yaml
cp scrubpy/configs/educational.yaml ~/.scrubpy/config.yaml
cp scrubpy/configs/developer.yaml ~/.scrubpy/config.yaml
```

---

## **Troubleshooting Configuration**

### **Common Configuration Issues**

#### **Issue: LLM not working**
```yaml
# Check LLM configuration
llm:
  provider: "ollama"
  base_url: "http://localhost:11434"  # Make sure Ollama is running
  timeout: 60                         # Increase timeout
```

#### **Issue: Out of memory errors**
```yaml
# Reduce memory usage
performance:
  chunk_size: 1000      # Smaller chunks
  memory_limit_gb: 2    # Lower limit
  parallel_processing: false  # Disable parallelism
```

#### **Issue: Slow processing**
```yaml
# Optimize for speed
performance:
  chunk_size: 50000     # Larger chunks
  parallel_processing: true
  cache_enabled: true
  max_workers: null     # Use all CPU cores
```

#### **Issue: Web interface not accessible**
```yaml
# Web server configuration
web:
  host: "0.0.0.0"      # Accept external connections
  port: 8501           # Check port isn't in use
  auto_open: false     # Disable auto-browser opening
```

### **Configuration Debugging**
```bash
# Show current configuration
python main.py --show-config

# Validate configuration
python main.py --validate-config

# Test with minimal configuration
python main.py --minimal-config

# Reset to defaults
python main.py --reset-config
```

---

## 📚 **Configuration Examples**

### **Example 1: Data Science Team**
```yaml
# data_science_team.yaml
llm:
  provider: "openai" 
  model: "gpt-4"
  api_key: "${OPENAI_API_KEY}"

performance:
  chunk_size: 20000
  memory_limit_gb: 8
  parallel_processing: true

ui:
  show_advanced_options: true
  theme: "dark"

advanced:
  enable_ml_imputation: true
  enable_profiling: true
```

### **Example 2: Production Pipeline**
```yaml
# production.yaml
llm:
  provider: "local"    # No external API calls

performance:
  chunk_size: 10000
  memory_limit_gb: 4
  cache_enabled: true

logging:
  level: "WARNING"     # Minimal logging
  file_logging: true

export:
  add_timestamp: true
  include_metadata: true
```

### **Example 3: Educational Environment**  
```yaml
# classroom.yaml
ui:
  show_advanced_options: true
  progress_bars: true

chat:
  explain_operations: true
  auto_suggest: true
  conversation_history: 15

logging:
  level: "INFO"
  verbose_logging: true

quality:
  missing_threshold: 0.05  # More sensitive to issues
```

---

## **Next Steps**

1. **Start with defaults**: Let ScrubPy create the initial config
2. **Identify needs**: Consider your hardware, data size, and use case
3. **Customize gradually**: Change one section at a time
4. **Test thoroughly**: Validate changes with sample data
5. **Document changes**: Keep notes on what works for your team

### **Related Documentation**
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
- **[Performance Guide](PERFORMANCE.md)** - Optimization strategies
- **[Security Guide](SECURITY.md)** - Data protection practices
- **[Developer Onboarding](DEVELOPER_ONBOARDING.md)** - Development setup

**Happy configuring!** ⚙️✨