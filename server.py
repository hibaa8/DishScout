from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search():
    query = request.args.get("query")
    search_type = request.args.get("search_type")

    # Simulated dummy data
    if search_type == "food":
        results = [
            {"food_item_id": 1, "name": "Spicy Ramen", "restaurant_name": "Totto Ramen"},
            {"food_item_id": 2, "name": "Miso Soup", "restaurant_name": "Ippudo"}
        ]
    else:
        results = [
            {"restaurant_id": 101, "name": "Totto Ramen", "location": "NYC"},
            {"restaurant_id": 102, "name": "Ippudo", "location": "NYC"}
        ]

    return render_template("search_results.html", query=query, search_type=search_type, results=results)

@app.route('/food_item/<int:food_item_id>')
def food_item(food_item_id):
    # Fake food item info
    food = {
        "food_item_id": food_item_id,
        "name": "Spicy Ramen",
        "restaurant_id": 101,
        "restaurant_name": "Totto Ramen",
        "nutritional_info": "600 cal, 20g protein, 70g carbs",
        "avg_rating": 4.5
    }

    # Fake reviews
    reviews = [
        {
            "taste_rating": 5,
            "presentation_rating": 4,
            "price_rating": 4,
            "value_rating": 5,
            "comment": "Delicious and super flavorful!"
        },
        {
            "taste_rating": 4,
            "presentation_rating": 3,
            "price_rating": 4,
            "value_rating": 4,
            "comment": "Good but a bit salty."
        }
    ]

    return render_template("food_item.html", food=food, reviews=reviews)

@app.route('/add_review/<int:food_item_id>', methods=['GET', 'POST'])
def add_review(food_item_id):
    if request.method == 'POST':
        # Normally you'd save the review to the DB here.
        print("Review Submitted:")
        print("Taste:", request.form.get("taste"))
        print("Presentation:", request.form.get("presentation"))
        print("Price:", request.form.get("price"))
        print("Value:", request.form.get("value"))
        print("Comment:", request.form.get("comment"))

        return "Review submitted! (You can redirect to food page here.)"

    # Dummy name for now
    return render_template("add_review.html", food_item_id=food_item_id, food_name="Spicy Ramen")

@app.route('/restaurant/<int:restaurant_id>')
def restaurant(restaurant_id):
    restaurant = {
        "name": "Totto Ramen",
        "location": "366 W 52nd St, New York, NY",
        "phone_number": "212-582-0052",
        "hours": "Mon-Sun: 11:00AM – 11:00PM",
        "website": "https://tottoramen.com"
    }

    menu_items = [
        {"food_item_id": 1, "name": "Spicy Ramen"},
        {"food_item_id": 2, "name": "Miso Soup"},
        {"food_item_id": 3, "name": "Chicken Karaage"}
    ]

    return render_template("restaurant.html", restaurant=restaurant, menu_items=menu_items)



if __name__ == "__main__":
    app.run(debug=True, port=8111)

