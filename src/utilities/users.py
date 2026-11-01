from datetime import datetime, timezone

from classes.catalog import BookUnavailableError, CatalogData
from classes.book_release import BookRelease
from classes.user import User
from utilities.util import (
	print_subheadline,
	prompt_for_choice,
	prompt_for_confirmation,
	prompt_for_float,
	search_for_choice,
)

def manage_user(catalog: CatalogData):
	user = search_for_choice(
		'Search for user by name, email, or ID',
		catalog.users.read_all(),
		User.is_query_match,
	)

	if user is None:
		raise ValueError('User not found.')

	# User manageemnt loop
	while True:
		print_subheadline(f'Manage User: {user}')
		options = [
			('details', 'User details'),
			('history', 'Checkout history'),
			('checkout', 'Check out a book'),
			('renew', 'Renew a book'),
			('return', 'Return a book'),
			('fines', 'Pay fines'),
			('exit', 'Exit user management'),
		]
		choice = prompt_for_choice('Choose an action:', options)
		if choice == 'details':
			view_user_details(user, catalog)
		elif choice == 'history':
			print_checkout_history(user, catalog)
		elif choice == 'checkout':
			checkout_book(user, catalog)
		elif choice == 'renew':
			renew_book(user, catalog)
		elif choice == 'return':
			return_book(user, catalog)
		elif choice == 'fines':
			pay_fines(user, catalog)
		elif choice == 'exit':
			return

def view_user_details(user: User, catalog: CatalogData):
	print(f'User details for {user.first_name} {user.last_name}:')
	print(f'ID: {user.id}')
	print(f'Email: {user.email}')
	checkouts = catalog.get_checkouts_for_user(user)
	print(f'Total checkouts (all time): {len(checkouts)}')
	print(f'Total fines (all time): ${catalog.get_total_fines(user):.2f}')
	print(f'Total fines paid (all time): ${user.fines_paid:.2f}')
	print(f'Total fines due: ${user.fines_due:.2f}')

def print_checkout_history(user: User, catalog: CatalogData):
	checkouts = catalog.get_checkouts_for_user(user)
	if not checkouts:
		print('No checkout history found.')
		return

	currently_borrowed = [
		checkout for checkout in checkouts if checkout.returned_date is None
	]
	print(f'Currently borrowed books ({len(currently_borrowed)}):')
	if not currently_borrowed:
		print('None.')
	else:
		for checkout in currently_borrowed:
			copy = catalog.get_copy_by_id(checkout.copy_id)
			book = catalog.get_book_by_isbn(copy.isbn)
			print(book)
	print()

	print(f'Checkout history for user {user.first_name} {user.last_name}:')
	for checkout in checkouts:
		copy = catalog.get_copy_by_id(checkout.copy_id)
		book = catalog.get_book_by_isbn(copy.isbn)
		return_string = (
			f'returned on {checkout.returned_date}'
			if checkout.returned_date
			else f'due by {checkout.due_date}'
		)

		print(
			f'Checked out {book} (#{copy.id})',
			f'on {checkout.checkout_date},',
			f'{return_string}',
		)

def checkout_book(user: User, catalog: CatalogData):
	# Prevent users from checking out a book while they have overdue checkouts.
	overdue_checkouts = catalog.get_overdue_checkouts_for_user(user)
	while len(overdue_checkouts) > 0:
		print(
			'User cannot check out books until',
			'overdue books have been returned:',
		)
		for checkout in overdue_checkouts:
			book = catalog.get_book_by_copy_id(checkout.copy_id)
			print(f'{book} (due on {checkout.due_date})')

		if not prompt_for_confirmation('Continue to return overdue books?'):
			return
		return_book(user, catalog)
		overdue_checkouts = catalog.get_overdue_checkouts_for_user(user)

	# Prevent users from checking out a book while they have outstanding fines.
	while user.fines_due > 0:
		print(
			'User cannot check out books until',
			'outstanding fines have been paid:',
			f'${user.fines_due:.2f}',
		)

		if not prompt_for_confirmation('Continue to payment?'):
			return
		pay_fines(user, catalog)

	book = search_for_choice(
		'Search for book to checkout by title, author, or ISBN',
		catalog.books.read_all(),
		BookRelease.is_query_match,
	)

	if book is None:
		raise ValueError('Book not found.')
	if not catalog.is_book_available(book):
		raise ValueError('Book is not available for checkout.')

	print(f'Book selected: {book}')
	if not prompt_for_confirmation('Confirm checkout?'):
		return

	try:
		catalog.checkout_book(user, book)
	except BookUnavailableError:
		print('Book is not available for checkout.')
		return

	print('Checkout complete.')

def renew_book(user: User, catalog: CatalogData):
	checkouts = catalog.get_checkouts_for_user(user)

	# Determine if any books are borrowed by the user.
	if not checkouts:
		print('No books currently borrowed.')
		return

	current_checkouts = [
		checkout for checkout in checkouts
		if checkout.returned_date is None
	]

	if not current_checkouts:
		print('No books currently borrowed.')
		return

	# Determine whether any of the user's books are eligible for renewal.
	today = datetime.now(tz=timezone.utc).date()
	on_time_checkout_ids = {
		checkout.id
		for checkout in current_checkouts
		if checkout.due_date >= today
	}

	renewable_checkouts = [
		checkout for checkout in current_checkouts
		if checkout.renewal_date is None
		and checkout.id in on_time_checkout_ids
	]

	if not renewable_checkouts:
		print('No books currently eligible for renewal.')
		return

	# List the eligible books and prompt the user for a choice.
	checkout = prompt_for_choice(
		'Choose a book to renew:',
		[
			(checkout, str(catalog.get_book_by_copy_id(checkout.copy_id)))
			for checkout in renewable_checkouts
		],
	)

	if checkout is None:
		raise ValueError('Checkout not found.')

	copy = catalog.get_copy_by_id(checkout.copy_id)
	book = catalog.get_book_by_isbn(copy.isbn)
	print(f'Book selected: {book}')
	if not prompt_for_confirmation('Confirm renewal?'):
		return

	# Run the renewal function.
	catalog.renew_book(checkout)
	print('Book renewed successfully.')

def return_book(user: User, catalog: CatalogData):
	checkouts = catalog.get_checkouts_for_user(user)
	if not checkouts:
		print('No books currently borrowed.')
		return

	current_checkouts = [
		checkout for checkout in checkouts
		if checkout.returned_date is None
	]

	if not current_checkouts:
		print('No books currently borrowed.')
		return

	overdue_checkout_ids = {
		checkout.id for checkout in catalog.get_overdue_checkouts_for_user(user)
	}

	checkout = prompt_for_choice(
		'Choose a book to return ([!] = overdue):',
		[
			(
				checkout,
				f'[!] {catalog.get_book_by_copy_id(checkout.copy_id)}'
				if checkout.id in overdue_checkout_ids
				else str(catalog.get_book_by_copy_id(checkout.copy_id)),
			)
			for checkout in current_checkouts
		],
	)

	if checkout is None:
		raise ValueError('Checkout not found.')

	copy = catalog.get_copy_by_id(checkout.copy_id)
	book = catalog.get_book_by_isbn(copy.isbn)
	print(f'Book selected: {book}')
	if not prompt_for_confirmation('Confirm return?'):
		return

	catalog.return_book(checkout)
	if checkout.returned_date is None:
		raise ValueError('Book wasn\'t returned.')

	# TODO
	# This conditional block needs to be audited.
	# Provide feedback in comments, and determine if there are any bugs.
	#
	# BUG
	# In particular, the system does not account for late fees
	# on books that have not been turned in yet.
	# Perhaps a system is needed to charge late fees for books not returned yet.
	# Alternatively, a system that demands overdue books be returned could work instead.

	# Charge a $0.20 fine per day late, up to a maximum of $5.00
	if checkout.due_date < checkout.returned_date:
		# Count days overdue.
		date_delta = checkout.returned_date - checkout.due_date
		days_overdue = date_delta.days
		# Calculate the fine.
		fine = days_overdue * 0.20
		fine = min(fine, 5.00)
		# Apply the fine and return the book.
		catalog.add_fine(user, fine)
		print(
			'Book returned successfully.',
			f'Fine of ${fine:.2f} applied.',
		)
	else:
		print('Book returned successfully.')

def pay_fines(user: User, catalog: CatalogData):
	if user.fines_due == 0:
		print('No fines are due.')
		return

	print(f'Total fines due: ${user.fines_due:.2f}')
	payment = prompt_for_float('Enter payment amount:')
	catalog.pay_fines(user, payment)
	print('Fines paid successfully.')
