# EML MEIR Data Batch Extraction

## Project Overview

The EML MEIR Data Batch Extraction project automates the process of logging into the MEIR website, selecting a device, applying date ranges and variables, and exporting the data. This automation is achieved using Selenium, a powerful tool for web browser automation.

## Components

The project consists of three main components:

1. `main.py`
2. `helper_functions.py`
3. `meir.py`

### `main.py`

This is the entry point of the application. It initializes the Selenium WebDriver, loads configurations and variables, and orchestrates the overall workflow by invoking methods from the `MEIR` class.

### `helper_functions.py`

This module contains utility functions to load configurations and variables and set up logging.

- **Functions**:
  - `load_config()`: Loads the configuration from a YAML file.
  - `load_variables()`: Loads the list of variables from a text file.
  - `setup_logging()`: Sets up logging configuration.

### `meir.py`

This module defines the `MEIR` class, which contains methods to interact with the MEIR website. It includes methods for logging in, selecting a device, applying date ranges and variables, and other related actions.

## Selenium Usage

Selenium WebDriver is used to automate interactions with the web browser. The key steps where Selenium is used include:

1. **Initialization**: Setting up the WebDriver with specified options.
2. **Login**: Automating the login process by entering credentials and clicking the login button.
3. **Navigation**: Navigating through the MEIR interface to select devices and set date ranges.
4. **Form Interaction**: Entering variable names and applying filters to generate the desired data.

## Configuration File (`config.yml`)

The configuration file contains various properties required for the script to run. Below is a brief explanation of the configuration properties:

- `max_attempts`: Maximum number of attempts to enter text in the input fields.
- `login`: Credentials and element IDs for the login process.
  - `username`: Username for login.
  - `password`: Password for login.
  - `url`: URL of the MEIR login page.
  - `user_id`: ID of the username input field.
  - `pwd_id`: ID of the password input field.
  - `btn_login_id`: ID of the login button.
- `dates`: Date range settings and related element IDs.
  - `start_date`: Start date for data extraction.
  - `end_date`: End date for data extraction.
  - `delta_date`: Number of days to apply in each step.
  - `strt_date_id`: ID of the start date input field.
  - `end_date_id`: ID of the end date input field.
  - `btn_date_id`: ID of the apply date range button.
- `variables`: Variable settings.
  - `btn_apply_id`: ID of the apply button for plotting data.
- `wait_times`: Various wait times to handle asynchronous loading.
  - `popup_wait`: Time to wait for the popup to appear.
  - `UGML_wait`: Time to wait after selecting the device.
  - `variable_wait`: Time to wait after entering each variable.
  - `plot_sleep`: Time to wait after clicking the apply button.

## `MEIR` Class Logic

The `MEIR` class is responsible for automating the interactions with the MEIR website to download data. Here's a detailed breakdown of its methods and logic:

### Initialization

Initializes the `MEIR` object with necessary configurations, start and end dates, Selenium WebDriver, and service objects.

### Landing Login Page

Logs into the MEIR website by entering credentials and clicking the login button.

**Logic**:
- Navigates to the login URL.
- Finds the username, password fields, and login button using their IDs.
- Enters the username and password, then clicks the login button.
- Waits until the element with ID `lblDeviceName` is present to ensure the login is successful.

### Device Page

Selects the device from the popup on the MEIR page.

**Logic**:
- Waits until the device name element (`lblDeviceName`) is clickable.
- Attempts to click the device name. If the standard click fails, uses JavaScript to perform the click.
- Waits for the device selection confirmation and clicks the corresponding device element.

### Apply Dates

Applies the date ranges and variables, then clicks the Apply button to plot the data.

**Logic**:
- Iterates through the date ranges, setting the start and end dates for each range.
- For each set of dates, applies the variables in batches of six.
- Clicks the Apply button to plot the data.

### Set Date Range

Sets the date range in the MEIR page by clearing the existing values, entering new start and end dates, and pressing the TAB key to confirm.

### Apply Variables

Applies the variables to the MEIR page by entering variable names in the input fields.

**Logic**:
- Iterates through the input fields and variable names.
- Clears each input field, enters the variable name, and presses the TAB key to confirm.
- Repeats the process for the specified number of attempts in case of failure.

### Plot Apply

Clicks the Apply button to plot the data after setting the date range and applying the variables.

**Logic**:
- Finds the Apply button using its ID.
- Clicks the button using JavaScript to ensure the action is performed.
- Waits for a specified duration to allow the plot to be generated.

## Example Usage

1. **Setup**:
   - Ensure you have the necessary dependencies installed, including `selenium`, `webdriver_manager`, and `python-box`.

2. **Configuration**:
   - Edit the `config.yml` file with the appropriate values for your MEIR setup.

3. **Run the Script**:
   - Execute `main.py` to start the data extraction process.

```bash
python main.py