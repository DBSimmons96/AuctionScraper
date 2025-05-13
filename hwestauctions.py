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
wait = WebDriverWait(driver, 10)

try:
    url = "https://app.hwestauctions.com/"
    driver.get(url)

    print("Scraping HWest Auctions details...\n")

    # List to store all records
    all_data = []

    # Wait for accordion buttons
    accordion_buttons = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "accordion-button")))

    for i, button in enumerate(accordion_buttons, 1):
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
            'Auction Website': 'hwestauctions.com',
            'Notes': '',
            'Listing': ''
        }

        # Click the button to expand content
        driver.execute_script("arguments[0].click();", button)
        driver.implicitly_wait(1)

        # Find the associated collapse section
        collapse_id = button.get_attribute("data-bs-target")
        collapse_section = driver.find_element(By.CSS_SELECTOR, collapse_id)

        # Get text content
        full_text = []

        try:
            title = collapse_section.find_element(By.CLASS_NAME, "card-title").text
            full_text.append(title)
        except:
            pass

        try:
            details = collapse_section.find_element(By.CLASS_NAME, "card-text").text
            full_text.append(details)
        except:
            pass

        # Store full listing text
        listing_text = '\n'.join(full_text)
        record_data['Listing'] = listing_text

        # Try to extract address and location info
        if listing_text:
            # Extract address if present
            text_lines = listing_text.split('\n')
            for line in text_lines:
                if any(word in line.lower() for word in
                       ['street', 'road', 'avenue', 'lane', 'drive', 'court', 'way', 'circle']):
                    record_data['Address'] = line.strip()
                    if 'Maryland' in line:
                        parts = line.split('Maryland')
                        if len(parts) > 1:
                            # Get ZIP
                            zip_part = parts[1].strip()
                            record_data['Zip'] = zip_part.strip(' ,')
                            # Get City
                            city_part = parts[0].split(',')[-1].strip()
                            record_data['City'] = city_part

        if record_data['Address']:  # Only append if we found an address
            all_data.append(record_data)
            print(f"Processed Listing #{i}")

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
    output_path = r"C:\Users\wally\Desktop\UJpwork\AuctonScraper\HWestInfo.xlsx"
    df.to_excel(output_path, index=False)
    print(f"\nData successfully exported to {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()