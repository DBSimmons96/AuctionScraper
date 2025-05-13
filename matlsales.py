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
    time.sleep(2)

    # List to store all data
    all_data = []

    # Wait for tables
    tables = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "saledisplaytable")))

    for table in tables:
        # Initialize record dictionary
        record_data = {
            'County': '',
            'Address': '',
            'City': '',
            'State': 'MD',
            'Zip': '',
            'Auction Date': '',
            'Auction Time': '',
            'Owner First Name': '',
            'Owner Last Name': '',
            'Owner Address': '',
            'Owner City': '',
            'Owner State': '',
            'Owner Zip': '',
            'Auction Website': 'matlsales.orlans.com',
            'Notes': '',
            'Listing': ''
        }

        # Get all rows
        rows = table.find_elements(By.TAG_NAME, "tr")
        full_text = []

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                row_text = " | ".join([cell.text.strip() for cell in cells if cell.text.strip()])
                if row_text:
                    full_text.append(row_text)

                    # Try to extract address and location info
                    if any(word in row_text.lower() for word in ['street', 'road', 'avenue', 'lane', 'drive', 'court']):
                        record_data['Address'] = row_text.split('|')[0].strip()
                        if 'Maryland' in row_text:
                            parts = row_text.split('Maryland')
                            if len(parts) > 1:
                                record_data['Zip'] = parts[1].strip().split()[0]
                                city_part = parts[0].split('|')[-1].strip()
                                record_data['City'] = city_part

        # Store full listing text
        record_data['Listing'] = '\n'.join(full_text)

        if record_data['Address']:  # Only append if we found an address
            all_data.append(record_data)

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Reorder columns
    columns = [
        'County', 'Address', 'City', 'State', 'Zip',
        'Auction Date', 'Auction Time',
        'Owner First Name', 'Owner Last Name',
        'Owner Address', 'Owner City', 'Owner State', 'Owner Zip',
        'Auction Website', 'Notes', 'Listing'
    ]
    df = df[columns]

    # Export to Excel
    output_path = r"C:\Users\wally\Desktop\UJpwork\AuctonScraper\MatlSalesInfo.xlsx"
    df.to_excel(output_path, index=False)
    print(f"\nData successfully exported to {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()