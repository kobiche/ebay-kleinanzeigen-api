import streamlit as st
import json
import os


# Define the path to the JSON results file
JSON_FILEPATH = "results.json"


def load_results(filepath=JSON_FILEPATH):
    """Load the JSON data from the specified filepath."""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return dict()


# Streamlit UI
st.title("eBay Kleinanzeigen Scraper Results Viewer")

# Create a radio button selection for filtering options
filter_option = st.radio(
    "Select which ads to view:",
    ("Blacklisted", "Not Blacklisted", "All")
)

# Load data once at startup
data = load_results()

# Filter processed ads based on selection
processed_ads = dict(sorted(
    data.items(),
    key=lambda item: item[1].get("upload_date", ""),
    reverse=True  # change to False for ascending order
))

# Option to display as JSON text or more structured view
view_format = st.selectbox("Choose display format:", ["Table", "Raw JSON"])

show_images = st.toggle("Show images")

if show_images:
    column_order = ("title", "blacklisted", "price", "url", "location", "description", "upload_date", "images")
else:
    column_order = ("title", "blacklisted", "price", "url", "location", "description", "upload_date")

if view_format == "Raw JSON":
    st.json(processed_ads)
else:
    # Convert to list of dicts for tabular display
    table_data = []
    for _, details in processed_ads.items():
        entry = {}
        details["location"] = details["location"]["city"].strip()
        details["title"] = details["title"].strip()
        details["price"] = details["price"]["amount"]
        details["images"] = details["images"][0] if show_images and details.get("images", []) else None
        entry.update(details)
        table_data.append(entry)
    st.dataframe(table_data,
                 column_order=column_order,
                 column_config={
                     "title": st.column_config.TextColumn(pinned=True),
                     "upload_date": st.column_config.DateColumn(),
                     "url": st.column_config.LinkColumn("URL",
                                                        validate=r"^https://[a-z]+\.streamlit\.app$",
                                                        max_chars=20),
                     "blacklisted": st.column_config.CheckboxColumn(),
                     "price": st.column_config.NumberColumn("Price in EUR"),
                     "location": st.column_config.TextColumn("Location", width="medium"),
                     "images": st.column_config.ImageColumn("Preview image")
                 },
                 hide_index=True,
                 )
