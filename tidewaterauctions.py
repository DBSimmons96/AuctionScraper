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
    # URL to scrape
    url = "https://www.tidewaterauctions.com/upcoming-real-estate-auctions"
    driver.get(url)

    print("Scraping sale items...\n")

    # List to store all records
    all_data = []

    # Wait for elements to be present and find all us-sale-item elements
    wait = WebDriverWait(driver, 10)
    sale_items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "us-sale-item")))

    for i, item in enumerate(sale_items, 1):
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
            'Auction Website': 'tidewaterauctions.com',
            'Notes': '',
            'Listing': ''
        }

        # Get text content
        text = item.text
        record_data['Listing'] = text

        # Process text line by line
        lines = text.split('\n')
        for line in lines:
            # Try to extract address and location info
            if any(word in line.lower() for word in ['street', 'road', 'avenue', 'lane', 'drive', 'court', 'way', 'circle']):
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
            print(f"Processed Sale Item #{i}")

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
    output_path = r"C:\Users\wally\Desktop\UJpwork\AuctonScraper\TideWaterAuctionsInfo.xlsx"
    df.to_excel(output_path, index=False)
    print(f"\nData successfully exported to {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()