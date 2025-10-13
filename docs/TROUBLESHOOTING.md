# ScrubPy Troubleshooting Guide

> **Quick solutions for common ScrubPy issues and problems**

This guide helps you resolve common issues when using ScrubPy's web, CLI, and chat interfaces. Most problems have simple solutions!

## 🚨 **Emergency Quick Fixes**

### **Nothing Works / Won't Start**
```bash
# 1. Check Python version (must be 3.8+)
python --version

# 2. Reinstall dependencies  
pip install -r requirements.txt

# 3. Try minimal startup
python -c "import scrubpy; print('ScrubPy imports successfully')"

# 4. Reset configuration
rm -rf ~/.scrubpy/ && python main.py
```

### **"Module not found" Errors**
```bash
# Install ScrubPy in development mode
pip install -e .

# Or install missing packages
pip install pandas streamlit typer rich ollama
```

### **Web Interface Won't Open**
```bash
# Try different port
python main.py --port 8502

# Check what's using port 8501
lsof -i :8501  # On macOS/Linux
netstat -ano | findstr :8501  # On Windows
```

---

## 🌐 **Web Interface Issues**

### **Issue: Browser doesn't open automatically**
**Symptoms:** Command runs but no browser window appears

**Solutions:**
```bash
# 1. Open manually
# Look for: "Local URL: http://localhost:8501"
# Copy URL to browser

# 2. Check if port is blocked
python main.py --port 8080  # Try different port

# 3. Disable auto-open
python main.py --no-browser
```

**Prevention:** Configure in `~/.scrubpy/config.yaml`:
```yaml
web:
  auto_open: false  # Disable automatic browser opening
  port: 8080        # Use different default port
```

### **Issue: "Address already in use" error**
**Symptoms:** `OSError: [Errno 48] Address already in use`

**Solutions:**
```bash
# 1. Use different port
python main.py --port 8502

# 2. Kill process using port 8501
# On macOS/Linux:
lsof -ti:8501 | xargs kill -9

# On Windows:
netstat -ano | findstr :8501
taskkill /PID <PID_NUMBER> /F

# 3. Restart your computer (last resort)
```

### **Issue: File upload fails**
**Symptoms:** "File too large" or upload hangs

**Solutions:**
1. **Check file size** (default limit: 100MB)
```yaml
# In config.yaml
web:
  upload_max_size_mb: 500  # Increase limit
```

2. **Try different file format**
```bash
# If Excel fails, convert to CSV first
python -c "import pandas as pd; pd.read_excel('file.xlsx').to_csv('file.csv')"
```

3. **Check file encoding**
```python
# Test file readability
import pandas as pd
df = pd.read_csv('your_file.csv', encoding='utf-8')  # Try utf-8
df = pd.read_csv('your_file.csv', encoding='latin-1')  # Try latin-1
```

### **Issue: Web app runs but shows errors**
**Symptoms:** Interface loads but crashes when processing data

**Debug steps:**
```bash
# 1. Check Python console for detailed errors
python main.py  # Look at terminal output

# 2. Enable debug mode
STREAMLIT_LOGGER_LEVEL=debug python main.py

# 3. Test with sample data
python main.py sample_data.csv
```

---

## **CLI Interface Issues**

### **Issue: CLI commands not recognized**
**Symptoms:** `scrubpy: command not found` or similar

**Solutions:**
```bash
# 1. Use Python module directly
python -m scrubpy.cli --help

# 2. Install in development mode
pip install -e .

# 3. Check if script installed correctly
which scrubpy  # Should show path to script

# 4. Add to PATH (if needed)
export PATH=$PATH:~/.local/bin
```

### **Issue: CLI crashes on large files**
**Symptoms:** Memory errors or "Killed" message

**Solutions:**
1. **Increase chunk size and memory limits**
```yaml
# In config.yaml
performance:
  chunk_size: 5000      # Smaller chunks
  memory_limit_gb: 2    # Lower memory limit
  parallel_processing: false  # Disable parallelism
```

2. **Process file in parts**
```bash
# Split large file first
python -c "
import pandas as pd
df = pd.read_csv('large_file.csv')
for i, chunk in enumerate(pd.read_csv('large_file.csv', chunksize=10000)):
    chunk.to_csv(f'chunk_{i}.csv', index=False)
"
```

### **Issue: Rich formatting not working**
**Symptoms:** No colors, broken progress bars

**Solutions:**
```bash
# 1. Check terminal support
echo $TERM  # Should not be 'dumb'

# 2. Force color output
export FORCE_COLOR=1
python main.py --cli

# 3. Disable colors if needed
python main.py --cli --no-color
```

### **Issue: Interactive prompts don't work**
**Symptoms:** CLI doesn't wait for input or skips prompts

**Solutions:**
```bash
# 1. Check if running in proper terminal
# Avoid: shell scripts, cron jobs, IDE terminals

# 2. Force interactive mode
python main.py --cli --interactive

# 3. Use non-interactive mode for scripts
python main.py --cli --batch --input file.csv --output cleaned.csv
```

---

## **AI/Chat Interface Issues**

### **Issue: "LLM service not available"**
**Symptoms:** Chat mode fails to start or respond

**Solutions:**
1. **Check Ollama installation (default provider)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull required model
ollama pull mistral

# Test connection
curl http://localhost:11434/api/version
```

2. **Configure different provider**
```yaml
# In config.yaml - use OpenAI instead
llm:
  provider: "openai"
  api_key: "your-openai-api-key"
  model: "gpt-3.5-turbo"
```

3. **Test LLM connectivity**
```bash
python -c "
from scrubpy.llm_utils import test_llm_connection
print(test_llm_connection())
"
```

### **Issue: Chat responses are slow or timeout**
**Symptoms:** Long waits, timeout errors

**Solutions:**
```yaml
# Increase timeout and reduce response length
llm:
  timeout: 60           # Increase from 30 seconds
  max_tokens: 1000      # Reduce from 2000
  temperature: 0.5      # Faster, less creative responses
```

### **Issue: Chat gives unhelpful responses**
**Symptoms:** Generic responses, doesn't understand data context

**Solutions:**
1. **Provide better context**
```bash
# Instead of: "Clean my data"
# Try: "I have a customer dataset with missing emails and duplicate records"
```

2. **Use specific column names**
```bash
# "What should I do with the 'customer_age' column that has negative values?"
```

3. **Check model configuration**
```yaml
llm:
  model: "mistral"      # Try different models
  temperature: 0.3      # Lower = more focused responses
```

---

## **Data Processing Issues**

### **Issue: "Memory Error" or system freeze**
**Symptoms:** Python crashes, system becomes unresponsive

**Solutions:**
1. **Reduce memory usage**
```yaml
performance:
  chunk_size: 1000           # Much smaller chunks
  memory_limit_gb: 1         # Conservative limit
  parallel_processing: false # Disable multiprocessing
```

2. **Sample large datasets first**
```python
# Test with subset of data
import pandas as pd
df = pd.read_csv('large_file.csv', nrows=1000)  # First 1000 rows only
```

3. **Use memory-efficient methods**
```python
# Instead of loading entire file:
# df = pd.read_csv('huge_file.csv')

# Use chunking:
for chunk in pd.read_csv('huge_file.csv', chunksize=5000):
    process_chunk(chunk)
```

### **Issue: Cleaning operations fail**
**Symptoms:** Operations complete but data isn't actually cleaned

**Debug steps:**
1. **Check data types**
```python
print(df.dtypes)  # Verify expected types
print(df.head())  # Check actual values
```

2. **Enable verbose logging**
```yaml
logging:
  level: "DEBUG"
  verbose_logging: true
```

3. **Test operations individually**
```bash
python -c "
from scrubpy.core import remove_duplicates
import pandas as pd
df = pd.read_csv('test.csv')
print(f'Before: {len(df)} rows')
cleaned = remove_duplicates(df)
print(f'After: {len(cleaned)} rows')
"
```

### **Issue: Wrong data types detected**
**Symptoms:** Numbers treated as text, dates as strings

**Solutions:**
1. **Manual type conversion**
```python
# Force correct types
df = pd.read_csv('file.csv', dtype={
    'customer_id': 'string',
    'amount': 'float64',
    'date': 'string'  # Convert manually later
})
```

2. **Configure type detection**
```yaml
dtypes:
  auto_convert: true
  date_formats: ["%Y-%m-%d", "%m/%d/%Y"]  # Add your format
  force_types:
    customer_id: "string"
    order_date: "datetime64[ns]"
```

---

## **Installation & Environment Issues**

### **Issue: Python version conflicts**
**Symptoms:** Import errors, syntax errors, compatibility warnings

**Solutions:**
```bash
# 1. Check Python version (need 3.8+)
python --version

# 2. Create virtual environment with correct Python
python3.9 -m venv scrubpy_env
source scrubpy_env/bin/activate  # Linux/Mac
scrubpy_env\Scripts\activate     # Windows

# 3. Install in clean environment
pip install --upgrade pip
pip install -r requirements.txt
```

### **Issue: Package version conflicts**
**Symptoms:** `VersionConflict`, dependency errors

**Solutions:**
```bash
# 1. Create fresh virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# 2. Install specific compatible versions
pip install pandas==1.5.3 streamlit==1.28.0

# 3. Use pip-tools for dependency management
pip install pip-tools
pip-compile requirements.in  # Creates requirements.txt
```

### **Issue: Import errors for specific modules**
**Symptoms:** `ModuleNotFoundError` for scikit-learn, scipy, etc.

**Solutions:**
```bash
# Install optional dependencies
pip install scikit-learn>=1.0.0
pip install scipy>=1.7.0

# Or install all optional features
pip install -e ".[advanced,ai]"
```

---

## 🐛 **Performance Issues**

### **Issue: Very slow processing**
**Symptoms:** Operations take much longer than expected

**Diagnosis:**
```python
# Profile your dataset
import pandas as pd
df = pd.read_csv('your_file.csv')
print(f"Dataset shape: {df.shape}")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
print(f"Data types:\n{df.dtypes}")
```

**Solutions:**
1. **Optimize data types**
```python
# Convert to more efficient types
df['category_col'] = df['category_col'].astype('category')
df['int_col'] = pd.to_numeric(df['int_col'], downcast='integer')
```

2. **Increase chunk size for large datasets**
```yaml
performance:
  chunk_size: 50000     # Larger chunks for big files
  parallel_processing: true
  max_workers: 4        # Use multiple cores
```

3. **Enable caching**
```yaml
performance:
  cache_enabled: true   # Cache repeated operations
```

### **Issue: High memory usage**
**Symptoms:** System slowdown, swap usage

**Solutions:**
```yaml
# Conservative memory settings
performance:
  chunk_size: 5000
  memory_limit_gb: 2
  parallel_processing: false

# Enable memory monitoring
logging:
  level: "DEBUG"  # Shows memory usage
```

---

## 🔍 **Debugging Tools & Commands**

### **General Debugging**
```bash
# 1. Enable maximum logging
export SCRUBPY_LOG_LEVEL=DEBUG
python main.py

# 2. Test installation
python -c "import scrubpy; print('Import works')"

# 3. Show configuration
python main.py --show-config

# 4. Validate sample data
python main.py --test sample_data.csv
```

### **Component Testing**
```bash
# Test core functionality
python -c "
from scrubpy.core import load_dataset, get_dataset_summary
df = load_dataset('sample_data.csv')
print(get_dataset_summary(df))
"

# Test quality analyzer
python -c "
from scrubpy.quality_analyzer import SmartDataQualityAnalyzer
import pandas as pd
df = pd.read_csv('sample_data.csv')
analyzer = SmartDataQualityAnalyzer(df)
print(f'Quality score: {analyzer.get_quality_score()[0]}')
"

# Test LLM connection
python -c "
from scrubpy.llm_utils import test_llm_connection
print(test_llm_connection())
"
```

### **Performance Profiling**
```bash
# Profile memory usage
pip install memory_profiler
python -m memory_profiler main.py your_data.csv

# Profile execution time
python -m cProfile -o profile_stats main.py your_data.csv
python -c "
import pstats
p = pstats.Stats('profile_stats')
p.sort_stats('tottime').print_stats(20)
"
```

---

## **Issue Reporting Checklist**

If none of these solutions work, please report the issue with:

### **Environment Information**
```bash
# Run this and include output in bug report
python -c "
import sys, platform, pandas, streamlit
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Pandas: {pandas.__version__}')
print(f'Streamlit: {streamlit.__version__}')
"

# Include ScrubPy configuration
cat ~/.scrubpy/config.yaml
```

### **Error Details**
- Full error message and stack trace
- Steps to reproduce the issue
- Sample data (anonymized) if possible
- Expected vs actual behavior

### **System Information**
- Operating system and version
- Python version
- Available RAM and CPU cores
- File size and format being processed

---

## 🆘 **Getting Help**

### **Self-Help Resources**
1. **[Configuration Guide](CONFIG.md)** - Detailed configuration options
2. **[API Reference](API_REFERENCE.md)** - Function documentation
3. **[Architecture Guide](ARCHITECTURE.md)** - How ScrubPy works

### **Community Support**
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: General questions and usage help
- **Documentation**: Check latest docs for updates

### **Quick Contact**
Found a critical bug? Create a GitHub issue with:
- "🚨 CRITICAL:" in the title
- Steps to reproduce
- Your environment details
- Sample data (if possible)

---

## **Prevention Tips**

### **Avoid Common Issues**
1. **Always use virtual environments**
2. **Keep dependencies updated regularly**  
3. **Test with small datasets first**
4. **Monitor memory usage with large files**
5. **Backup important data before cleaning**
6. **Keep configuration files in version control**

### **Best Practices**
- Start with default configuration
- Make incremental changes
- Test after each configuration change
- Keep log files for debugging
- Document custom configurations

**Remember: Most issues have simple solutions!** 🔧✨

---

**📞 Still stuck?** Create a GitHub issue with the information above, and the community will help! 🤝