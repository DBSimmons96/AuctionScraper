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
    url = "https://app.hwestauctions.com/"
    driver.get(url)

    print("Scraping HWest Auctions details...\n")

    # Wait for accordion buttons to be present
    wait = WebDriverWait(driver, 10)
    accordion_buttons = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "accordion-button")))

    for i, button in enumerate(accordion_buttons, 1):
        print(f"Section #{i}")
        print("=" * 50)

        # Click the button to expand content
        driver.execute_script("arguments[0].click();", button)

        # Small delay to let content load
        driver.implicitly_wait(1)

        # Find the associated collapse section
        collapse_id = button.get_attribute("data-bs-target")
        collapse_section = driver.find_element(By.CSS_SELECTOR, collapse_id)

        # Get card title and text from expanded section
        try:
            title = collapse_section.find_element(By.CLASS_NAME, "card-title")
            print(f"Title: {title.text}\n")
        except:
            print("No title found\n")

        try:
            card_text = collapse_section.find_element(By.CLASS_NAME, "card-text")
            print(f"Details: {card_text.text}\n")
        except:
            print("No details found\n")

        print("-" * 50 + "\n")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()