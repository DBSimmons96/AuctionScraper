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
    # URL to scrape
    url = "https://www.tidewaterauctions.com/upcoming-real-estate-auctions"
    driver.get(url)

    print("Scraping sale items...\n")

    # Wait for elements to be present and find all us-sale-item elements
    wait = WebDriverWait(driver, 10)
    sale_items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "us-sale-item")))

    # Print text from each sale item
    for i, item in enumerate(sale_items, 1):
        print(f"Sale Item #{i}")
        print("-" * 50)
        print(item.text)
        print("\n")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()