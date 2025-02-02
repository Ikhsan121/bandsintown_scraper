# Bandsintown Event Scraper

## Overview
This project is a **web scraper** built with **Playwright** that extracts event details from **Bandsintown**. It automates the login process, navigates to artist pages, collects event details, and saves the results in JSON format.

## Features
- **Automated Login**: Handles user authentication and stores session cookies.
- **Event Scraping**: Extracts event details such as date, venue, city, and country.
- **Duplicate Removal**: Ensures that events are unique.
- **Logging**: Provides detailed logs for debugging.
- **JSON Output**: Saves event data in structured JSON files.
- **Batch Processing**: Reads artist data from a database and scrapes events for multiple artists.

## Installation
### **1. Clone the Repository**
```sh
git clone https://github.com/yourusername/bandsintown-scraper.git
cd bandsintown-scraper
```

### **2. Install Dependencies**
Ensure you have **Python 3.8+** and **pip** installed. Then, install the required packages:
```sh
pip install -r requirements.txt
```

### **3. Install Playwright Browsers**
```sh
playwright install
```

## Usage
### **1. Prepare the Artists Database**
Create a JSON file named `artists_database.json` with a structure like this:
```json
[
    {"name": "Artist Name", "bands_in_url": "https://www.bandsintown.com/a/12345"},
    {"name": "Another Artist", "bands_in_url": "https://www.bandsintown.com/a/67890"}
]
```

### **2. Run the Scraper**
#### **First-time Login**
If you haven't logged in before, the scraper will ask you to log in manually:
```sh
python main.py
```
After login, it will save cookies for future use.

#### **Scraping Events for All Artists**
If cookies exist, the scraper will directly start scraping:
```sh
python main.py
```

#### **Combining JSON Files**
Once all events are scraped, you can merge them into a single JSON file using:
```sh
python combine_json.py
```

## Output
- Scraped events are saved in `./events/events_{artist_name}.json`.
- Logs are stored in `bandsintown_scraper_debug.log`.

## File Structure
```
├── main.py               # Main scraper script
├── combine_json.py       # Merges JSON files into one
├── artists_database.json # List of artists to scrape
├── events/               # Folder containing scraped event JSON files
├── cookies.json          # Saved session cookies
├── requirements.txt      # Dependencies
├── README.md             # Documentation
```

## Troubleshooting
### **1. No Events Found**
- Ensure the selectors (`.TNgS3aApp6XIXOIqyEGQ`, etc.) are still valid.
- The page structure might have changed. Update the scraper if necessary.

### **2. Playwright Timeout Errors**
- Check your internet connection.
- Try increasing the timeout in `page.wait_for_selector()`.

### **3. Login Issues**
- Delete `cookies.json` and re-run `python main.py` to log in again.

## License
This project is licensed under the **MIT License**.

## Author
Developed by **Ikhsan Arif**.

