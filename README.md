# DishScout 
A full-stack web application to explore NYC restaurants and review menu items.

DishScout allows users to search for food items or restaurants, view detailed reviews, leave their own ratings, and favorite dishes they love. The platform pulls data from the Google Places API and scrapes menu data using BeautifulSoup for a rich discovery experience.

---

## Features

### Search Functionality
- Search by **food item** or **restaurant name**
- Results sorted by average rating (highest first)

### Food Item Pages
- View:
  - Name and location of restaurant
  - Food categories (from `has_category`)
  - Average ratings for taste, presentation, price, and value
  - Reviews from other users
- Add new reviews or edit existing ones
- Add items to favorites (only if logged in)

### User Authentication
- Secure sign-up and login using hashed passwords (with `werkzeug.security`)
- Logged-in users can:
  - Leave or edit reviews
  - Add/remove favorite dishes
  - View all past reviews and favorites in their **Profile**

### Profile Page
- Lists all reviews the user has posted
- Edit or delete reviews
- View and remove favorited items

---

## Database

PostgreSQL database with key tables:
- `users`
- `restaurant`
- `food_item`
- `rating`
- `favorites`
- `has_category`
- `categories`

SQLAlchemy is used for executing raw SQL queries and managing transactions.

---

## Data Sources

- [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview) – For restaurant metadata
- [MenuPages](https://menupages.com/) – Scraped with `BeautifulSoup` to get food items
- Random reviews generated for demonstration

---

## Tech Stack

- **Backend:** Flask (Python), SQLAlchemy
- **Frontend:** HTML, CSS (Bootstrap), Jinja2 Templates
- **Database:** PostgreSQL
- **Other:** BeautifulSoup, Google Places API

---

## Setup

1. Clone the repo:
```bash
git clone https://github.com/hibaa8/DishScout.git
cd dishscout
```
2. Install dependencies:
```
pip install -r requirements.txt
```

3. Create a .env file and add your Google API key:
```
GOOGLE_PLACES_KEY=your_key_here
```

4. Run the app:
```
python server.py
```
