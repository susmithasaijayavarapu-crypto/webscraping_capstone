import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)
driver.get("https://www.timeanddate.com/weather/")
time.sleep(3)  # Wait for DOM load
    
data = []

rows = driver.find_elements(By.XPATH, "/html/body/div[5]/section[1]/div/section/div[1]/div/table//tr")
for row in rows:
        try:
            city_elem = row.find_elements(By.TAG_NAME, "td")
            if not city_elem:
                continue
                
            # Parse alternating column pairs typically present on weather tables
            for i in range(0, len(city_elem), 2):
                if i + 1 < len(city_elem):
                    city_name = city_elem[i].text.strip()
                    temp_val = city_elem[i+1].text.strip()
                    
                    if city_name:
                        data.append({
                            "city": city_name,
                            "raw_temp": temp_val,
                            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
        except Exception as e:
            # Handle missing tags or changing DOM elements gracefully
            continue

driver.quit()
raw_df = pd.DataFrame(data)

raw_df.to_csv("data_raw.csv", index=False)
print(f"Scraped {len(raw_df)} raw records successfully.")
