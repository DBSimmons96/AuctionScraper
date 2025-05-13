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

    # Create a list to store all data
    all_data = []

    # Wait for records to be present
    wait = WebDriverWait(driver, 10)
    records = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "record")))

    for i, record in enumerate(records, 1):
        print(f"Record #{i}")
        print("=" * 50)

        # Find all forecol elements within this record
        forecols = record.find_elements(By.CLASS_NAME, "forecol")

        # Initialize empty data dictionary for each record
        record_data = {
            'County': '',
            'Address': '',
            'City': '',
            'State': 'MD',  # Default to MD since it's Maryland foreclosures
            'Zip': '',
            'Auction Date': '',
            'Auction Time': '',
            'Owner First Name': '',
            'Owner Last Name': '',
            'Owner Address': '',
            'Owner City': '',
            'Owner State': '',
            'Owner Zip': '',
            'Auction Website': 'brockandscott.com',
            'Notes': '',
            'Listing': ''
        }

        # Inside the forecols loop, modify the address parsing section:
        for forecol in forecols:
            text = forecol.text.strip()
            if text:
                print(text)
                if "Case No." in text:
                    record_data['Notes'] = text
                elif any(word in text.lower() for word in
                             ['street', 'road', 'avenue', 'lane', 'drive', 'court', 'ct', 'way', 'circle', 'cir',
                              'point', 'rd', 'ave', 'ln', 'dr', 'st', 'place', 'pl', 'terrace', 'ter', 'boulevard',
                              'blvd', 'highway', 'hwy']):
                    # Handle address as before
                    clean_address = text.replace("Address:", "").strip()
                    record_data['Address'] = clean_address
                    if "Maryland" in clean_address:
                        zip_part = clean_address.split("Maryland", 1)[1].strip()
                        record_data['Zip'] = zip_part.strip(' ,')
                elif "County:" in text:
                    # Extract county name by removing "County:" and any extra whitespace
                    county = text.replace("County:", "").strip()
                    record_data['County'] = county
                elif "Sale Date:" in text:
                    # Rest of your existing code...
                    sale_info = text.replace("Sale Date:", "").strip()
                    if " - " in sale_info:
                        date_part, time_part = sale_info.split(" - ")
                        record_data['Auction Date'] = date_part.strip()
                        record_data['Auction Time'] = time_part.strip()
                    else:
                        record_data['Auction Date'] = sale_info
                        record_data['Auction Time'] = ''
                elif "LOCATION:" in text:
                    record_data['Listing'] = text

        print("-" * 50 + "\n")
        all_data.append(record_data)

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



    # Export to Excel
    output_path = r"C:\Users\wally\Desktop\UJpwork\AuctonScraper\BrockAndScottInfo.xlsx"
    df.to_excel(output_path, index=False)
    print(f"\nData successfully exported to {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()