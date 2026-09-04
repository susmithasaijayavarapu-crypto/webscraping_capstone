import sqlite3
import pandas as pd


def load_data_to_sqlite(
    raw_csv="data_raw.csv",
    clean_csv="data_clean.csv",
    db_name="weather_project.db",
):
    # 1. Connect to SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 2. Read existing CSV files into pandas DataFrames
    df_raw = pd.read_csv(raw_csv)
    df_clean = pd.read_csv(clean_csv)

    # 3. Load DataFrames into separate SQLite tables
    # "raw_weather": Unmodified raw data from scraper
    # "cleaned_weather": Cleaned, deduplicated, and transformed data
    df_raw.to_sql("raw_weather", conn, if_exists="replace", index=False)
    df_clean.to_sql("cleaned_weather", conn, if_exists="replace", index=False)

    print(
        f"Database '{db_name}' updated successfully with tables: raw_weather, cleaned_weather\n"
    )

    # 4. Perform SQLite transformations & verification queries
    print("=== SQL VERIFICATION & AGGREGATIONS ===")

    # Verification: Record counts before vs after
    cursor.execute("SELECT COUNT(*) FROM raw_weather")
    raw_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cleaned_weather")
    clean_count = cursor.fetchone()[0]

    print(
        f"Raw Table Count: {raw_count} | Cleaned Table Count: {clean_count}"
    )

    # SQL Data Transformation: Create a high-level summary table directly in SQLite
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS city_weather_summary AS
        SELECT 
            city,
            temp_celsius,
            CASE 
                WHEN temp_celsius >= 30 THEN 'Hot'
                WHEN temp_celsius BETWEEN 15 AND 29 THEN 'Moderate'
                ELSE 'Cold'
            END AS temperature_category,
            scraped_at
        FROM cleaned_weather
    """)
    conn.commit()

    # Display Top 5 Warmest Cities from the SQLite database
    print("\n--- Top 5 Warmest Cities (Queried from SQLite) ---")
    query = """
        SELECT city, temp_celsius, temperature_category 
        FROM city_weather_summary 
        ORDER BY temp_celsius DESC 
        LIMIT 5
    """
    summary_df = pd.read_sql_query(query, conn)
    print(summary_df)

    conn.close()


if __name__ == "__main__":
    load_data_to_sqlite()