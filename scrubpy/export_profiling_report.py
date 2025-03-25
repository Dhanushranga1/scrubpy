# profiling_export.py - Enhanced profiling export with visuals & stats

import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import zscore, skew, iqr
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import os

def export_profiling_report(df: pd.DataFrame, dataset_name="dataset", filename="scrubpy_profile_report.txt"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    text_cols = df.select_dtypes(include=[object]).columns
    total_missing = df.isnull().sum().sum()
    missing_cols = df.columns[df.isnull().any()]
    duplicates = df.duplicated().sum()

    # Ensure plots directory exists
    os.makedirs("plots", exist_ok=True)
    pdf_path = "scrubpy_profile_report.pdf"
    pdf = PdfPages(pdf_path)

    report = [
        "=" * 30,
        "📊 SCRUBPY PROFILING REPORT",
        "=" * 30,
        f"\n📁 Dataset: {dataset_name}",
        f"🕒 Generated On: {now}",
        "-" * 40,
        "🧠 Dataset Overview",
        "-" * 40,
        f"- Total Rows              : {df.shape[0]}",
        f"- Total Columns           : {df.shape[1]}",
        f"- Memory Usage (KB)       : {df.memory_usage().sum() / 1024:.2f}",
        "- Column Types:"
    ] + [f"    • {col:15} → {df[col].dtype}" for col in df.columns]

    report += [
        "-" * 40,
        "📉 Missing Value Analysis",
        "-" * 40,
        f"- Total Missing Cells     : {total_missing} ({(total_missing / df.size) * 100:.2f}%)"
    ]
    for col in missing_cols:
        pct = df[col].isnull().mean() * 100
        report.append(f"    • {col:15} → {df[col].isnull().sum()} missing ({pct:.2f}%)")

    report += [
        "-" * 40,
        "📎 Duplicate Rows",
        "-" * 40,
        f"- Total Duplicates Found  : {duplicates}"
    ]

    report += [
        "-" * 40,
        "📈 Statistical Summary (Numeric Columns)",
        "-" * 40
    ]

    for col in numeric_cols:
        stats = df[col].dropna()
        zs_outliers = (np.abs(zscore(stats)) > 3).sum()
        iqr_range = iqr(stats)
        q1, q3 = stats.quantile(0.25), stats.quantile(0.75)
        iqr_outliers = ((stats < (q1 - 1.5 * iqr_range)) | (stats > (q3 + 1.5 * iqr_range))).sum()
        skewness = skew(stats)
        report.append(
            f"{col} => Mean: {stats.mean():.2f}, Median: {stats.median():.2f}, Std: {stats.std():.2f}, "
            f"Skewness: {skewness:.2f}, Z-Outliers: {zs_outliers}, IQR-Outliers: {iqr_outliers}"
        )

        # Plot histogram
        plt.figure(figsize=(6, 4))
        sns.histplot(stats, kde=True, bins=30, color="skyblue")
        plt.title(f"Distribution of {col}")
        plt.xlabel(col)
        plt.tight_layout()
        plot_path = f"plots/hist_{col}.png"
        plt.savefig(plot_path)
        pdf.savefig()
        plt.close()

    report += [
        "-" * 40,
        "📊 Correlation Matrix (Heatmap)",
        "-" * 40
    ]
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        report.append(corr.round(2).to_string())

        # Correlation heatmap
        plt.figure(figsize=(7, 5))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", square=True)
        plt.title("Correlation Matrix")
        plt.tight_layout()
        plt.savefig("plots/correlation_heatmap.png")
        pdf.savefig()
        plt.close()

    report += [
        "-" * 40,
        "🔡 Text Column Summary",
        "-" * 40
    ]
    for col in text_cols:
        unique_vals = df[col].nunique()
        common_val = df[col].mode().iloc[0] if not df[col].mode().empty else "-"
        avg_words = df[col].dropna().astype(str).apply(lambda x: len(x.split())).mean()
        report.append(f"{col}: Unique={unique_vals}, Most Common='{common_val}', Avg Words={avg_words:.1f}")

        # Top values bar plot
        top_vals = df[col].value_counts().head(5)
        plt.figure(figsize=(6, 3))
        sns.barplot(x=top_vals.values, y=top_vals.index, palette="viridis")
        plt.title(f"Top Values in '{col}'")
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    # === Cleaning Recommendations ===
    report += [
        "-" * 40,
        "🧠 Cleaning Recommendations",
        "-" * 40
    ]
    if total_missing > 0:
        report.append(f"- 🛠️ Handle missing values in: {list(missing_cols)}")
    if duplicates > 0:
        report.append(f"- ♻️ Remove {duplicates} duplicate rows")
    if any(" " in col or col.lower() != col for col in df.columns):
        report.append("- 🔠 Fix column names (spaces/capitalization issues)")
    if len(text_cols):
        report.append(f"- 🔡 Standardize text in: {list(text_cols)}")
    for col in numeric_cols:
        stats = df[col].dropna()
        if not stats.empty and (np.abs(zscore(stats)) > 3).sum() > 0:
            report.append(f"- 📉 Consider removing outliers in '{col}'")

    report.append("\n📤 Export Completed Successfully")
    report.append(f"Saved as: {filename}")
    report.append(f"📄 PDF Plots saved as: {pdf_path}")

    # Write to text file
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    pdf.close()
    print(f"\n✅ Profiling report saved to '{filename}' and '{pdf_path}'!\n")
