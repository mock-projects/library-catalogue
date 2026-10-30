from classes.catalog import CatalogData
from classes.models import Book
from utilities.util import print_subheadline, search_for_choice

def search_catalog(catalog: CatalogData):
	print_subheadline('Search library catalog')
	book = search_for_choice(
		'Search for book by title, author, or ISBN',
		catalog.books.read_all(),
		Book.is_query_match,
	)

	if book is None:
		raise Exception('Book not found.')

	print()
	print(f'Title: {book.title}')
	print(f'Author: {book.author}')
	print(f'Year: {book.year}')
	print(f'ISBN: {book.isbn}')
	print(
		f'Available for checkout: {"Yes" if catalog.is_book_available(book) else "No"}'
	)

	checkouts = catalog.get_checkouts_for_book(book)

	print('\nCheckout history:')
	if not checkouts:
		print('No checkouts.')
	else:
		for checkout in checkouts:
			user = catalog.get_user_by_id(checkout.user_id)
			return_string = (
				f'returned on {checkout.returned_date}'
				if checkout.returned_date
				else f'due by {checkout.due_date}'
			)
			print(
				f'Checked out by {user} on {checkout.checkout_date}, {return_string}.'
			)
