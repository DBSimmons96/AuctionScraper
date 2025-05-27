import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import sys
from datetime import datetime

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")

# Use ChromeDriverManager to automatically manage the driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


# Create a log file with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_path = rf"C:\Users\wally\Desktop\UJpwork\AuctonScraper\AlexCooper_log_{timestamp}.txt"

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

try:
    # URL to scrape
    url = "https://realestate.alexcooper.com/foreclosures"
    driver.get(url)

    print("Scraping active foreclosure listings...\n")

    # Find all foreclosure container elements
    containers = driver.find_elements(By.CLASS_NAME, "alexcooper-foreclosure-container")

    # List to store all records
    all_data = []

    # Process each container
    for i, container in enumerate(containers, 1):
        # Check if the container has a cancelled div
        cancelled_div = container.find_elements(By.CLASS_NAME, "foreclosure-lot.cancelled")

        # Only process if the listing is not cancelled
        if not cancelled_div:
            text = container.text
            parts = text.split(',')

            # Initialize record dictionary with empty values
            record_data = {
                'County': '',
                'Address': '',
                'City': '',
                'State': 'MD',  # Default to MD
                'Zip': '',
                'Auction Date': '',
                'Auction Time': '',
                'Owner First Name': '',
                'Owner Last Name': '',
                'Owner Address': '',
                'Owner City': '',
                'Owner State': '',
                'Owner Zip': '',
                'Auction Website': 'alexcooper.com',
                'Notes': '',
                'Listing': text  # Store full listing text
            }

            # Parse address and location info
            if len(parts) >= 2:
                address = parts[0].strip()

                # Extract time if present using regex
                time_pattern = r'\d{1,2}:\d{2}\s*[AaPp][Mm]'
                time_match = re.search(time_pattern, address)

                if time_match:
                    # Extract the time
                    auction_time = time_match.group()
                    # Remove the time from address
                    address = re.sub(time_pattern, '', address).strip()
                    record_data['Auction Time'] = auction_time

                record_data['Address'] = address

                if 'Maryland' in text:
                    # Extract ZIP code after Maryland
                    md_parts = text.split('Maryland')
                    if len(md_parts) > 1:
                        zip_part = md_parts[1].strip()
                        record_data['Zip'] = zip_part.strip(' ,')

                # Try to extract city
                for part in parts:
                    part = part.strip()
                    if 'Maryland' in part:
                        city_part = part.split('Maryland')[0].strip()
                        record_data['City'] = city_part

            all_data.append(record_data)
            print(f"Processed Active Listing #{i}")

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Reorder columns according to specified order
    columns = [
        'County', 'Address', 'City', 'State', 'Zip',
        'Auction Date', 'Auction Time',
        'Owner First Name', 'Owner Last Name',
        'Owner Address', 'Owner City', 'Owner State', 'Owner Zip',
        'Auction Website', 'Notes', 'Listing'
    ]
    df = df[columns]

    def clean_county_from_address(row):
        address = row['Address']
        if 'county' in address.lower():
            # Split by 'county' (case insensitive)
            parts = re.split('county', address, flags=re.IGNORECASE)
            if len(parts) > 1:
                # Get county name (everything before 'county')
                county = parts[0].strip()
                # Get remaining address (everything after 'county')
                clean_address = parts[1].strip(' .,')
                return pd.Series([county, clean_address])
        return pd.Series([row['County'], row['Address']])


    # Apply the cleaning function and update both columns
    df[['County', 'Address']] = df.apply(clean_county_from_address, axis=1)


    def extract_auction_date(row):
        address = row['Address']
        # List of month names for pattern matching
        months = "January|February|March|April|May|June|July|August|September|October|November|December"

        if '|' in address:
            parts = address.split('|')
            # Look for date pattern in each part
            for part in parts:
                # Match month name followed by day
                date_pattern = f"({months})\s+(\d{{1,2}})"
                match = re.search(date_pattern, part.strip(), re.IGNORECASE)
                if match:
                    # Extract the date
                    auction_date = match.group().strip()
                    # Remove the date from address
                    clean_address = address.replace(part, '').replace('|', '').strip()
                    return pd.Series([auction_date, clean_address])

        return pd.Series([row['Auction Date'], row['Address']])


    # Apply both cleaning functions in sequence
    df[['County', 'Address']] = df.apply(clean_county_from_address, axis=1)
    df[['Auction Date', 'Address']] = df.apply(extract_auction_date, axis=1)

    # Export to Excel
    output_path = r"C:\Users\wally\Desktop\UJpwork\AuctonScraper\AlexCooperInfo.xlsx"
    df.to_excel(output_path, index=False)
    print(f"\nData successfully exported to {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    # Restore original stdout
    sys.stdout = sys.__stdout__
    print(f"Log file saved to {log_path}")