import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.timeanddate.com/weather/")
time.sleep(3)  # Wait for dynamic table contents to load

data = []

# Target the weather table specifically using its exact class name
rows = driver.find_elements(By.CSS_SELECTOR, "table.zebra.fw.tb-theme tbody tr")

for row in rows:
    # Extract all city anchors and temperature spans inside this specific row
    city_links = row.find_elements(By.CSS_SELECTOR, "td a")
    # Temperatures on timeanddate use class 'rbi' or 't'
    temp_elements = row.find_elements(By.CSS_SELECTOR, "td.rbi, span.rbi")

    # Pair each city in the row with its corresponding temperature element
    for city_elem, temp_elem in zip(city_links, temp_elements):
        city_name = city_elem.text.strip()
        temp_val = temp_elem.text.strip()

        if city_name and temp_val:
            data.append({
                "city": city_name,
                "raw_temp": temp_val,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            })

driver.quit()

raw_df = pd.DataFrame(data)
raw_df.to_csv("data_raw.csv", index=False)
print(f"Scraped {len(raw_df)} raw weather records successfully.")