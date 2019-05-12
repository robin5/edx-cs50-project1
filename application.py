from flask import Flask, render_template, request, redirect, url_for, session
#from flask_session import Session


app = Flask(__name__)

#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_type"] = "filesystem"
#Session(app)

logged_in = False

# ----------------------------------------------------------
# Function: redirect_to_index
#
# Description:  This function is used by each page too cause 
#     the user to be redirected to the index page when the 
#     user is not logged in.
#
# Parameters: none
#
# Return: the index page to be rendered
# ----------------------------------------------------------

def redirect_to_index():
	"""Redirectes the user to the index page"""

	return redirect(url_for("index"))

# --------------------------------------
#
# --------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
	"""Render index page"""
	
	return render_template("index.html", logged_in=logged_in)

# --------------------------------------
#
# --------------------------------------

@app.route("/logout", methods=["GET", "POST"])
def logout():
	"""Render index page"""
	
	global logged_in

	logged_in = False

	return render_template("index.html", logged_in=logged_in)

# --------------------------------------
#
# --------------------------------------

@app.route("/login/<string:form>", methods=["GET", "POST"])
def login(form):
	"""Render login page"""
	
	global logged_in

	if request.method == "GET":
		if logged_in:
			return redirect(url_for("search"))
		
		return render_template("login.html", form=form)
	else:
		if not logged_in:
			#at the moment hardcode to just log in
			logged_in = True
			return redirect(url_for("search"))

# --------------------------------------
#
# --------------------------------------

@app.route("/search", methods=["GET"])
def search():
	""" Render Search page"""

	if logged_in:
		return render_template("search.html")
	else:
		return redirect_to_index()

# --------------------------------------
#
# --------------------------------------

@app.route("/results", methods=["POST"])
def results():
	"""Renders page that shows search results"""

	if logged_in:

		# Get params from request
		isbn=request.form.get("isbn")
		title=request.form.get("title")
		author=request.form.get("author")

		#Get results from database
		search_results = get_results_from_database(isbn, title, author)

		return render_template("results.html", search_results=search_results)
	else:
		return redirect_to_index()

# --------------------------------------
#
# --------------------------------------

@app.route("/book/<string:isbn>", methods=["GET"])
def book(isbn):
	"""Renders page that show book details """

	if logged_in:
		book = get_book_from_database(isbn)
		return render_template("book.html", book=book)
	else:
		return redirect_to_index()

#########################################################################
#                        DATABASE
#########################################################################

def get_results_from_database(isbn, title, author):
		return [{"isbn":"1234", "title":"dusk to dawn", "author":"robin"},\
			{"isbn":"5678", "title":"Titanic", "author":"Sage"}]

def get_book_from_database(isbn):
	return {"isbn":"1234", "title":"dusk to dawn", "author":"robin", "year":"1975"}
