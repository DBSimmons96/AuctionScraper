import pandas as pd
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create a log file with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_path = rf"C:\Users\wally\Desktop\UJpwork\AuctonScraper\Tidewater_log_{timestamp}.txt"


# Create custom print function that writes to both console and file
class Logger:
    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log_file = open(log_file, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()


# Redirect stdout to our custom logger
sys.stdout = Logger(log_path)

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")

# Initialize driver only once
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds

try:
    url = "https://www.tidewaterauctions.com/upcoming-real-estate-auctions"
    driver.get(url)
    print("Accessing website...\n")

    # Wait for page to load
    print("Waiting for page to load...\n")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "us-block-header")))

    print("Scraping sale items...\n")
    all_data = []

    # Define street types list
    street_types = ['street', 'road', 'avenue', 'lane', 'drive', 'court', 'way', 'circle']

    # Find all county sections directly
    county_sections = driver.find_elements(By.CLASS_NAME, "us-block-header")

    for section in county_sections:
        try:
            # Extract county name
            county_element = section.find_element(By.CLASS_NAME, "us-countyname")
            county_name = county_element.text.strip()
            print(f"\nProcessing {county_name}...")

            # Find sale items - looking in parent element and following siblings
            parent = section.find_element(By.XPATH, "./..")
            sale_items = parent.find_elements(By.CLASS_NAME, "us-sale-item")

            for i, item in enumerate(sale_items, 1):
                record_data = {
                    'County': county_name,
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
                    # Look for address lines containing MD
                    if 'MD' in line and any(st in line.lower() for st in street_types):
                        # Split by comma to separate address, city, and state+zip
                        parts = [part.strip() for part in line.split(',')]

                        # First part should be the street address
                        if len(parts) >= 2:
                            record_data['Address'] = parts[0]
                            # Second part should be the city
                            if len(parts) >= 2:
                                record_data['City'] = parts[1].strip()
                            # Last part should contain MD and ZIP
                            if len(parts) >= 3:
                                last_part = parts[-1].strip()
                                if 'MD' in last_part:
                                    # Extract ZIP after MD
                                    zip_part = last_part.split('MD')[1].strip()
                                    zip_code = ''.join(filter(str.isdigit, zip_part))
                                    if len(zip_code) >= 5:
                                        record_data['Zip'] = zip_code[:5]

                if record_data['Address']:
                    all_data.append(record_data)
                    print(f"Processed {county_name} Sale Item #{i}")

        except Exception as e:
            print(f"Error processing section: {str(e)}")
            continue

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

    # Export to Excel with timestamp
    output_path = rf"C:\Users\wally\Desktop\UJpwork\AuctonScraper\TideWaterAuctionsInfo_{timestamp}.xlsx"
    try:
        df.to_excel(output_path, index=False)
        print(f"\nData successfully exported to {output_path}")
    except PermissionError:
        alt_path = rf"C:\Users\wally\Desktop\UJpwork\AuctonScraper\TideWaterAuctionsInfo_new.xlsx"
        df.to_excel(alt_path, index=False)
        print(f"\nCouldn't write to original path. Data exported to {alt_path}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    # Restore original stdout
    sys.stdout = sys.__stdout__
    print(f"Log file saved to {log_path}")