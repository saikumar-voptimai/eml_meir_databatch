from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from meir import MEIR
from helper_functions import load_config, load_variables, setup_logging
import logging
import time

# Load configurations and setup logging
config = load_config()
variables = load_variables()
setup_logging()
logger = logging.getLogger("DataExtraction")

logger.info(f"Started at - {time.time()}\n")

# Setup Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Initialize MEIR instance
meir = MEIR(config, driver, service)

# Perform the required operations
try:
    meir.landing_login_page()
    meir.device_page()
    meir.apply_dates(variables)
finally:
    # Close the driver
    driver.quit()
    logger.info(f"Finished at - {time.time()}\n")
