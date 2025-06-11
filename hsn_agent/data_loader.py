from typing import List, Dict, Union, Any, Optional
import os
import pandas as pd

# --- load the hsn data file  ---
def load_hsn_data(file_path: str) -> Dict[str, str]:
    """
    Loads HSN data from an Excel file into an efficient in-memory dictionary.
    This function is called once when the application starts.
    """
    if not os.path.exists(file_path):
        print(f"--- CRITICAL ERROR: HSN master file not found at '{file_path}'. The validation tool will be non-functional. ---")
        return {}

    try:
        df = pd.read_excel(file_path, dtype={'HSNCode': str})

        if 'HSNCode' not in df.columns or 'Description' not in df.columns:
            print("--- CRITICAL ERROR: Excel file must contain 'HSNCode' and 'Description' columns. ---")
            return {}

        df.dropna(subset=['HSNCode'], inplace=True)
        df['HSNCode'] = df['HSNCode'].str.strip()
        hsn_map = pd.Series(df.Description.values, index=df.HSNCode).to_dict()
        
        print(f"--- Successfully loaded {len(hsn_map)} HSN codes into memory. ---")
        return hsn_map

    except Exception as e:
        print(f"--- CRITICAL ERROR: An error occurred while reading the Excel file: {e} ---")
        return {}
    
# Load the data into a global variable as our in-memory data store.
script_dir = os.path.dirname(__file__) 
file_path = os.path.join(script_dir, "..", "data", "HSN_SAC.xlsx")
file_path = os.path.abspath(file_path)
hsn_master_data = load_hsn_data(file_path)

