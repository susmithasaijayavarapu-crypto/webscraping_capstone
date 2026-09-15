import sqlite3
import pandas as pd

# ==========================================
# 1. LOAD RAW DATA
# ==========================================
raw_df = pd.read_csv("data_raw.csv")

print("--- STAGE 1: RAW DATA INSPECTION ---")
print(f"Initial row count: {len(raw_df)}")
print(raw_df.head(4))
print("\nMissing values in raw dataset:")
print(raw_df.isnull().sum())
print("------------------------------------\n")


# ==========================================
# 2. CLEANING STAGE
# ==========================================
clean_df = raw_df.copy()

# A. Clean city names (remove asterisk footnote markers and trailing whitespace)
clean_df["city"] = clean_df["city"].astype(str).str.replace(r"\*$", "", regex=True).str.strip()

# B. Extract numeric temperature value (handles integer extraction)
clean_df["temperature"] = (
    clean_df["raw_temp"]
    .astype(str)
    .str.extract(r"(-?\d+)")  # Extract digits, including negative signs
    .astype(float)
)

# C. Extract temperature unit (e.g., °F or °C)
clean_df["temp_unit"] = clean_df["raw_temp"].astype(str).str.extract(r"(°[FC])")

# D. Convert scraped_at to proper datetime format
clean_df["scraped_at"] = pd.to_datetime(clean_df["scraped_at"], errors="coerce")

# E. Handle missing / malformed records (drop any failed extractions)
clean_df = clean_df.dropna(subset=["city", "temperature", "scraped_at"])

# F. Drop exact duplicates across city and scraped timestamp
clean_df = clean_df.drop_duplicates(subset=["city", "scraped_at"])

# Drop original unparsed string column
clean_df = clean_df.drop(columns=["raw_temp"])


# ==========================================
# 3. TRANSFORMATIONS & METRICS
# ==========================================
# Add Celsius conversion column for standardized analytical reporting
clean_df["temp_celsius"] = clean_df.apply(
    lambda row: (row["temperature"] - 32) * 5 / 9 if row["temp_unit"] == "°F" else row["temperature"],
    axis=1,
).round(1)

# Categorize weather condition based on temperature ranges
def categorize_temp(celsius):
    if celsius < 10:
        return "Cold"
    elif 10 <= celsius <= 25:
        return "Mild"
    else:
        return "Hot"

clean_df["temp_category"] = clean_df["temp_celsius"].apply(categorize_temp)

print("--- STAGE 2: BEFORE vs AFTER METRICS ---")
print(f"Raw rows:      {len(raw_df)}")
print(f"Clean rows:    {len(clean_df)}")
print(f"Rows dropped:  {len(raw_df) - len(clean_df)}")
print("\nCleaned Data Preview:")
print(clean_df.head(4))
print("----------------------------------------\n")


# ==========================================
# 4. SAVE TO SQLITE DATABASE
# ==========================================
db_name = "weather_data.db"
conn = sqlite3.connect(db_name)

# A. Save main cleaned dataset table
clean_df.to_sql("weather_records", conn, if_exists="replace", index=False)

# B. Aggregate transformation: Summary table by temperature category
summary_df = (
    clean_df.groupby("temp_category")
    .agg(
        city_count=("city", "count"),
        avg_temp_c=("temp_celsius", "mean"),
        max_temp_c=("temp_celsius", "max"),
        min_temp_c=("temp_celsius", "min"),
    )
    .round(1)
    .reset_index()
)

# Save summary analytics table to SQLite
summary_df.to_sql("weather_summary", conn, if_exists="replace", index=False)

conn.close()

print("--- STAGE 3: DATABASE PERSISTENCE COMPLETE ---")
print(f"Successfully created '{db_name}' with tables 'weather_records' and 'weather_summary'.")