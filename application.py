import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import functools
from datalayer import db_search, db_get_book, db_get_reviews, db_get_user, db_insert_user, db_insert_review
from flask import jsonify
from goodread import gr_get_book

app = Flask(__name__)

app.config["SECRET_KEY"] = 'super secret key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# --------------------
# User status messages
# --------------------

please_login_message = {'status': 'info', 'text': 'You are not logged in.  Please log in.'}
logout_message = {'status': 'info', 'text': 'Thanks for visiting our site.  Please come again.'}
review_thank_you_message = {'status': 'info', 'text': 'Thank you for your review.'}

messages = {
	'please_login_message': please_login_message,
	'logout_message': logout_message,
	'review_thank_you_message': review_thank_you_message
}

# -------------------------------------------------------------
# Function: redirect_to_index
#
# Description:  This function is used by each page to redirect
#     the user to the index page.
#
# Parameters: none
#
# Return: the index page to be rendered
# --------------------------------------------------------------

def redirect_to_index(message = None):
	"""Redirectes the user to the index page"""

	if message == None:
		return redirect(url_for("index"))
	else:
		return redirect(url_for("index", message = message))

# -------------------------------------------------------------
# Function: redirect_to_search
#
# Description:  This function is used by each page to redirect
#     the user to the search page.
#
# Parameters: none
#
# Return: the index page to be rendered
# --------------------------------------------------------------

def redirect_to_search():
	"""Redirectes the user to the index page"""

	return redirect(url_for("index"))

# ----------------------------------------------------
# Function: user_is_logged_in
#
# Description: tells whether user is logged in or not
#
# Parameters: none
#
# Return: True if user is logged in, False otherwise
# ---------------------------------------------------

def user_is_logged_in():

	if session.get("logged_in") is None:
		session["logged_in"] = False
	return session["logged_in"]

# -----------------------------------------------------
# Function: login_user
#
# Description: Logs user into the session.  On failure
#     redirects the user to the index page
#
# Parameters: User_name - User's user name
#             Password - User's password
#
# Return:  True if user was successfully logged in, 
#          False otherwise
# -----------------------------------------------------

def login_user(user_name, password):

	user = db_get_user(user_name, password)

	if user != None:
		session["user"] = user
		session["logged_in"] = True
		return True

	return logout_user()

# ------------------------------------------
# Function: logout_user
#
# Description: Logs user out of the session
#
# Parameters: none
#
# Return: False always
# ------------------------------------------

def logout_user():
	session.pop("user", None)
	session["logged_in"] = False
	return False

# ---------------------------------------------
# Function: index
#
# Description: View function for the index page
#
# Parameters: none
#
# Return: rendered html
# ---------------------------------------------

@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])

def index():
	"""Render index page with an optional message"""

	message = request.args.get('message')
	if message is None:
		message = ''
	else:
		message = messages[message]

	return render_template("index.html", user = session.get("user") ,logged_in = user_is_logged_in(), message = message)

# ---------------------------------------------
# Function: logout
#
# Description: View function for the logout page
#
# Parameters: none
#
# Return: rendered html
# ---------------------------------------------

@app.route("/logout", methods=["GET", "POST"])

def logout():
	"""Sign user out and redirct to index page"""
	
	logout_user()

	return redirect_to_index('logout_message')

# ---------------------------------------------
# Function: login
#
# Description: View function for the login page
#     which displays the sign-in form or registration
#     form and validates the form upon submission
#
# Parameters: form - switch which selects either
#     the sign-in form or register form
#
# Return: rendered html
# ---------------------------------------------

@app.route("/login/<string:form>", methods=["GET", "POST"])

def login(form):
	"""Render login page """
	
	if request.method == "GET":

		if user_is_logged_in():
			return redirect_to_search()
		
		return render_template("login.html", form=form)

	else:

		if form == 'sign-in': #Login form

			user_name = request.form.get("user-name")
			password = request.form.get("password")

			if not login_user(user_name, password):
				message = {'status': 'error', 'text': 'Invalid user name or password.  Please try again.'}
				return render_template("login.html", form = form, message = message)
			
			return redirect_to_search()
			
		else: # Registration form

			first_name = request.form.get("first-name")
			last_name = request.form.get("last-name")
			email = request.form.get("email")
			user_name = request.form.get("user-name")
			password = request.form.get("password")

			if not db_insert_user(first_name, last_name, email, user_name, password):
				message = {'status': 'info', 'text': 'User name already exist.  Please try a different user name.'}
				return render_template("login.html", form = form, message = message)

			if not login_user(user_name, password):
				message = {'status': 'warning', 'text': 'Registration accepted but unable to log you in at this time.  Please try signing in later.'}
				return render_template("login.html", form = form, message = message)

			return redirect_to_search()

# ---------------------------------------------
# Function: search
#
# Description: View function for the search page
#
# Parameters: none
#
# Return: rendered html if user is logged in 
#     otherwise redirected to index page
# ---------------------------------------------

@app.route("/search", methods=["GET"])
def search():
	""" Render Search page"""

	if user_is_logged_in():
		return render_template("search.html", user = session.get("user"))
	else:
		return redirect_to_index('please_login_message')

# ---------------------------------------------
# Function: results
#
# Description: View function for the search 
#     results page
#
# Parameters: none
#
# Return: rendered html if user is logged in 
#     otherwise redirected to index page
# ---------------------------------------------

@app.route("/results", methods=["POST"])
def results():
	"""Renders page that shows search results"""

	if user_is_logged_in():

		# Get params from request
		isbn = request.form.get("isbn")
		title = request.form.get("title")
		author = request.form.get("author")

		#Get results from database
		search_results = db_search(isbn, title, author)

		return render_template("results.html", user = session.get("user"), search_results=search_results)
	else:
		return redirect_to_index('please_login_message')

# ---------------------------------------------
# Function: book
#
# Description: View function for the book page. 
#     The page displays the book information if
#     a GET is used.  If a POST is used, the
#     books review will be inserted in the database 
#
# Parameters: isbn - selects book to display or
#     book for which review is posted
#
# Return: rendered html if user is logged in 
#     otherwise redirected to index page
# ---------------------------------------------

@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def book(isbn):
	"""Renders page that show book details """

	if user_is_logged_in():

		# Post the review to the database
		if request.method == "POST":

			# Get params from request
			review = request.form.get("book-review")
			rating = request.form.get("book-review-rating")
			user_id = session['user']['user_id']

			db_insert_review(user_id, isbn, review, rating)

			return redirect_to_index('review_thank_you_message')

		else:

			# Get the book data from the database
			book = db_get_book(isbn)

			# Get the review data for the book from the database
			reviews = db_get_reviews(isbn)

			# Search for a review from the current user
			user_review_defined = False
			for review in reviews:
				#print(session['user']['user_id'], ", ", review['user_id'])
				if review['user_id'] == session['user']['user_id']:
					user_review_defined = True
					break

			# Get the books rating from the Goodreads API
			goodread = gr_get_book(isbn)

			# Render the page
			return render_template("book.html", user = session["user"], book=book, goodread=goodread, reviews=reviews, user_review_defined = user_review_defined)
	
	else:
		
		return redirect_to_index('please_login_message')

# ---------------------------------------------
# Function: api
#
# Description: Returns book info in JSON format 
#
# Parameters: isbn - selects book to return
#
# Return: json data book is defined otherwise
#     404 page not found error
# ---------------------------------------------

@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
	"""return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score """

	# Get the book data from the database
	book = db_get_book(isbn)

	if book is None:
		return jsonify({}), 404

	obj = {
		"title": book['title'],
		"author": book['author'],
		"year": book['year'],
		"isbn": book['isbn'],
	}

	# Get the books rating from the Goodreads API
	book = gr_get_book(isbn)

	if not book is None:
		obj["review_count"] = book['reviews_count']
		obj["average_score"] = book['average_rating']

	return jsonify(obj)
