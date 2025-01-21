import os
import json
import logging
import sys
from urllib.parse import urlencode

import requests

JSON_FILEPATH = "results.json"
API_BASE_URL = "http://localhost:8000"  # Replace with the actual base URL of the API
SAVE_EVERY = 10


def is_blacklisted(title: str, description: str, blacklist_keywords: list[str]) -> bool:
    """
    Returns True if any blacklisted substring appears in the title or description.
    """
    text = f"{title}\n{description}".lower()
    for kw in blacklist_keywords:
        if kw.lower() in text:  # partial match check
            return True
    return False


def setup_logger():
    """Configure root logger with a simple StreamHandler."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove all existing handlers
    while logger.handlers:
        logger.handlers.pop()

    # Create and add a simple stream handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # A simple log format
    formatter = logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)


def load_results(filepath=JSON_FILEPATH) -> dict:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return dict()


def save_results(data: dict, filepath=JSON_FILEPATH):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)


def fetch_urls_from_api(query, location, radius, min_price, max_price, page_count):
    params = {
        "query": query,
        "location": location,
        "radius": radius,
        "min_price": min_price,
        "max_price": max_price,
        "page_count": page_count,
    }
    url = f"{API_BASE_URL}/inserate" + ("?" + urlencode(params) if params else "")
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def fetch_details_from_api(inserat_id):
    response = requests.get(f"{API_BASE_URL}/inserat/{inserat_id}")
    response.raise_for_status()
    return response.json()


def scrape_and_filter_pages(
    query: str,
    location: str,
    radius: str = "5",
    min_price: int = None,
    max_price: int = None,
    page_count: int = 1,
    blacklist_keywords=None
) -> dict:
    """
    Scrapes data using the API.
    """
    if blacklist_keywords is None:
        blacklist_keywords = []

    db = load_results(JSON_FILEPATH)
    new_processed_total = []
    blacklisted_total = []

    try:
        # Fetch URLs using the API
        logging.info('Fetching URLs...')
        listings_response = fetch_urls_from_api(
            query=query,
            location=location,
            radius=radius,
            min_price=min_price,
            max_price=max_price,
            page_count=page_count
        )

        if not listings_response or not listings_response["success"]:
            logging.error(f"No URLs returned.")
            raise

        data_list = listings_response["data"]

        # Process each URL
        for idx, data in enumerate(data_list):
            data_id = data["adid"]
            data_url = data["url"]
            logging.debug(f'Fetching details from {data_id}')
            if data_id in db:
                logging.info(f"Skipping already-processed ad: {data_id}")
                continue

            # Fetch details using the API
            try:
                details = fetch_details_from_api(data_id)
            except Exception as e:
                logging.error(f"Error fetching details for ID {data_id}: {e}")
                db[data_id] = {"failed": True, "blacklisted": False}
                continue

            if details is None or not details["success"]:
                db[data_id] = {"failed": True, "blacklisted": False}
                continue

            # Check blacklist
            data = details["data"]
            title = data.get("title", "")
            desc = data.get("description", "")
            blacklisted = is_blacklisted(title, desc, blacklist_keywords)
            data["blacklisted"] = blacklisted

            # Add final keys
            data["failed"] = False
            data["url"] = data_url

            # Finally add entry to the loaded db
            db[data_id] = data

            if blacklisted:
                blacklisted_total.append(details)
            else:
                new_processed_total.append(details)

            # Save results after each page
            if idx > 0 and idx % SAVE_EVERY == 0:
                save_results(db, JSON_FILEPATH)
                logging.info(f"Iteration #{idx}. Results saved to {JSON_FILEPATH}")

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt caught. Saving partial results before exiting.")
        save_results(db, JSON_FILEPATH)
        sys.exit(1)
    except Exception as e:
        logging.info(f"Exception caught: {e}. Saving partial results before exiting.")
        save_results(db, JSON_FILEPATH)
        sys.exit(1)

    return {
        "new_processed": new_processed_total,
        "blacklisted": blacklisted_total,
        "results_json_file": JSON_FILEPATH
    }


if __name__ == "__main__":
    setup_logger()

    summary = scrape_and_filter_pages(
        query="fahrrad",
        location="80804",
        radius="10",
        min_price=100,
        max_price=400,
        page_count=1,
        blacklist_keywords=['renn', 'dame', 'jugen', 'mädchen', 'kind', "elektri"]
    )

    # Final summary
    print("\nDone scraping!")
    print(f"Newly processed ads: {len(summary['new_processed'])}")
    print(f"Blacklisted ads: {len(summary['blacklisted'])}")
    print(f"Results saved to: {summary['results_json_file']}")
