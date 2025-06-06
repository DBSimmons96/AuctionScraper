import pandas as pd
import openpyxl
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Create a log file with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_path = rf"C:\Users\wally\Desktop\UJpwork\AuctonScraper\HWest_log_{timestamp}.txt"

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

# Use ChromeDriverManager to automatically manage the driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # URL to scrape
    url = "https://rosenberg-assoc.com/foreclosure-sales/"
    driver.get(url)

    # Find the table with id="table_1"
    table = driver.find_element(By.ID, "table_1")
    rows = table.find_elements(By.TAG_NAME, "tr")
    cell_values = []

    # Iterate through each row
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) > 8:  # Ensure the row has enough cells
            # Only append if State is MD
            if cells[6].text.strip().upper() == "MD":
                cell_values.append((
                    cells[0].text,  # Case Number
                    cells[1].text,  # Sale Date
                    cells[2].text,  # Sale Time
                    cells[3].text,  # Property Address
                    cells[4].text,  # City
                    cells[5].text,  # Jurisdiction
                    cells[6].text,  # State
                    cells[7].text   # Opening Bid
                ))

    # Define column names
    column_names = [
        "Case Number",
        "Sale Date",
        "Sale Time",
        "Property Address",
        "City",
        "Jurisdiction",
        "State",
        "Opening Bid"
    ]

    # Convert the array to a DataFrame
    df = pd.DataFrame(cell_values, columns=column_names)

    # Export filtered data to Excel
    output_path = r"C:\Users\wally\Desktop\UJpwork\AuctonScraper\RosenbergInfo.xlsx"
    df.to_excel(output_path, index=False)
    print(f"Data exported to {output_path} (MD cases only)")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    # Restore original stdout
    sys.stdout = sys.__stdout__
    print(f"Log file saved to {log_path}")