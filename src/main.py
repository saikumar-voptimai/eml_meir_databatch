from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from meir import MEIR
from helper_functions import load_config, load_variables, setup_logging
from pathlib import Path
import logging
import time

# Load configurations and setup logging
root_path = Path(__file__).resolve().parents[1]
config = load_config()

# download_dir = config.download.path
# chrome_options = Options()
# prefs = {
#     "download.default_directory": download_dir,
#     "download.prompt_for_download": False,
#     "directory_upgrade": True,
# }
# chrome_options.add_experimental_option("prefs", prefs)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

variables = load_variables()
setup_logging()
logger = logging.getLogger("DataExtraction")

logger.info(f"Started at - {time.time()}\n")

# Setup Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

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
