import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scrubpy.profiling import DataProfiler
from fpdf import FPDF
from datetime import datetime
from scrubpy.utils import clean_text_for_pdf


class SmartEDA:
    def __init__(self, df: pd.DataFrame, dataset_name="dataset", extra_data=None):
        self.df = df
        self.name = dataset_name.replace(".csv", "")
        self.profiler = DataProfiler(df)
        self.extra_data = extra_data or {}
        self.output_dir = f"eda_outputs/{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)

        self.font_path = "scrubpy/fonts/DejaVuSans.ttf"
        self.font_name = "DejaVu"

    def auto_categorize_columns(self):
        return {
            "Numeric": self.df.select_dtypes(include=[np.number]).columns.tolist(),
            "Categorical": self.df.select_dtypes(include=["object", "category"]).columns.tolist(),
            "Datetime": self.df.select_dtypes(include=["datetime64"]).columns.tolist()
        }

    def visualize_column(self, col):
        plt.figure(figsize=(6, 4))
        if pd.api.types.is_numeric_dtype(self.df[col]):
            sns.histplot(self.df[col].dropna(), kde=True, color="skyblue")
            plt.title(f"Distribution of {col}")
        elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
            self.df[col].value_counts().sort_index().plot()
            plt.title(f"Time Distribution of {col}")
        elif self.df[col].nunique() < 20:
            self.df[col].value_counts().plot(kind="bar", color="orange")
            plt.title(f"Top Categories in {col}")
        else:
            return
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{col}_plot.png"))
        plt.close()

    def plot_missing_heatmap(self):
        plt.figure(figsize=(10, 6))
        sns.heatmap(self.df.isnull(), cbar=False, cmap="YlOrRd")
        plt.title("Missing Values Heatmap")
        plt.tight_layout()
        path = os.path.join(self.output_dir, "missing_heatmap.png")
        plt.savefig(path)
        plt.close()
        return path

    def plot_correlation_matrix(self):
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] >= 2:
            plt.figure(figsize=(8, 6))
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Correlation Matrix")
            plt.tight_layout()
            path = os.path.join(self.output_dir, "correlation_matrix.png")
            plt.savefig(path)
            plt.close()
            return path
        return None

    def create_pdf_report(self):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Success Register Unicode-compliant TTF font
        try:
            pdf.add_font(self.font_name, "", self.font_path, uni=True)
            pdf.set_font(self.font_name, size=16)
        except Exception as e:
            # Fallback to Arial if custom font fails
            print(f"Warning: Custom font failed ({e}), using Arial")
            pdf.set_font('Arial', size=16)
            self.font_name = 'Arial'
        
        pdf.cell(0, 10, f"ScrubPy EDA Report - {self.name}", ln=True, align="C")

        pdf.set_font(self.font_name, size=12)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

        # Dataset Overview
        pdf.set_font(self.font_name, size=14)
        pdf.cell(0, 10, "Dataset Overview", ln=True)
        pdf.set_font(self.font_name, size=12)
        for k, v in self.profiler.dataset_overview().items():
            # Ensure overview text fits on page
            overview_text = f"- {k}: {v}"
            if len(overview_text) > 100:
                overview_text = overview_text[:97] + "..."
            pdf.cell(0, 10, overview_text, ln=True)

        # Column Info
        pdf.set_font(self.font_name, size=14)
        pdf.cell(0, 10, "Column Details", ln=True)
        pdf.set_font(self.font_name, size=12)
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            missing = self.df[col].isnull().mean() * 100
            uniq = self.df[col].nunique()
            # Truncate sample data to prevent overflow
            sample_data = str(self.df[col].dropna().unique()[:3])
            if len(sample_data) > 50:
                sample_data = sample_data[:47] + "..."
            
            # Create the text and ensure it's not too long
            text = f"• {col} | Type: {dtype} | Missing: {missing:.1f}% | Unique: {uniq} | Sample: {sample_data}"
            if len(text) > 150:
                text = text[:147] + "..."
            
            # Use specific width instead of 0 to avoid layout issues
            try:
                pdf.multi_cell(190, 8, text)  # Use specific width
            except Exception as e:
                # Fallback to simple cell if multi_cell fails
                print(f"Warning: multi_cell failed for {col}, using simple cell")
                pdf.cell(0, 8, text[:100] + "..." if len(text) > 100 else text, ln=True)

        # Column Visuals
        pdf.set_font(self.font_name, size=14)
        pdf.cell(0, 10, "Column Visualizations", ln=True)
        for plot in sorted(os.listdir(self.output_dir)):
            if plot.endswith(".png") and "plot" in plot:
                pdf.add_page()
                pdf.image(os.path.join(self.output_dir, plot), w=180)

        # Missing Heatmap
        heatmap_path = self.plot_missing_heatmap()
        if heatmap_path:
            pdf.add_page()
            pdf.image(heatmap_path, w=180)

        # Correlation Heatmap
        corr_path = self.plot_correlation_matrix()
        if corr_path:
            pdf.add_page()
            pdf.image(corr_path, w=180)

        # High Correlation Pairs
        pdf.add_page()
        pdf.set_font(self.font_name, size=14)
        pdf.cell(0, 10, "Top Correlations", ln=True)
        corr = self.df.select_dtypes(include=[np.number]).corr().stack().reset_index()
        corr.columns = ["Feature 1", "Feature 2", "Correlation"]
        corr = corr[corr["Feature 1"] != corr["Feature 2"]]
        top_corr = corr.reindex(corr.Correlation.abs().sort_values(ascending=False).index).drop_duplicates().head(5)
        pdf.set_font(self.font_name, size=12)
        for _, row in top_corr.iterrows():
            pdf.cell(0, 10, f"- {row['Feature 1']} & {row['Feature 2']} = {row['Correlation']:.2f}", ln=True)

        # Summary & Recommendations
        pdf.add_page()
        pdf.set_font(self.font_name, size=14)
        pdf.cell(0, 10, "Final Recommendations", ln=True)
        pdf.set_font(self.font_name, size=12)
        for rec in self.profiler.suggest_cleaning_actions():
            # Clean and truncate recommendation text to prevent overflow
            clean_rec = clean_text_for_pdf(f"- {rec}")
            if len(clean_rec) > 200:
                clean_rec = clean_rec[:197] + "..."
            
            # Use specific width instead of 0 to avoid layout issues
            try:
                pdf.multi_cell(190, 10, clean_rec)  # Use specific width
            except Exception as e:
                # Fallback to simple cell if multi_cell fails
                print(f"Warning: multi_cell failed for recommendation, using simple cell")
                pdf.cell(0, 10, clean_rec[:80] + "..." if len(clean_rec) > 80 else clean_rec, ln=True)


        out_path = os.path.join(self.output_dir, f"{self.name}_smart_eda_report.pdf")
        pdf.output(out_path)
        print(f"\nSuccess Smart EDA PDF saved to: {out_path}")

    def run(self):
        print("\nRunning Smart EDA...")
        for col in self.df.columns:
            self.visualize_column(col)
        self.create_pdf_report()
