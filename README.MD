# Kleinanzeigen Scraper API

A FastAPI-based application for scraping and viewing eBay Kleinanzeigen ads.

## Features

- **Ad Scraping**: Scrape detailed ad data from eBay Kleinanzeigen.
- **API Endpoints**:
  - `GET /inserate`: Fetch multiple ads based on query parameters.
  - `GET /inserat/{id}`: Fetch detailed information about a specific ad.
- **Streamlit UI**: Visualize scraped results in an interactive dashboard.
- **Blacklist Filtering**: Automatically filter ads based on keywords.

## Installation

1. Clone the repository:
   ```bash
    git clone https://github.com/kobiche/ebay-kleinanzeigen-api
    cd kleinanzeigen-scraper
   ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the API:
    ```bash
    uvicorn main:app --reload
   ```
   
4. (Optional) use the `scrape_runner.py` to automatically scrape the website for custom listings, 
and save the results in JSON format
    ```bash
   python utils/scraper_runner.py
   ```
   
5. (Optional) Start the Streamlit dashboard to visualize the JSON file:
    ```bash
   streamlit run utils/streamlit_results.py
   ```
   
## API Endpoints

#### 1. Fetch Listings
**Endpoint:** `GET /inserate`

**Description:** Retrieves a list of listings based on search criteria.

##### Query Parameters:
- **`query`** *(string, optional)*: The search term (e.g., "fahrrad" to search for bicycles).
- **`location`** *(string, optional)*: The location or postal code to narrow the search (e.g., `10178` for Berlin).
- **`radius`** *(integer, optional)*: The search radius in kilometers from the specified location (e.g., `5` for a 5 km radius).
- **`min_price`** *(integer, optional)*: The minimum price in Euros for the listings (e.g., `200` for at least 200 Euros).
- **`max_price`** *(integer, optional)*: The maximum price in Euros for the listings (e.g., `500` for at most 500 Euros).
- **`page_count`** *(integer, optional)*: The number of pages to search or return (e.g., `5` for the first 5 pages, default is 1, max: 20 pages).

##### Example Request:
```http
GET /inserate?query=fahrrad&location=10178&radius=5&min_price=200&page_count=5
```

#### 2. Fetch Listing Details
**Endpoint:** `GET /inserat/{id}`

**Description:** Retrieves detailed information about a specific listing.

##### Path Parameters:
- **`id`** *(string)*: The unique identifier of the listing to fetch details for.

##### Example Request:
```http
GET /inserat/12345
```


### Documentation

#### API Response Format
All API endpoints return responses in the following JSON format:
```json
{
  "success": true,
  "data": [
    ...
  ]
}
```

API documentation is available at `http://localhost:8000/docs` when running locally.

## License
Distributed under the MIT License. See `LICENSE` for more information.
