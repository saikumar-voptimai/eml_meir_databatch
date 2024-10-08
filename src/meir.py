import os
import re
import pandas as pd
import time
from typing import List
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class MEIR:
    """
    MEIR class to interact with the MEIR webpage to download the data.
    """
    def __init__(self, config: dict, driver: webdriver.Chrome, service: Service, logger: logging.Logger) -> None:
        """
        Initialize the MEIR object with the start and end dates, the Selenium WebDriver, and the Service object.
        :param config: Configuration dictionary
        :param driver: Selenium WebDriver object
        :param service: Selenium Service object
        :return: None
        """
        self.config = config
        self.start_date = datetime.strptime(self.config.dates.start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(self.config.dates.end_date, "%Y-%m-%d")
        self.driver = driver
        self.service = service
        self.logger = logger

    def landing_login_page(self) -> None:
        """
        Perform login to the landing page.
        :return: None
        """
        self.logger.info("Navigating to the login page.")
        self.driver.get(self.config.login.url)        

        username_field = self.driver.find_element(By.ID, self.config.login.user_id)
        password_field = self.driver.find_element(By.ID, self.config.login.pwd_id)
        login_button = self.driver.find_element(By.ID, self.config.login.btn_login_id)
        
        username_field.send_keys(self.config.login.username)
        password_field.send_keys(self.config.login.password)
        login_button.click()

        self.logger.info("Logging in.")
        WebDriverWait(self.driver, self.config.wait_times.popup_wait).until(
            EC.presence_of_element_located((By.ID, "lblDeviceName"))
        )
        self.logger.info("Login successful.")

    def device_page(self) -> None:
        """
        Select the device from the popup.
        :return: None
        """
        self.logger.info("Navigating to the device page.")
        popup_button = WebDriverWait(self.driver, self.config.wait_times.popup_wait).until(
            EC.element_to_be_clickable((By.ID, "lblDeviceName"))
        )
        try:
            popup_button.click()
        except:
            self.driver.execute_script("arguments[0].click();", popup_button)
            self.logger.info("Clicked the device name using JavaScript.")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'UGML BF2 415V MCC~~TimeZone:India Standard Time')]"))
        )

        div_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'UGML BF2 415V MCC~~TimeZone:India Standard Time')]")
        div_element.click()
        self.logger.info("Selected the device.")
        time.sleep(self.config.wait_times.UGML_wait)

    def apply_dates(self, variables: List[str]) -> None:
        """
        Apply the dates and variables to the MEIR page, click on Apply for the chart and Download.
        :param variables: List of variables to apply
        :return: None
        """
        self.logger.info("Applying date ranges and variables.")
        current_start_date = self.start_date
        run = 0
        while current_start_date < self.end_date:
            current_end_date = min(current_start_date + timedelta(days=self.config.dates.delta_date), self.end_date)
            self.set_date_range(current_start_date, current_end_date)
            self.set_time_range(self.config.dates.start_time, self.config.dates.start_time)
            # TODO: Add time range using set_time_range function

            start_var = self.config.start_from.variable-1 if run == 0 else 0
            if self.config.end_at.variable == "end":
                self.config.end_at.variable = len(variables)
            end_var = self.config.end_at.variable if run == 0 else len(variables)
            for i in range(start_var, end_var, 6):
                selected_vars = variables[i:i+6] if i+6 <= len(variables) else variables[i:]
                self.apply_vars(selected_vars, self.config.max_attempts)
                self.plot_apply()
                self.data_download()
                self.file_rename(current_start_date, current_end_date, self.config.dates.start_time, self.config.dates.end_time, i, i+6)
            
                time.sleep(self.config.wait_times.download_wait)
            current_start_date = current_end_date # + timedelta(days=1)
            run += 1
            #TODO: Choose an appropriate time delay after implementing the time range
        self.logger.info("Completed applying date ranges and variables.")

    def set_date_range(self, start_date: datetime, end_date: datetime) -> None:
        """
        Set the date range in the MEIR page.
        :param start_date: Start date
        :param end_date: End date
        :return: None
        """
        date_start = self.driver.find_element(By.ID, self.config.dates.start_date_id)
        date_end = self.driver.find_element(By.ID, self.config.dates.end_date_id)

        self.driver.execute_script("arguments[0].value = '';", date_start)
        date_start.send_keys(start_date.strftime("%Y-%m-%d"))
        time.sleep(1)
        date_start.send_keys(Keys.TAB)

        self.driver.execute_script("arguments[0].value = '';", date_end)
        date_end.send_keys(end_date.strftime("%Y-%m-%d"))
        time.sleep(1)
        date_end.send_keys(Keys.TAB)
        self.logger.info(f"Set date range from {start_date} to {end_date}.")

    def set_time_range(self, start_time: str, end_time: str) -> None:
        """
        Set the time range in the MEIR page.
        :param start_time: Start time
        :param end_time: End time
        :return: None
        """
        start_time_field = self.driver.find_element(By.ID, self.config.dates.start_time_id)
        end_time_field = self.driver.find_element(By.ID, self.config.dates.end_time_id)

        self.driver.execute_script("arguments[0].value = '';", start_time_field)
        start_time_field.send_keys(start_time)
        time.sleep(1)
        start_time_field.send_keys(Keys.TAB)

        self.driver.execute_script("arguments[0].value = '';", end_time_field)
        end_time_field.send_keys(end_time)
        time.sleep(1)
        end_time_field.send_keys(Keys.TAB)
        self.logger.info(f"Set time range from {start_time} to {end_time}.")

    def apply_vars(self, variables: List[str], max_attempts: int = 1) -> None:
        """
        Apply the variables to the MEIR page.
        :param variables: List of variables to apply
        :param max_attempts: Maximum number of attempts to enter text in the field
        :return: None
        """
        input_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[id='txtVariables']")
        for input_field, variable_name in zip(input_fields, variables):
            self.clear_and_send_keys(input_field, variable_name, max_attempts)

    def clear_and_send_keys(self, element: webdriver.remote.webelement.WebElement, text: str, max_attempts: int) -> None:
        """
        Clear the input field and send the variable key as 'text' and press 'TAB'.
        :param element: Input field element in the webpage
        :param text: Variable name to enter
        :param max_attempts: Maximum number of attempts to enter variable name in the field
        :return: None
        """
        for attempt in range(max_attempts):
            try:
                self.driver.execute_script("arguments[0].value = '';", element)
                element.send_keys(text)
                time.sleep(self.config.wait_times.variable_wait)
                element.send_keys(Keys.TAB)
                time.sleep(self.config.wait_times.variable_wait)
                self.logger.info(f"Entered variable '{text}' in the field.")
                return
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for variable '{text}': {e}")
                time.sleep(1)

    def plot_apply(self) -> None:
        """
        Click the Apply button to plot the data.
        :return: None
        """
        apply_button = self.driver.find_element(By.ID, self.config.variables.btn_apply_id)
        self.driver.execute_script("arguments[0].click();", apply_button)
        time.sleep(self.config.wait_times.plot_wait)
        self.logger.info("Clicked the Apply button.")

    def data_download(self) -> None:
        """
        Click the Export button to download the data.
        :return: None
        """
        self.logger.info("Clicking the Export button.")
        apply_button = self.driver.find_element(By.ID, self.config.variables.dwnld_btn_id)
        self.driver.execute_script("arguments[0].click();", apply_button)
        time.sleep(self.config.wait_times.download_wait)
        #TODO: Add code to check the download status, file size, and download completion
        self.logger.info("Clicked the Export button.")

    def file_rename(self, start_date: datetime, end_date: datetime, start_time: str, end_time: str, start_var: int, end_var: int) -> None:
        """
        Rename the downloaded file to the specified format.
        :param start_date: Start date of the range
        :param end_date: End date of the range
        :param start_time: Start time of the range
        :param end_time: End time of the range
        :param start_var: Starting index of the variables set
        :param end_var: Ending index of the variables set
        :return: None
        """
        self.logger.info("Renaming the downloaded File.")

        start_var_index = start_var + 1
        end_var_index = min(end_var, start_var_index + 5)
        
        new_filename = f"{start_date.strftime('%Y-%m-%d')} {start_time} To {end_date.strftime('%Y-%m-%d')} {end_time} For {start_var_index}To{end_var_index}Vars.xls"
        
        # Replace invalid characters for Windows filenames with an underscore or a valid character
        cleaned_filename = re.sub(r'[<>:"/\\|?*]', '-', new_filename)
        download_dir = self.config.file_handling.download_path
        downloaded_files = os.listdir(download_dir)
        downloaded_files = [f for f in downloaded_files if f.endswith('.xls')]
        downloaded_files.sort(key=lambda x: os.path.getctime(os.path.join(download_dir, x)), reverse=True)
        
        # Assume the latest file is the one just downloaded
        latest_file = os.path.join(download_dir, downloaded_files[0]) if downloaded_files else None
        
        if latest_file:
            new_filepath = os.path.join(download_dir, cleaned_filename)
            os.rename(latest_file, new_filepath)
            self.logger.info(f"Renamed file to: {new_filepath}")
        else:
            self.logger.warning("No downloaded file found to rename.")

    def files_club(self) -> None:
        """
        Combine all the files into a single file and store it in a specified location.
        Delete the original files afterward.
        :return: None
        """
        # Path to the download directory and output directory
        download_dir = self.config.download.path
        output_dir = self.config.output.path
        
        # List all the renamed files in the download directory
        downloaded_files = [f for f in os.listdir(download_dir) if f.endswith('.txt')]

        if not downloaded_files:
            self.logger.warning("No files found to combine.")
            return

        # Create a DataFrame list for combining
        combined_df = pd.DataFrame()

        for file_name in downloaded_files:
            file_path = os.path.join(download_dir, file_name)
            # Read the file content (assumed to be in text or tabular format)
            df = pd.read_csv(file_path, delimiter='\t')  # Adjust delimiter if necessary
            combined_df = pd.concat([combined_df, df], axis=1)  # Combine column-wise
        
        # Generate the final combined file name
        if combined_df.empty:
            self.logger.warning("No data to combine.")
            return

        # Assuming the start and end dates are the same across all files
        first_file = downloaded_files[0]
        start_date, start_time = first_file.split(' ')[0], first_file.split(' ')[1]
        last_file = downloaded_files[-1]
        end_date, end_time = last_file.split(' ')[4], last_file.split(' ')[5]

        combined_filename = f"{start_date} {start_time} To {end_date} {end_time} For AllVars.txt"
        combined_filepath = os.path.join(output_dir, combined_filename)

        # Save the combined file to the specified location
        combined_df.to_csv(combined_filepath, sep='\t', index=False)
        self.logger.info(f"Combined file saved as: {combined_filepath}")
        
        # Delete original files
        for file_name in downloaded_files:
            file_path = os.path.join(download_dir, file_name)
            os.remove(file_path)
        
        self.logger.info(f"Deleted original downloaded files after combining.")