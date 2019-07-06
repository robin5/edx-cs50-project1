import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import generate_password_hash, check_password_hash

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
db = scoped_session(sessionmaker(bind=engine))

# ---------------------------------------------
# Function: db_search
#
# Description: Queries database for books matching
#     criteria given by parameters
#
# Parameters:
#
#     isbn - partial or full ISBN of book
#     title - partial or full title of book
#     author - partial or full author's name of book
#
# Return: list of books matching search criteria
# ---------------------------------------------

def db_search(isbn, title, author):

	# Remove surrounding white space from each input
	isbn = isbn.strip()
	title = title.strip()
	author = author.strip()

	# If isbn is not empty set where to isbn like clause else set it to blank
	
	where = "" if isbn == "" else "isbn ILIKE '%" + isbn + "%'"

	# if title not present add title to where clause
	
	if title != "":
		where += (" OR " if where else "") + "title ILIKE '%" + title + "%'"

	# if author not present add author to where clause
	if author != "":
		where += (" OR " if where else "") + "author ILIKE '%" + author + "%'"

	# Test for null case (i.e. no input from user) and return empty array if detected
	if where == "":
		return []

	query = "SELECT * FROM tbl_books WHERE " + where;

	print("Query: \"" + query + "\"")

	books = db.execute(query).fetchall()

	return books

# ---------------------------------------------
# Function: db_get_book
#
# Description: Queries database for book with 
#     given ISBN
#
# Parameters:
#
#     isbn - ISBN of book
#
# Return: Book corresponding to ISBN or none
# ---------------------------------------------

def db_get_book(isbn):

	book = db.execute('SELECT * FROM tbl_books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()

	return book

# ---------------------------------------------
# Function: db_get_reviews
#
# Description: Queries database for reviews of 
#     book given by ISBN
#
# Parameters:
#
#     isbn - ISBN of book
#
# Return: List of reviews corresponding to ISBN or none
# ---------------------------------------------

def db_get_reviews(isbn):

	reviews = db.execute('SELECT * FROM tbl_reviews INNER JOIN tbl_users ON tbl_reviews.user_id=tbl_users.user_id  WHERE isbn = :isbn', {"isbn": isbn}).fetchall()

	return reviews

# ---------------------------------------------
# Function: db_get_user
#
# Description: Queries database for user with 
#     given username and matching password
#
# Parameters:
#
#     user_name - user name of user
#     password - password of user
#
# Return: Book corresponding to ISBN or none
# ---------------------------------------------

def db_get_user(user_name, password):

	query = "SELECT * FROM tbl_users WHERE user_name = '" + user_name + "'"
	
	user = db.execute(query).fetchone()

	if user != None:

		if check_password_hash(user['password'], password):

			# return object with all user fields except for password
			return {
				'user_id':    user['user_id'],
				'user_name':  user['user_name'], 
				'first_name': user['first_name'],
				'last_name':  user['last_name'],
				'email':      user['email']
				}

	return None

# ---------------------------------------------
# Function: db_insert_user
#
# Description: Inserts user into the database 
#
# Parameters:
#
#     first_name - first name of user
#     last_name - last name of user
#     email - email address of user
#     user_name - user name of user
#     password - password for user
#
# Return: True if user was inserted, False otherwise
# ---------------------------------------------

def db_insert_user(first_name, last_name, email, user_name, password):

	encrypted_password = encrypt(password)

	query = "INSERT INTO tbl_users (first_name, last_name, email, user_name, password) VALUES ('" + \
		first_name + "', '" + \
		last_name + "', '" + \
		email + "', '" + \
		user_name + "', '" + \
		encrypted_password + "') RETURNING user_id;"
	
	try:

		result = db.execute(query)
		db.commit()
		return True

	except Exception as e:

		#print('Exception:', str(e))
		return False	

# ---------------------------------------------
# Function: db_insert_review
#
# Description: Inserts book review into the database 
#
# Parameters:
#
#     user_id - user's ids
#     isbn - the books ISBN
#     review - user's review
#     rating - user's rating
#
# Return: True if review was inserted, False otherwise
# ---------------------------------------------

def db_insert_review(user_id, isbn, review, rating):

	query = "INSERT INTO tbl_reviews (user_id, isbn, text, rating) \
			 VALUES ('" + \
			     str(user_id) + "', '" + \
			     str(isbn) + "', '" + \
			     str(review) + "', '" + \
			     str(rating) + "')"
	
	try:

		result = db.execute(query)
		db.commit()

		return True

	except:

		return False	

# ---------------------------------------------
# Function: encrypt
#
# Description: encrypts password using a hashing algorithm 
#
# Parameters:
#
#     password - password to encrypt
#
# Return: encrypted password
# ---------------------------------------------

def encrypt(password):

	return generate_password_hash(password)
