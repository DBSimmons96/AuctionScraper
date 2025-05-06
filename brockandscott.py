import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")

# Use ChromeDriverManager to automatically manage the driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    url = "https://www.brockandscott.com/foreclosure-sales/?_sft_foreclosure_state=md"
    driver.get(url)

    print("Scraping Brock and Scott MD foreclosures...\n")

    # Wait for records to be present
    wait = WebDriverWait(driver, 10)
    records = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "record")))

    for i, record in enumerate(records, 1):
        print(f"Record #{i}")
        print("=" * 50)

        # Find all forecol elements within this record
        forecols = record.find_elements(By.CLASS_NAME, "forecol")

        # Print text from each forecol
        for forecol in forecols:
            if forecol.text.strip():  # Only print if there's text
                print(forecol.text)

        print("-" * 50 + "\n")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()