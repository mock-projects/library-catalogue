from classes.catalog import CatalogData
from utilities.util import print_subheadline, prompt_for_choice

def show_status_page(catalog: CatalogData):
	print_subheadline('Status Pages')
	options = [
		('checkouts', 'Current Checkouts'),
		('books', 'Available Books'),
		('users', 'All Users'),
		('analytics', 'Book Analytics'),
	]
	choice = prompt_for_choice('Available status pages to view', options)
	if choice == 'checkouts':
		print_checkouts(catalog)
	elif choice == 'books':
		print_available_books(catalog)
	elif choice == 'users':
		print_all_users(catalog)
	elif choice == 'analytics':
		print_book_analytics(catalog)

def print_checkouts(catalog: CatalogData):
	'''Prints current status of all guests with currently checked out books.'''
	print_subheadline('Current Checkouts')

	# Get all users
	for user in catalog.users.read_all():
		checkouts = catalog.get_checkouts_for_user(user)
		active_checkouts = [
			checkout for checkout in checkouts if checkout.returned_date is None
		]
		if active_checkouts:
			print(f'=== {user.first_name} {user.last_name} ===')
			for checkout in active_checkouts:
				book = catalog.get_book_by_isbn(checkout.isbn)
				print(
					f'{book.title} (borrowed on {checkout.checkout_date}, due on {checkout.due_date})'
				)
			print()

def print_available_books(catalog: CatalogData):
	'''Prints all books that are currently available to be checked out.'''
	print_subheadline('Available Books')

	for book in catalog.books.read_all():
		if catalog.is_book_available(book):
			print(book)

def print_all_users(catalog: CatalogData):
	'''Prints all users in the database.'''
	print_subheadline('All Users')
	for user in catalog.users.read_all():
		print(user)

def print_book_analytics(catalog):
	'''Get analytics for each book on checkout count and how long people hold onto the book for'''
	# TODO
	# This function needs to be audited.
	# Provide feedback in comments, and determine if there are any bugs.

	checkout_counts = dict()

	for book in catalog.books.read_all():
		checkout_counts[book.title] = len(catalog.get_checkouts_for_book(book))

	print_subheadline('Book Analytics')

	# Number of checkouts
	print('Books ordered by number of checkouts')
	checkout_counts = list(checkout_counts.items())
	checkout_counts.sort(key=lambda x: x[1], reverse=True)
	for title, count in checkout_counts:
		print(f'{count} checkouts: {title}')

	# Average checkout duration
	print('\nBooks ordered by average checkout duration')
	checkout_durations = dict()
	for book in catalog.books.read_all():
		checkouts = catalog.get_checkouts_for_book(book)
		checkout_duration_sum = 0
		checkout_duration_count = 0

		for checkout in checkouts:
			duration = (
				checkout.returned_date - checkout.checkout_date
			).total_seconds() / (60 * 60 * 24)
			checkout_duration_sum += duration
			checkout_duration_count += 1

		if checkout_duration_count > 0:
			average_checkout_duration = checkout_duration_sum / checkout_duration_count
			checkout_durations[book.title] = average_checkout_duration

	checkout_durations = list(checkout_durations.items())
	checkout_durations.sort(key=lambda x: x[1], reverse=True)
	for title, duration in checkout_durations:
		print(f'{duration:.0f} days: {title}')
