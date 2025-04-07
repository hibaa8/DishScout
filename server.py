
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASE_USERNAME = "ha2616"
DATABASE_PASSWRD = "489057"
DATABASE_HOST = "34.148.223.31"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"

engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


@app.route('/')
def index():
    return render_template("index.html")



# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
# 	# accessing form inputs from user
# 	name = request.form['name']
	
# 	# passing params in for each variable into query
# 	params = {}
# 	params["new_name"] = name
# 	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
# 	g.conn.commit()
# 	return redirect('/')

@app.route('/search', methods=['POST'])
def search():
    food_name = request.form["query"]
    get_food_item_query = f"""
    WITH selected_food_item AS (
    SELECT food_item_id
    FROM rating
    WHERE food_item_id IN (
        SELECT food_item_id 
        FROM food_item 
        WHERE name ILIKE '%{food_name}%'
    )
    GROUP BY food_item_id
    ORDER BY SUM(taste_rating + presentation_rating + price_rating + value_rating) DESC
    LIMIT 1
    )
    SELECT food_item.food_item_id, food_item.name, rest.restaurant_id, rest.name, rest.location FROM restaurant rest
    JOIN food_item ON rest.restaurant_id = food_item.restaurant_id
    WHERE food_item.food_item_id = (SELECT food_item_id FROM selected_food_item);
    """
    
    # get_food_item_query = "select * from food_item;"
    cursor = g.conn.execute(text(get_food_item_query))
    options = [row for row in cursor]
    cursor.close()

    context = dict(data = options)
    print(context)
    return render_template("search_results.html", query=food_name, results=context)


@app.route('/food_item/<int:food_item_id>')
def food_item(food_item_id):
    """
    Food item name (2)
    food category:
    get category_ids for food items from has_category and map them to category names, then render the category name list here
    restaurant name:
    use the restaurant_id and search restaurant table to identify the restaurant name
    average rating:
    run a query to compute the average rating of that food_item and then render the output here
    Add rating button 
    ratings:
    use the food_item_id to render all the ratings for that food item
    """
    res = {}

    res["food_item_id"] = food_item_id
    # 1. Get food item name + restaurant_id
    get_food_item_info_query = """
        SELECT name, restaurant_id 
        FROM food_item 
        WHERE food_item_id = :food_item_id;
    """
    food_item_info = g.conn.execute(text(get_food_item_info_query), {"food_item_id": food_item_id}).fetchone()

    if not food_item_info:
        return "Food item not found", 404

    res["food_item_name"] = food_item_info[0]
    restaurant_id = food_item_info[1]

    # 2. Get category names for the food item
    get_category_query = """
        select category from categories where category_id in (
        SELECT category_id
        FROM has_category
        WHERE has_category.food_item_id = :food_item_id
        );
    """
    category_results = g.conn.execute(text(get_category_query), {"food_item_id": food_item_id})
    res["categories"] = [row[0] for row in category_results]

    # 3. Get restaurant name
    get_restaurant_query = """
    SELECT restaurant_id, name, location
    FROM restaurant
    WHERE restaurant_id = :restaurant_id;
    """
    restaurant_info = g.conn.execute(
        text(get_restaurant_query), 
        {"restaurant_id": restaurant_id}
    ).fetchone()
    
    res["restaurant_id"] = restaurant_info[0]
    res["restaurant_name"] = restaurant_info[1]
    res["restaurant_location"] = restaurant_info[2]

    # 4. Get average ratings
    get_four_average_ratings_query = """
        SELECT 
            AVG(taste_rating), 
            AVG(presentation_rating), 
            AVG(price_rating), 
            AVG(value_rating)
        FROM rating
        WHERE food_item_id = :food_item_id;
    """
    avg_ratings = g.conn.execute(text(get_four_average_ratings_query), {"food_item_id": food_item_id}).fetchone()
    res["average_ratings"] = avg_ratings  # tuple: (taste_avg, presentation_avg, price_avg, value_avg)

    # 5. Get all ratings (tuples)
    get_ratings_query = """
        SELECT user_id, taste_rating, presentation_rating,  price_rating, value_rating, comment    
        FROM rating 
        WHERE food_item_id = :food_item_id;
    """
    rating_results = g.conn.execute(text(get_ratings_query), {"food_item_id": food_item_id})
    res["reviews"] = [row for row in rating_results]  # list of tuples

    print(res)
    return render_template("food_item.html", food=res)

@app.route('/add_review/<int:food_item_id>', methods=['GET', 'POST'])
def add_review(food_item_id):
    res = {"food_item_id": food_item_id}

    # 1. Get food item name + restaurant_id
    get_food_item_query = """
    SELECT name, restaurant_id 
    FROM food_item 
    WHERE food_item_id = :food_item_id
    """
    food_item_data = g.conn.execute(text(get_food_item_query), {"food_item_id": food_item_id}).fetchone()
    res["food_item_name"] = food_item_data[0]
    restaurant_id = food_item_data[1]

    # 2. Get restaurant name
    get_restaurant_query = """
    SELECT name 
    FROM restaurant 
    WHERE restaurant_id = :restaurant_id
    """
    restaurant_name = g.conn.execute(text(get_restaurant_query), {"restaurant_id": restaurant_id}).scalar()
    res["restaurant_name"] = restaurant_name

    # If POST, insert the review (optional to complete here)
    if request.method == "POST":
        taste = int(request.form["taste"])
        presentation = int(request.form["presentation"])
        price = int(request.form["price"])
        value = int(request.form["value"])
        comment = request.form.get("comment", "")
        user_id = 1

        insert_query = """
        INSERT INTO rating (food_item_id, user_id, taste_rating, presentation_rating, price_rating, value_rating, comment)
        VALUES (:food_item_id, :user_id, :taste_rating, :presentation_rating, :price_rating, :value_rating, :comment)
        """
        g.conn.execute(
            text(insert_query),
            {
                "food_item_id": food_item_id,
                "user_id": user_id,
                "taste_rating": taste,
                "presentation_rating": presentation,
                "price_rating": price,
                "value_rating": value,
                "comment": comment
            }
        )
        g.conn.commit()
        return redirect(f"/food_item/{food_item_id}")

    return render_template("add_review.html", food=res)


@app.route('/restaurant/<int:restaurant_id>')
def restaurant(restaurant_id):
    restaurant = {"restaurant_id": restaurant_id}
    menu = {}

    get_restaurant_info_query = """
    SELECT * FROM restaurant WHERE restaurant_id = :restaurant_id;
    """
    restaurant_info = g.conn.execute(
        text(get_restaurant_info_query), {"restaurant_id": restaurant_id}
    ).fetchone()

    restaurant["name"] = restaurant_info[1]
    restaurant["location"] = restaurant_info[2]
    restaurant["website"] = restaurant_info[3]
    restaurant["phone_number"] = restaurant_info[4]
    restaurant["hours"] = restaurant_info[5]
    restaurant["rating"] = restaurant_info[6]
    restaurant["price_range"] = restaurant_info[7]

    get_menu_items_query = """
    SELECT food_item_id, category_id, name 
    FROM food_item 
    WHERE restaurant_id = :restaurant_id;
    """
    menu_items = g.conn.execute(
        text(get_menu_items_query), {"restaurant_id": restaurant_id}
    ).fetchall()
    menu["menu_items"] = menu_items

    return render_template("restaurant.html", restaurant=restaurant, menu=menu)


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()