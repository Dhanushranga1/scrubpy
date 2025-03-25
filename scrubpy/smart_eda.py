# scrubpy/smart_eda.py
from scrubpy.utils import clean_text_for_pdf

from scrubpy.eda_analysis import SmartEDA

def generate_smart_eda_pdf(df, dataset_name="dataset"):
    eda = SmartEDA(df, dataset_name=dataset_name)
    
    eda.run()
