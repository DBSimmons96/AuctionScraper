import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")

# Use ChromeDriverManager to automatically manage the driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)

try:
    url = "https://matlsales.orlans.com/Sales.aspx"
    driver.get(url)

    # Wait for and click the accept button
    accept_button = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "input[type='submit'][value='Accept']")))
    driver.execute_script("arguments[0].click();", accept_button)

    # Small delay to let the page update
    time.sleep(2)

    # Wait for and get the first element with class "sdcolname"
    file_number_header = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, "sdcolname")))

    # Get the first file number TD within the sale display table
    file_number = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, ".saledisplaytable td:first-child")))
    # Wait for sale display tables to be present
    tables = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "saledisplaytable")))

    # Loop through each table
    for table_index, table in enumerate(tables, 1):
        print(f"\nTable {table_index}")
        print("=" * 50)

        # Find all tbody elements in this table
        tbodies = table.find_elements(By.TAG_NAME, "tbody")

        # Loop through each tbody
        for tbody_index, tbody in enumerate(tbodies, 1):
            print(f"\nBody {tbody_index}:")
            print("-" * 30)

            # Get all rows in this tbody
            rows = tbody.find_elements(By.TAG_NAME, "tr")

            # Process each row
            for row in rows:
                # Get all cells in the row
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    row_text = " | ".join([cell.text.strip() for cell in cells if cell.text.strip()])
                    if row_text:
                        print(row_text)

except Exception as e:
    print(f"An error occurred: {e}")
    print(f"Error details: {str(e)}")

finally:
    driver.quit()