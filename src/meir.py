from box import Box
from datetime import datetime, timedelta
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

import time
import yaml

# Load configuration from config.yml
root_path = Path(__file__).resolve().parents[1]

with open(root_path / "stave_proj" / "config.yml", "r") as file:
    config = yaml.safe_load(file)

# Convert the dictionary to a Box object
config = Box(config)

with open(root_path / "stave_proj" / "variables_load.txt", "r") as file:
    lines = file.readlines()

variables = []
for line in lines:
    variables.append(line.strip())

start_date = datetime.strptime(config.dates.start_date, "%Y-%m-%d")
end_date = datetime.strptime(config.dates.end_date, "%Y-%m-%d")

# Setup Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

def clear_and_send_keys(element, text):
    max_attempts = config.max_attempts
    attempts = 0
    while attempts < max_attempts:
        try:
            driver.execute_script("arguments[0].value = '';", element)
            element.send_keys(text)
            time.sleep(1)  # Wait for autocomplete suggestions
            element.send_keys(Keys.TAB)  # Simulate pressing the Tab key
            return
        except Exception as e:
            attempts += 1
            if attempts < max_attempts:
                element = driver.find_elements(By.CSS_SELECTOR, "input[id='txtVariables']")[variables.index(text)]
            else:
                print(f"Failed to enter text into the field: {e}")
                raise

def set_date_range(start_date, end_date):
    date_start = driver.find_element(By.ID, "PageContentHolder_calendarSelect")
    date_end = driver.find_element(By.ID, "PageContentHolder_calendarSelectEnd")
    apply_button = driver.find_element(By.ID, "PageContentHolder_btnApplyChanges")

    driver.execute_script("arguments[0].value = '';", date_start)
    date_start.send_keys(start_date.strftime("%Y-%m-%d"))
    time.sleep(1)
    date_start.send_keys(Keys.TAB)  # Use Tab key instead of Return

    driver.execute_script("arguments[0].value = '';", date_end)
    date_end.send_keys(end_date.strftime("%Y-%m-%d"))
    time.sleep(1)
    date_end.send_keys(Keys.TAB)  # Use Tab key instead of Return

    apply_button = driver.find_element(By.ID, "PageContentHolder_btnApplyChanges")
    driver.execute_script("arguments[0].click();", apply_button)
    time.sleep(15)  # Allow time for the data to load

# Open the web page
driver.get(config.login.url)

# Perform login
username = driver.find_element(By.ID, config.login.user_id)
password = driver.find_element(By.ID, config.login.pwd_id)
login_button = driver.find_element(By.ID, config.login.btn_login_id)

username.send_keys(config.login.username)  # Replace with actual username
password.send_keys(config.login.password)  # Replace with actual password
login_button.click()

# Wait for navigation to the intermediate page
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "lblDeviceName"))
)

# Click the span element to open the popup
popup_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "lblDeviceName"))
)

# Attempt to click the button
try:
    popup_button.click()
except:
    driver.execute_script("arguments[0].click();", popup_button)

# Wait for the UI widget to be interactable
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'UGML BF2 415V MCC~~TimeZone:India Standard Time')]"))
)

# Click the div element inside the UI widget
div_element = driver.find_element(By.XPATH, "//div[contains(text(), 'UGML BF2 415V MCC~~TimeZone:India Standard Time')]")
div_element.click()

time.sleep(10)

# Loop over each week in the date range
current_start_date = start_date
while current_start_date < end_date:
    current_end_date = min(current_start_date + timedelta(days=int(config.dates.delta_date)), end_date)

    # Set the date range for the current week
    set_date_range(current_start_date, current_end_date)

    # Locate all input fields (assuming they are in the same container)
    input_fields = driver.find_elements(By.CSS_SELECTOR, "input[id='txtVariables']")

    # Fill each input field with the corresponding variable name
    for input_field, variable_name in zip(input_fields, variables):
        clear_and_send_keys(input_field, variable_name)

    # Locate the apply button again to avoid stale element reference
    apply_button = driver.find_element(By.ID, "PageContentHolder_btnApplyChanges")
    driver.execute_script("arguments[0].click();", apply_button)

    # Allow time for the data to load and capture it if needed
    time.sleep(15)

    # Move to the next week
    current_start_date = current_end_date + timedelta(days=1)

# Close the driver
driver.quit()