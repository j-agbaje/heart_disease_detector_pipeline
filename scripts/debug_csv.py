#!/usr/bin/env python3
"""
Debug script to analyze the CSV data and find problematic rows
"""

import pandas as pd
import numpy as np

def debug_csv_data():
    """Debug the CSV data to find NaN values and problematic rows"""
    try:
        # Read the CSV file
        df = pd.read_csv('data/heart.csv')
        print(f"Total records: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print("\n" + "="*50)
        
        # Check for NaN values in each column
        print("NaN values per column:")
        for col in df.columns:
            nan_count = df[col].isna().sum()
            if nan_count > 0:
                print(f"  {col}: {nan_count} NaN values")
        
        print("\n" + "="*50)
        
        # Check specific problematic rows mentioned in error (around 916, 918, 920)
        problematic_rows = [915, 916, 917, 918, 919, 920]  # 0-indexed
        
        print("Checking problematic rows:")
        for idx in problematic_rows:
            if idx < len(df):
                row = df.iloc[idx]
                print(f"\nRow {idx + 1} (0-indexed: {idx}):")
                has_nan = False
                for col in df.columns:
                    value = row[col]
                    if pd.isna(value) or str(value).lower() == 'nan':
                        print(f"  {col}: {value} (NaN detected)")
                        has_nan = True
                    else:
                        print(f"  {col}: {value}")
                
                if not has_nan:
                    print("  No NaN values found in this row")
        
        print("\n" + "="*50)
        
        # Check data types
        print("Data types:")
        print(df.dtypes)
        
        print("\n" + "="*50)
        
        # Check for any rows with all NaN values
        all_nan_rows = df[df.isna().all(axis=1)]
        if len(all_nan_rows) > 0:
            print(f"Found {len(all_nan_rows)} rows with all NaN values:")
            print(all_nan_rows.index.tolist())
        
        # Check for rows with any NaN values
        any_nan_rows = df[df.isna().any(axis=1)]
        if len(any_nan_rows) > 0:
            print(f"Found {len(any_nan_rows)} rows with some NaN values:")
            print("Row indices:", any_nan_rows.index.tolist())
            
        print("\n" + "="*50)
        
        # Show unique values for categorical columns
        categorical_cols = ['sex', 'dataset', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
        print("Unique values in categorical columns:")
        for col in categorical_cols:
            if col in df.columns:
                unique_vals = df[col].unique()
                print(f"  {col}: {unique_vals}")
        
        print("\n" + "="*50)
        
        # Check for any non-numeric values in numeric columns
        numeric_cols = ['age', 'trestbps', 'chol', 'thalch', 'oldpeak', 'ca', 'num']
        print("Checking numeric columns for non-numeric values:")
        for col in numeric_cols:
            if col in df.columns:
                # Try to convert to numeric and see what fails
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                non_numeric_mask = df[col].notna() & numeric_series.isna()
                if non_numeric_mask.any():
                    print(f"  {col}: Non-numeric values found:")
                    print(f"    Values: {df[col][non_numeric_mask].unique()}")
                    print(f"    Row indices: {df[col][non_numeric_mask].index.tolist()}")
                else:
                    print(f"  {col}: All values are numeric or NaN")
        
    except Exception as e:
        print(f"Error analyzing CSV: {e}")

if __name__ == "__main__":
    debug_csv_data()