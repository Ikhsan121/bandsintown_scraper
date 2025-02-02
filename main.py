from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json
from datetime import datetime
import re
from unidecode import unidecode
import logging
import sys
import os

folder_path = "./events"
os.makedirs(folder_path, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of log messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("./bandsintown_scraper_debug.log", mode='w')
    ]
)
def login():
    with sync_playwright() as p:
        logging.debug("Launching Chromium browser for login.")
        # Launch browser (set headless=False to see the browser)
        browser = p.chromium.launch(headless=False, args=["--disable-popup-blocking"])
        context = browser.new_context()
        page = context.new_page()

        logging.info(f"Navigating to URL: https://www.bandsintown.com/")
        page.goto("https://www.bandsintown.com/", wait_until="domcontentloaded")
        logging.debug("Page loaded. Waiting 1 minute for you to login.")
        login_selector = '.giKV2k3zxSZYNmnpwBrS'
        page.wait_for_selector(login_selector, timeout=10000)
        page.click(login_selector)

        email_selector = '.fNqlG1sOQFDVkTvNFeaY'
        page.wait_for_selector(email_selector, timeout=10000)
        page.fill("input[placeholder='Email Address']", "ikhsanarif211@gmail.com")

        continue_selector = '.aoFoUwmnmRmSIj1GmXNI'
        page.wait_for_selector(continue_selector, timeout=10000)
        page.click(continue_selector)
        # Wait for a post-login indicator
        logged_in_selector = ".eyHuQnCk289nZ7GD8U3B"
        page.wait_for_selector(logged_in_selector, timeout=60000)
        # Save cookies to a file
        context.storage_state(path="./cookies.json")
        browser.close()


def bandsintown_scraper(url, artist_name):
    logging.info("Starting Bandsintown scraper.")
    with sync_playwright() as p:
        logging.debug("Launching Chromium browser.")
        # Launch browser (set headless=False to see the browser)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="cookies.json")
        page = context.new_page()
        try:
            logging.info(f"Navigating to URL: {url}")
            page.goto(url, wait_until="domcontentloaded")
            logging.debug("Page loaded. Waiting for 'Show More details' button selector.")

            # click more info if available
            try:
                show_more_selector = ".OsDXzJEUtjxbMlCnPMsj"
                page.wait_for_selector(show_more_selector, timeout=10000)
                logging.debug("'Show More details' button found. Clicking the button.")
                page.click(show_more_selector)
            except PlaywrightTimeoutError as te:
                logging.error(f"Timeout error: {str(te)}")

            # Wait for events to load after clicking
            events_selector = ".TNgS3aApp6XIXOIqyEGQ"
            logging.debug(f"Waiting for events to load with selector: {events_selector}")
            page.wait_for_selector(events_selector, timeout=10000)
            
            all_events = page.query_selector_all(events_selector)
            # remove duplicate events
            unique_events = []
            seen_links = set()
            for event in all_events:
                # Get the <a> tag inside the event div
                link_element = event.query_selector("a")

                if link_element:
                    event_link = link_element.get_attribute("href")  # Extract href

                    if event_link and event_link not in seen_links:
                        seen_links.add(event_link)  # Store unique hrefs
                        unique_events.append(event)
            all_events = unique_events
            num_events = len(all_events)
            logging.info(f"Number of events found: {num_events}")

            if num_events == 0:
                logging.warning("No events found. Check if the selector is correct or if the page structure has changed.")

            artist_selector = ".sKZg4aYIueqDu5cAfZ_q"
            logging.debug(f"Fetching artist name using selector: {artist_selector}")
            artist_element = page.query_selector(artist_selector)
            if artist_element:
                artist = artist_element.inner_text()
                logging.info(f"Artist found: {artist}")
            else:
                logging.error("Artist element not found.")
                artist = "Unknown Artist"

            event_list = []
            for idx, event in enumerate(all_events, start=1):
                try:
                    logging.debug(f"Processing event {idx}/{num_events}.")
                    
                    month_selector = ".jnX2IOn9AGg9SfWK4eCL"
                    date_selector = ".vLfdQ0HSBUy47Eujeqkk"
                    venue_selector = ".TYzA8d85IfvLeyChcYJj"
                    location_selector = ".D9Nc3q2GrC4mEVUaPKoR"

                    month_element = event.query_selector(month_selector)
                    date_element = event.query_selector(date_selector)
                    venue_element = event.query_selector(venue_selector)
                    location_element = event.query_selector(location_selector)

                    if not all([month_element, date_element, venue_element, location_element]):
                        logging.warning(f"Missing one or more elements in event {idx}. Skipping this event.")
                        continue

                    month = month_element.inner_text().strip()
                    date = date_element.inner_text().strip()
                    venu = venue_element.inner_text().strip()
                    location = location_element.inner_text().strip()

                    logging.debug(f"Raw venue text: {venu}")
                    decoded_text = venu.encode("utf-8").decode("unicode_escape")
                    decoded_venu = unidecode(decoded_text)
                    logging.debug(f"Decoded venue: {decoded_venu}")

                    logging.debug(f"Raw location text: {location}")
                    if "," in location:
                        state, country = location.split(",", 1)
                        decoded_text = state.encode("utf-8").decode("unicode_escape")
                        decoded_state = unidecode(decoded_text)
                        logging.debug(f"Decoded state: {decoded_state.strip()}, Country: {country.strip()}")
                    else:
                        logging.warning(f"Location format unexpected in event {idx}: '{location}'. Skipping this event.")
                        continue

                    # Convert month and date to "YYYY-MM-DD" format
                    try:
                        event_date = datetime.strptime(f"{month} {date} 2025", "%b %d %Y").strftime("%Y-%m-%d")
                        logging.debug(f"Parsed event date: {event_date}")
                    except ValueError as ve:
                        logging.error(f"Date parsing error in event {idx}: {ve}. Skipping this event.")
                        continue

                    event_data = {
                        "artist": artist,
                        "start_date": event_date,
                        "end_date": event_date,
                        "venue": decoded_venu,
                        "city/state": decoded_state.strip(),
                        "country": country.strip()
                    }
                    event_list.append(event_data)
                    logging.info(f"Event {idx} added: {event_data}")

                except Exception as event_e:
                    logging.error(f"Error processing event {idx}: {str(event_e)}")
                    continue

            event_list = [dict(t) for t in {tuple(d.items()) for d in event_list}]
            logging.info(f"Total events collected: {len(event_list)}")

            with open(f'./events/events_{artist_name}.json', 'w', encoding='utf-8') as f:
                json.dump(event_list, f, indent=4, ensure_ascii=False)
                logging.info(f"Events successfully written to 'events_{artist_name}.json'.")

        except PlaywrightTimeoutError as te:
            logging.error(f"Timeout error: {str(te)}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
        finally:
            logging.debug("Closing browser.")
            browser.close()
            logging.info("Browser closed.")

def scrape_all_artists():
    # Open and read the JSON file
    with open("artists_database.json", "r") as file:
        data = json.load(file)
    links = [data[idx]['bands_in_url'] for idx, item in enumerate(data)]
    for link in links:
        name = link.split("/")[-1]
        name = re.sub(r'\d', '', name)  # Remove digits
        name = re.sub(r'-', '_', name).replace("_", " ").strip()
        bandsintown_scraper(link, artist_name=name)


if __name__ == "__main__":
    # check cookies
    file_path = './cookies.json'
    if os.path.exists(file_path):
        scrape_all_artists()
    else:
        login()
        scrape_all_artists()
