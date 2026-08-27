import pandas as pd
import re

def clean_weather_data(input_file="data_raw.csv", output_file="data_clean.csv"):
    df_raw = pd.read_csv(input_file)
    
    print("=== BEFORE CLEANING ===")
    print(f"Shape: {df_raw.shape}")
    print(df_raw.head())
    print("\nMissing Values:\n", df_raw.isnull().sum())
    
    # 1. Drop duplicates
    df = df_raw.drop_duplicates(subset=["city"]).copy()
    
    # 2. Filter out null or empty records
    df = df.dropna(subset=["city", "raw_temp"])
    
    # 3. Extract numerical temperature (°C/°F) using RegEx
    def extract_temp(val):
        match = re.search(r'(-?\d+)', str(val))
        return int(match.group(1)) if match else None

    df["temp_celsius"] = df["raw_temp"].apply(extract_temp)
    
    # Drop rows where temperature parsing failed
    df = df.dropna(subset=["temp_celsius"])
    df["temp_celsius"] = df["temp_celsius"].astype(int)
    
    # 4. Clean City Text
    df["city"] = df["city"].str.replace(r'[*N/A]', '', regex=True).str.strip()
    
    print("\n=== AFTER CLEANING ===")
    print(f"Shape: {df.shape}")
    print(df.head())
    
    # Save cleaned data to CSV
    df.to_csv(output_file, index=False)
    print(f"\nCleaned dataset saved to {output_file}")

if __name__ == "__main__":
    clean_weather_data()