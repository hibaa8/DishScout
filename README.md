Group Number: Project 1 Group 2

1. PostgreSQL Account:
   Database URI: postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2

2. URL of Web Application:
   http://35.243.188.131:8111/

3. Implementation Summary:
   The following components from our original Part 1 proposal were implemented:
   - A search interface on the homepage allowing users to query either food items or restaurants
   - A results page that displays food items or restaurants matching the query
   - A food item detail page with nutritional information, average ratings, and a list of user reviews
   - A review submission form allowing users to enter ratings for taste, presentation, price, and value, along with optional comments
   - A restaurant page that shows restaurant information and links to their menu items

   We did not implement user login and personalized profiles as initially proposed in our "Future Work" section. We decided to prioritize the core functionality of search, review, and browsing food/restaurant pages for this submission.
   Additionally, we added robust form validation and clean test routes to allow testing front-end pages independently from backend database logic during development.

4. Interesting Pages from a Database Perspective:

   a) search_results.html:
   This page performs a dynamic SQL query depending on whether the user is searching for food or restaurants. If the user selects "food," the backend retrieves food item names joined with their associated restaurant names. If "restaurant" is selected, the backend returns restaurant records. The SQL logic dynamically adjusts based on query parameters and uses `ILIKE` for case-insensitive search. The query joins tables such as FoodItems, Restaurants, and optionally Reviews for aggregate previews.

   b) food_item.html:
   This page displays detailed data about a food item, including average user ratings and nutritional data. It performs a join across multiple tables (FoodItems, Restaurants, and Reviews). It also runs an aggregate query to calculate average ratings per category (taste, presentation, etc.), and another query to pull all existing user reviews for display. These operations showcase multiple query types: joins, aggregates, and filtering by primary key.

End of README.
