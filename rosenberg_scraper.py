import pandas as pd
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

    # Array to store the specified <td> values
    cell_values = []

    # Iterate through each row and get the specified <td> values
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) > 7:  # Ensure the row has at least 8 <td> elements
            cell_values.append((
                cells[0].text,  # 1st cell
                cells[1].text,  # 3rd cell
                cells[3].text,  # 4th cell
                cells[4].text,  # 5th cell
                cells[5].text,  # 6th cell
                cells[6].text,  # 7th cell
                cells[7].text   # 8th cell
            ))

    # Convert the array to a DataFrame
    df = pd.DataFrame(cell_values)

    # Export the DataFrame to an Excel file
    output_path = "C:\\Users\\wally\\Desktop\\UJpwork\\AuctonScraper\\RosenbergInfo.xlsx"
    df.to_excel(output_path, index=False)
   # print(f"Data exported to {output_path}")
finally:
    # Close the WebDriver
    driver.quit()