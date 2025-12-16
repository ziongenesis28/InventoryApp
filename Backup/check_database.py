# save as check_database.py
import pandas as pd
import os

def check_database():
    filepath = "data/inventory.xlsx"
    
    if not os.path.exists(filepath):
        print("❌ Database file doesn't exist!")
        return
    
    print(f"📊 Checking database: {filepath}")
    print(f"File size: {os.path.getsize(filepath)} bytes")
    
    try:
        # List all sheets
        xls = pd.ExcelFile(filepath)
        print(f"\nSheets found: {xls.sheet_names}")
        
        # Check each sheet
        for sheet in xls.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet)
            print(f"\n{sheet}:")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {list(df.columns)}")
            
            if len(df) > 0:
                print(f"  First few rows:")
                print(df.head(2).to_string())
    
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    check_database()