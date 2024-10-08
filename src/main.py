from pathlib import Path
from selenium import webdriver
import logging
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from meir import MEIR
from helper_functions import load_config, load_variables, setup_logging

# Load configurations and setup logging
root_path = Path(__file__).resolve().parents[1]
config = load_config()

# Path to your chromedriver.exe
#chrome_driver_path = r'F:\PythonBase\EML Project\eml_meir_databatch\src\chromedriver.exe'
# Define the new download folder
#download_dir = config.file_handling.download_path
# Set up Chrome options
#chrome_options = webdriver.ChromeOptions()
#chrome_options.add_experimental_option("prefs", {
     #"download.default_directory": download_dir,  # Set download path
     #"download.prompt_for_download": False,  # Disable download prompt
     #"directory_upgrade": True
#})

# Use Service() to specify the path to chromedriver
#service = Service(executable_path=chrome_driver_path)

# Setup Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service = service) #options=chrome_options)

variables = load_variables()
setup_logging()
logger = logging.getLogger("DataExtraction")


logger.info(f"Started at - {time.time()}\n")

# Initialize MEIR instance
meir = MEIR(config, driver, service, logger)

# Perform the required operations
try:
    meir.landing_login_page()
    meir.device_page()
    meir.apply_dates(variables)
finally:
    # Close the driver
    driver.quit()
    logger.info(f"Finished at - {time.time()}\n")
