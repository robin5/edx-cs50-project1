import os
import requests

# ---------------------------------------------
# Function: gr_get_book
#
# Description: makes an API call to get goodreads 
#    data of a book specified  by ISBN
#
# Parameters:
#
#     isbn - ISBN of book to recieve rating
#
# Return: Book rating or none
# ---------------------------------------------

def gr_get_book(isbn):

	# Get the books rating from the Goodreads API
	response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("GOODREADS_URL"), "isbns": isbn})
	
	# Check for successful response
	if response.status_code != 200:
		return None

	try:

		return response.json()['books'][0]

	except:

		return None
