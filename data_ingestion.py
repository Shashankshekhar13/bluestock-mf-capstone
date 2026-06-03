import os
import glob
import pandas as pd

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_dir = os.path.join(script_dir, "data", "raw")
    print(f"Scanning for CSV datasets in: {raw_data_dir}\n")
    
    # Find all CSV files in the raw data directory
    csv_files = glob.glob(os.path.join(raw_data_dir, "*.csv"))
    
    if not csv_files:
        print("No CSV files found in data/raw/ yet.")
        print("Please add the 10 CSV datasets to data/raw/ and run this script again.")
        return
        
    print(f"Found {len(csv_files)} CSV files in data/raw/:\n")
    
    for idx, file_path in enumerate(sorted(csv_files), 1):
        file_name = os.path.basename(file_path)
        print("=" * 80)
        print(f"[{idx}] File: {file_name}")
        print("=" * 80)
        
        try:
        
            df = pd.read_csv(file_path)
            
         
            print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            print("-" * 50)
            

            print("Data Types:")
            print(df.dtypes)
            print("-" * 50)
            
            print("First 5 Rows:")
            print(df.head())
            print("\n")
            
        except Exception as e:
            print(f"Error loading {file_name}: {e}\n")

if __name__ == "__main__":
    main()
