# Web Scraper

This is a Python script for scraping email addresses from web pages based on a Google Custom Search. It provides a graphical user interface (GUI) for configuring the search and extraction settings.

## Configuration

Before running the script, you need to configure the following settings:

### API Key and CSE ID

To use Google Custom Search, you'll need an API Key and a Custom Search Engine (CSE) ID. You can obtain these by following these steps:

1. Go to the [Google Developers Console.]([https://website-name.com](https://developers.google.com/custom-search/v1/overview?csw=1))
3. Create a new project or select an existing one.
4. In the project dashboard, go to "APIs & Services" > "Library."
5. Search for "Custom Search API" and enable it for your project.
6. In the left sidebar, click on "Credentials" and create a new API Key.
7. Copy the API Key and use it as the "API Key" in the script's GUI.
8. Next, create a Custom Search Engine by going to [Google Custom Search]([https://website-name.com](https://programmablesearchengine.google.com)) and following the setup instructions.
9. Once your CSE is created, you'll find the CSE ID in the control panel. Use this as the "CSE ID" in the script's GUI.

### Query and Keywords

- **Query**: Enter the search query you want to use for searching web pages.
- **Keywords**: Specify a comma-separated list of keywords that the script will use to filter the extracted email addresses.

### Total Pages to Visit

Specify the total number of Google search result pages to visit during the scraping process.

### Desired TLD

Enter the desired top-level domain (TLD) that you want to match when fetching websites. For example, ".com" or ".org."

## Installation

1. Clone this repository or download the script.

2. Create a virtual environment (optional but recommended).

3. Install the required packages using pip:

```pip3 install -r requirements.txt```


## Running the Script

1. After configuring the settings, run the script by executing the following command:

```python3 script.py```

2. The GUI will open, and you can click the "Start Scraping" button to begin the email scraping process.

3. The script will display progress and results in the GUI window. Extracted email addresses will be saved to a file named "result.csv" in the script's directory.

4. The script will also print the sub-websites (URLs) that are fetched during the process.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
