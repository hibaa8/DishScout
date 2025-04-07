
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
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.148.223.31/proj1part2
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.148.223.31/proj1part2"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "ha2616"
DATABASE_PASSWRD = "489057"
DATABASE_HOST = "34.148.223.31"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"

# DATABASE_USERNAME = ""
# DATABASE_PASSWRD = ""
# DATABASE_HOST = "34.148.223.31"
# DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
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
    food_name = request.form("query")
    # search_type = request.args.get("search_type")
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
    SELECT rest.name, rest.location 
    FROM restaurant rest
    JOIN selected_food_item food ON rest.restaurant_id = food.restaurant_id
    WHERE food.food_item_id = (SELECT food_item_id FROM selected_food_item);
    """
    cursor = g.conn.execute(text(get_food_item_query))
    options = []
    for result in cursor:
        options.append(result[0])
    cursor.close()

    context = dict(data = options)

    return render_template("search_results.html", query=food_name, results=context)




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