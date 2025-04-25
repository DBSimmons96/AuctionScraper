from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode

# Use ChromeDriverManager to automatically manage the driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # URL to scrape
    url = "https://rosenberg-assoc.com/foreclosure-sales/"

    # Open the URL
    driver.get(url)

    # Find the table with id="table_1"
    table = driver.find_element(By.ID, "table_1")

    # Get all <tr> elements within the table
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Array to store the 3rd and 4th <td> values
    cell_values = []

    # Iterate through each row and get the 3rd and 4th <td> values
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) > 3:  # Ensure the row has at least 4 <td> elements
            cell_values.append((cells[2].text, cells[3].text))  # Store as a tuple

    print(cell_values)
finally:
    # Close the WebDriver
    driver.quit()