# insert_restaurant_and_menu.py

from bs4 import BeautifulSoup
import requests
import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import random

load_dotenv()

DATABASE_URL = "postgresql://ha2616:489057@34.148.223.31/proj1part2"
engine = create_engine(DATABASE_URL)

GOOGLE_API_KEY ="AIzaSyCSY5_TUiAAwGAEhDW3bu_Y3hisQJvJu2A"

class GooglePlacesAPIHandler:
    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        self.search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    def get_restaurant_info_by_name(self, name, location="New York"):
        search_query = f"{name} restaurant {location}"
        search_params = {"query": search_query, "key": self.api_key}

        response = requests.get(self.search_url, params=search_params)
        if response.status_code != 200:
            return None

        search_results = response.json().get("results", [])
        if not search_results:
            return None

        top_result = search_results[0]
        place_id = top_result.get("place_id")

        details_params = {
            "place_id": place_id,
            "fields": "name,formatted_address,geometry,photos,rating,price_level,website,formatted_phone_number,opening_hours",
            "key": self.api_key,
        }

        details_response = requests.get(self.details_url, params=details_params)
        if details_response.status_code != 200:
            return None

        details = details_response.json().get("result", {})
        photo_ref = top_result.get("photos", [{}])[0].get("photo_reference", "")
        image_url = (
            f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={self.api_key}"
            if photo_ref else None
        )

        return {
            "name": details.get("name"),
            "location": details.get("formatted_address"),
            "website": details.get("website"),
            "phone_number": details.get("formatted_phone_number"),
            "hours": ", ".join(details.get("opening_hours", {}).get("weekday_text", [])) if details.get("opening_hours") else None,
            "rating": details.get("rating"),
            "price_range": details.get("price_level", "N/A"),
            "image": image_url,
        }

def scrape_menu_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None, []

    soup = BeautifulSoup(response.text, "html.parser")
    name_div = soup.find("h1", class_="header__restaurant-name")
    restaurant_name = name_div.text.strip() if name_div else None

    menu_items = []
    item_tags = soup.find_all("a", class_="menu-item__title-link")
    for item in item_tags[:5]:
        menu_items.append(item.text.strip())

    return restaurant_name, menu_items

def get_category_id_for_item(item_name):
    name = item_name.lower()

    if any(word in name for word in ["salmon", "tuna", "shrimp", "lobster", "crab", "sashimi", "seafood", "clam"]):
        return 1  # Seafood
    if any(word in name for word in ["salad"]):
        return 2  # Salads
    if any(word in name for word in ["cake", "pudding", "dessert", "cookie", "brownie", "lava", "cheesecake"]):
        return 3  # Desserts
    if any(word in name for word in ["naan", "toast", "bread", "pastry", "bagel"]):
        return 4  # Breads & Pastries
    if any(word in name for word in ["juice", "smoothie", "soda", "wine", "coffee", "tea", "latte", "drink", "lassi"]):
        return 5  # Beverages
    if any(word in name for word in ["taco", "burrito", "guacamole", "quesadilla", "nachos"]):
        return 6  # Mexican Cuisine
    if any(word in name for word in ["steak", "burger", "grilled", "ribs", "ribeye", "meat"]):
        return 7  # Steaks & Grilled Meats
    if any(word in name for word in ["pasta", "pizza", "carbonara", "spaghetti"]):
        return 8  # Pasta & Italian Dishes
    if any(word in name for word in ["pancake", "waffle", "egg", "bacon", "breakfast", "benedict"]):
        return 9  # Breakfast Items
    if any(word in name for word in ["fries", "side", "potato", "coleslaw", "mac and cheese"]):
        return 10  # Side Dishes

    return 10  # Default to Side Dishes if unsure


def insert_restaurant_and_menu(url):
    restaurant_name, menu_items = scrape_menu_page(url)
    if not restaurant_name or not menu_items:
        return "Failed to extract menu or restaurant name."

    print(f'restaurant name: {restaurant_name}')
    print(f'menu items: {menu_items}')
    api = GooglePlacesAPIHandler()
    restaurant_data = api.get_restaurant_info_by_name(restaurant_name)

    if not restaurant_data:
        return f"No Google Places match found for {restaurant_name}."

    with engine.begin() as conn:
        insert_restaurant = """
        INSERT INTO restaurant (name, location, website, phone_number, hours, rating, price_range, image)
        VALUES (:name, :location, :website, :phone_number, :hours, :rating, :price_range, :image)
        RETURNING restaurant_id;
        """
        result = conn.execute(text(insert_restaurant), restaurant_data)
        restaurant_id = result.scalar()

        for item in menu_items:
            category_id = get_category_id_for_item(item)

            insert_food = """
            INSERT INTO food_item (category_id, name, nutritional_info, num_ratings, restaurant_id)
            VALUES (:category_id, :name, :nutritional_info, :num_ratings, :restaurant_id)
            RETURNING food_item_id;
            """
            result = conn.execute(text(insert_food), {
                "category_id": category_id,
                "name": item,
                "nutritional_info": "N/A",
                "num_ratings": 0,
                "restaurant_id": restaurant_id
            })
            food_item_id = result.scalar()

            insert_has_category = """
            INSERT INTO has_category (category_id, food_item_id)
            VALUES (:category_id, :food_item_id)
            """
            conn.execute(text(insert_has_category), {
                "category_id": category_id,
                "food_item_id": food_item_id
            })

            for _ in range(2):
                rating_data = {
                    "food_item_id": food_item_id,
                    "user_id": random.randint(1, 11),
                    "taste": round(random.uniform(1.0, 5.0), 1),
                    "presentation": round(random.uniform(1.0, 5.0), 1),
                    "price": round(random.uniform(1.0, 5.0), 1),
                    "value": round(random.uniform(1.0, 5.0), 1),
                    "comment": random.choice([
                        "Great dish, very tasty!",
                        "Could be better",
                        "Amazing!",
                        "Meh.",
                        "Best thing I’ve had this week!",
                        "A bit bland for me",
                        "Definitely ordering again",
                        "Not what I expected, but good",
                        "I didn’t really like this dish",
                        "Woah that is the best thing I have ever tasted!"
                    ])
                }

                insert_rating = """
                INSERT INTO rating (food_item_id, user_id, taste_rating, presentation_rating, price_rating, value_rating, comment)
                VALUES (:food_item_id, :user_id, :taste, :presentation, :price, :value, :comment)
                """
                conn.execute(text(insert_rating), rating_data)


    return f"✅ Inserted '{restaurant_name}' and {len(menu_items)} food items successfully."

# Test it
if __name__ == "__main__":
    restaurants =["https://menupages.com/adyar-ananda-bhavan-indian-restaurant/1071-1st-ave-new-york",
                  "https://menupages.com/afghan-kebab-house/1448-1st-ave-new-york",
                  "https://menupages.com/ag-kitchen/269-columbus-ave-new-york"
                  ] 
    for restaurant in restaurants:
        print(insert_restaurant_and_menu(restaurant))
