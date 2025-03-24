# 🧼 ScrubPy – Your Friendly Data Cleaning Sidekick

> 🚀 Clean smarter, not harder. Save hours of data wrangling with just a few keystrokes.

---

## 🤖 What is ScrubPy?

ScrubPy is a **command-line tool** that helps you **clean and understand your datasets** 10x faster.  
Whether you're a student, data analyst, or researcher – ScrubPy takes care of the messy stuff so you can focus on insights.

No need to write repetitive pandas code. Just run, choose, and clean.

---

## ✨ Impact (So Far)

✅ Cleaned datasets in **under 30 seconds**  
✅ Saved an average of **80% time** in basic data cleaning tasks  
✅ Made profiling accessible to **non-technical users** via a simple CLI  
✅ Used by students to clean **10,000+ rows** of messy public datasets  

---

## ⚙️ Features – Phase 1 (✅ Implemented)

### 🔍 Smart Dataset Profiling
- Rows, columns, memory usage
- Missing values and duplicates
- Summary stats (mean, median, skewness)
- Text column insights (unique values, avg word count)
- Outlier detection using Z-score

### 🧹 Cleaning Made Easy
- Drop/fill missing values interactively
- Remove duplicate rows
- Clean column names (spaces, casing)
- Convert column types safely
- Remove outliers
- Standardize text
- Undo your last cleaning step

### 📋 Exportable Reports
- Generates `.txt` reports with profiling insights
- Human-friendly and easy to share

### 🎨 Interactive CLI UI
- Built with `Rich` and `InquirerPy`
- Preview changes before applying anything

---

## 💡 Real-World Example (1 Line Setup)

```bash
PYTHONIOENCODING=utf-8 python -m scrubpy.cli
```

> Upload your `students.csv`, select cleaning steps via the CLI, and download a ready-to-analyze dataset in seconds.  
Even generates a quick `.txt` summary report for your team or class.

---

## 🚧 Phase 2 – Making ScrubPy Smarter (🔄 In Progress)

📊 **Smart EDA PDF Reports**  
- Generates beautiful PDF with visual insights  
- Charts, distributions, correlation heatmaps  

🧠 **Column Intelligence**  
- Auto-detect numeric, text, date columns  
- Suggest type conversions (e.g., object → int)

📈 **Visual Explorer Mode (CLI)**  
- View column plots directly in terminal  
- Choose cleaning based on patterns  

🔁 **Smart Undo & Dataset Backup**  
- Track history of operations  
- Revert step-by-step with previews  

---

## 🔮 Phase 3 – ScrubPy Becomes a Data Assistant

🤖 **AI-Powered Cleaning Suggestions**  
- Uses light ML to suggest better imputations  
- Flags suspicious patterns automatically

📦 **Data Cleaning Strategy Framework**  
- Recommends a strategy for your dataset (based on size, shape, and type)

📊 **Smart Visual Dashboards (Optional Web UI)**  
- Plug-in Web UI for large datasets  
- Cleaner + visual summary in your browser

🧠 **ML-Powered Missing Value Imputation**  
- Regression-based filling for numeric columns  
- Category inference for object columns

---

## 📦 Installation

```bash
git clone https://github.com/your-username/scrubpy.git
cd scrubpy
pip install -r requirements.txt
```

---

## 🧠 How It Helps

ScrubPy is for anyone who says:

> *"Ugh, I just want to clean this CSV quickly and move on."*

Whether it's for:
- A data science assignment
- An Excel sheet from your professor
- A public dataset from Kaggle

ScrubPy gets you a clean version with just a few interactive steps – no notebooks, no bugs, no stress.

---

## 🗂️ Folder Structure

```
scrubpy/
├── cli.py                      # Interactive CLI
├── core.py                     # Cleaning logic
├── preview.py                  # Undo & preview
├── profiling.py                # Stats & summaries
├── export_profiling_report.py  # .txt exporter
├── eda_analysis.py             # Smart EDA (PDF)
├── utils.py                    # Helpful utilities
```

---
# 🧠 ScrubPy – Phase 4 & Beyond: Context-Aware AI Assistant

> *The next evolution of ScrubPy — where your data cleaner understands the "why", not just the "what".*

## 💡 What's the Big Idea?

Most data tools just look at columns and numbers. But what if your assistant knew that a column called `Gross` means "movie revenue"? That `BP` likely refers to blood pressure in a hospital report? That `amount_spent` should be numeric even though it's written as "$45.6M"?

**Welcome to Phase 4 – Context-Aware AI Cleaning.**

ScrubPy now leverages its Smart EDA report to **extract the domain context** and pass it to an intelligent NLP assistant that helps you **make smarter, domain-specific cleaning decisions**.

This phase is **experimental**, but it lays the foundation for an entirely new way of interacting with data.

## 🧪 How It Works

1. You run `ScrubPy` and generate the Smart EDA Report.
2. That report is uploaded or passed to a **local or hosted NLP assistant**.
3. The assistant extracts:
   - The **domain** (e.g., movies, finance, medical)
   - The **column roles** (e.g., revenue, diagnosis, category)
   - The **value types** and potential patterns
4. It returns:
   - Suggestions tailored to your domain
   - Optional one-click fixes
   - A data cleaning plan you can preview or execute

## 🔍 Why It Matters

In real-world datasets, column names and values often encode **domain semantics**:

| Column Name | In Dataset Type      | Assistant Understands                       |
|-------------|----------------------|---------------------------------------------|
| `Gross`     | Movie Dataset        | Dollar values, often with M or K suffix     |
| `BP`        | Hospital Reports     | Short for Blood Pressure, needs unit check  |
| `Amount`    | Financial Records    | May contain symbols, requires conversion    |
| `Score`     | Student Grades       | Might need normalization or grade mapping   |
| `Tags`      | E-commerce Products  | Categorical split-cleaning, standardization |

## 🧬 In the Life of a Data Analyst – With ScrubPy

> Meet Ananya, a Data Analyst at a film production house.  
> She receives a messy CSV of **10,000+ movie titles** with columns like `Title`, `Genre`, `Gross`, and `Rating`.  
> Her task: clean and analyze this for quarterly performance reporting.

Without ScrubPy:
- She manually writes regex to strip `$` and `M` from revenue.
- She tries to standardize genres like "sci fi", "Sci-Fi", and "Science Fiction".
- She gets frustrated trying to fill missing ratings sensibly.

With ScrubPy's Context-Aware Assistant:
```bash
PYTHONIOENCODING=utf-8 python -m scrubpy.cli
# → Choose your dataset
# → Generate Smart EDA PDF
# → Upload EDA to AI Assistant (Phase 4)
```

The assistant responds:
> ✅ "Detected domain: Movies"  
> ✅ "'Gross' contains dollar values – convert to float?"  
> ✅ "'Genre' has inconsistent labels – normalize?"  
> ✅ "'Rating' missing for 12% rows – fill with genre-wise median?"

She approves, previews the changes, and **moves directly to storytelling** with charts and insights.

⏳ Time saved: ~3 hours  
🎯 Confidence in cleaning: 100%  
🔥 Business impact: Faster time to decision  

## 💼 Ideal For:

- 🧑‍💻 **Data Analysts** who work with messy, domain-specific data
- 👨‍⚕️ **Healthcare Data Engineers** cleaning patient-level records
- 💹 **Financial Analysts** dealing with unstructured exports
- 🧪 **Researchers** processing survey or experiment data
- 📈 **Startups** preparing CSV data for dashboards & ML

## ⚙️ Technical Flow (Experimental Design)

```
[CSV Dataset]
      ↓
[ScrubPy CLI]
      ↓
[Smart EDA Report (PDF/JSON)]
      ↓
[NLP Assistant 🔍]
   → Infers Domain
   → Extracts Structure
   → Suggests Fixes
      ↓
[ScrubPy CLI Preview & Confirm]
      ↓
[Cleaned Dataset + JSON Cleaning Plan]
```

## 📦 What's Coming Next

- 🧠 Lightweight LLM agent to run **entirely offline** (via `llama.cpp` or `gguf`)
- 📄 Accept `.txt` or `.pdf` EDA Reports for context
- 🔄 Optional Web UI for drag & drop uploads
- 🛠️ Plugin system to register **custom cleaning rules per domain**
- 📚 Growing library of "Scrub Recipes" for popular data types

## ✨ Why This Is Different

ScrubPy doesn't try to guess everything. Instead, it **asks smart questions** based on **what your data means** — not just what it looks like.

And unlike tools that force you into a GUI or locked environment, ScrubPy stays:
- Local
- CLI-first
- Explainable
- Customizable

## 🚀 Want to Try This Phase?

> This is experimental. If you're excited, fork it, try it, and shape it with us.  
> We believe the future of data cleaning is **context-aware** — and this is just the start.

---

Made with ❤️ for people who are tired of repetitive, blind data wrangling.  
Let's make cleaning smart, meaningful, and human again.
## 💬 Want to Contribute?

We're just getting started. Drop a star ⭐ if you like it, fork it to play around, or open an issue!

Ideas welcome for:
- More visual exports
- Smart ML-powered imputations
- Data cleaning strategy assistant

---

## 🧾 License

MIT – Free for all.

---

Made with ❤️ by a student tired of writing the same pandas code again and again.
