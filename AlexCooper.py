import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")

# Use ChromeDriverManager to automatically manage the driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # URL to scrape
    url = "https://realestate.alexcooper.com/foreclosures"
    driver.get(url)

    print("Scraping active foreclosure listings...\n")

    # Find all foreclosure container elements
    containers = driver.find_elements(By.CLASS_NAME, "alexcooper-foreclosure-container")

    # Process each container
    for i, container in enumerate(containers, 1):
        # Check if the container has a cancelled div
        cancelled_div = container.find_elements(By.CLASS_NAME, "foreclosure-lot.cancelled")

        # Only print if the listing is not cancelled
        if not cancelled_div:
            print(f"Active Listing #{i}")
            print("-" * 50)
            print(container.text)
            print("\n")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()