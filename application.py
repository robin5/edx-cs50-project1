from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

app.config["SECRET_KEY"] = 'super secret key'
#app.secret_key = 'super-secret-key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# -------------------------------------------------------------
# Function: redirect_to_index
#
# Description:  This function is used by each page to redirect
#     the user to the index page when the user is not logged in.
#
# Parameters: none
#
# Return: the index page to be rendered
# --------------------------------------------------------------

def redirect_to_index():
	"""Redirectes the user to the index page"""

	return redirect(url_for("index"))

# --------------------------------------
#
# --------------------------------------

def user_is_logged_in():

	if session.get("logged_in") is None:
		print("initialize logged_in to false")
		session["logged_in"] = False
	return session["logged_in"]

def login_user():
	session["logged_in"] = True
	print("Set logged_in to True")
	return True

def logout_user():
	session["logged_in"] = False
	print("Set logged_in to False")
	return False

# --------------------------------------
#
# --------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
	"""Render index page"""
	
	return render_template("index.html", logged_in=user_is_logged_in())

# --------------------------------------
#
# --------------------------------------

@app.route("/test", methods=["GET", "POST"])
def test():
	"""Render index page"""
	
	books = db.execute("SELECT * FROM tbl_books LIMIT 10").fetchall()
	print(books)
	return str(books)
    #return render_template("index.html", logged_in=user_is_logged_in())

# --------------------------------------
#
# --------------------------------------

@app.route("/logout", methods=["GET", "POST"])
def logout():
	"""Render index page"""
	
	logout_user()

	return render_template("index.html", logged_in=user_is_logged_in())

# --------------------------------------
#
# --------------------------------------

@app.route("/login/<string:form>", methods=["GET", "POST"])
def login(form):
	"""Render login page"""
	
	if request.method == "GET":

		if user_is_logged_in():
			return redirect(url_for("search"))
		
		return render_template("login.html", form=form)

	else:

		if login_user():
			return redirect(url_for("search"))

# --------------------------------------
#
# --------------------------------------

@app.route("/search", methods=["GET"])
def search():
	""" Render Search page"""

	if user_is_logged_in():
		return render_template("search.html")
	else:
		return redirect_to_index()

# --------------------------------------
#
# --------------------------------------

@app.route("/results", methods=["POST"])
def results():
	"""Renders page that shows search results"""

	if user_is_logged_in():

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

	if user_is_logged_in():

		book = get_book_from_database(isbn)

		res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("GOODREADS_URL"), "isbns": isbn})
		if res.status_code != 200:
			raise Exception("Error: API request unsuccessful.")
		data = res.json()

		return render_template("book.html", book=book, goodread=data["books"][0])
	else:
		return redirect_to_index()

#########################################################################
#                        DATABASE
#########################################################################

# --------------------------------------
#
# --------------------------------------

def get_results_from_database(isbn, title, author):

	# Remove surrounding white space from each input filed
	isbn = isbn.strip()
	title = title.strip()
	author = author.strip()

	# If isbn is not empty set where to isbn like clause else set it to blank
	where = "" if isbn == "" else "isbn LIKE '%" + isbn + "%'"

	# if title not present add title to where clause
	if title != "":
		where += (" OR " if where else "") + "title LIKE '%" + title + "%'"

	# if author not present add author to where clause
	if author != "":
		where += (" OR " if where else "") + "author LIKE '%" + author + "%'"

	# Test for null case (i.e. no input from user) and return empty array if detected
	if where == "":
		return []

	#query = "SELECT * FROM tbl_books LIMIT 10"
	query = "SELECT * FROM tbl_books WHERE " + where;

	print("Query: \"" + query + "\"")

	books = db.execute(query).fetchall()

	return books

# --------------------------------------
#
# --------------------------------------

def get_book_from_database(isbn):

	book = db.execute('SELECT * FROM tbl_books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()

	return book