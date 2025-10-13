# scrubpy/smart_eda.py
from scrubpy.utils import clean_text_for_pdf

from scrubpy.eda_analysis import SmartEDA

def generate_smart_eda_pdf(df, dataset_name="dataset", extra_data=None):
    eda = SmartEDA(df, dataset_name=dataset_name, extra_data=extra_data)
    
    eda.run()
