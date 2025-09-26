from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Setup
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 60)
url = "https://cutoff.tneaonline.org/"

print("🔵 Opening site...")
driver.get(url)

# Step 1: Click Proceed
print("🔵 Waiting for 'Proceed' button...")
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Proceed']"))).click()

# Step 2: Select Year and Category (Category is defaulted to Cutoff)
print("🔵 Waiting for 'Year' dropdown...")
try:
    year_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "syear")))
    Select(year_dropdown).select_by_visible_text("2021")
    print("✅ Year selected!")
except Exception as e:
    print(f"❌ Failed to select year: {e}")
    driver.quit()
    raise SystemExit()

# Click 'Get Details'
print("🔵 Clicking 'Get Details' button...")
try:
    get_details_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Get Details']")))
    get_details_btn.click()
    print("✅ Clicked 'Get Details'!")
except Exception as e:
    print(f"❌ Failed to click 'Get Details': {e}")
    driver.quit()
    raise SystemExit()

# Step 3: Wait for the table
print("🟢 Waiting for table to load...")
try:
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-responsive-sm")))
except Exception as e:
    print(f"❌ Table did not load: {e}")
    driver.save_screenshot("debug_screenshot.png")
    driver.quit()
    raise SystemExit()

# Step 4: Scrape data from all pages
print("🔍 Scraping pages...")

all_rows = []
headers = []
page = 1

while True:
    print(f"📄 Scraping page {page}...")
    time.sleep(1.5)

    table_container = driver.find_element(By.CLASS_NAME, "table-responsive-sm")
    table = table_container.find_element(By.TAG_NAME, "table")

    # Extract headers (only once on the first page)
    if page == 1:
        thead = table.find_element(By.TAG_NAME, "thead")
        header_row = thead.find_element(By.TAG_NAME, "tr")
        headers = [th.text.strip() for th in header_row.find_elements(By.TAG_NAME, "th")]

    # Extract data rows from tbody
    tbody = table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        all_rows.append([col.text.strip() for col in cols])

    # Try going to next page
    try:
        page += 1
        next_link = driver.find_element(By.LINK_TEXT, str(page))
        driver.execute_script("arguments[0].click();", next_link)
    except:
        print("🛑 No more pages.")
        break

# Step 5: Save to CSV
df = pd.DataFrame(all_rows, columns=headers)
df.to_csv("tnea_cutoff_2021.csv", index=False)
print("✅ Done! Data saved as 'tnea_cutoff_2021.csv'")

driver.quit()