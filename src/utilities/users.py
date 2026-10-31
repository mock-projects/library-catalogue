from classes.catalog import BookUnavailableError, CatalogData
from classes.book_release import BookRelease
from classes.user import User
from utilities.util import (
	print_subheadline,
	prompt_for_choice,
	prompt_for_confirmation,
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
			book = catalog.get_book_by_id(checkout.book_id)
			print(book)
	print()

	print(f'Checkout history for user {user.first_name} {user.last_name}:')
	for checkout in checkouts:
		book = catalog.get_book_by_id(checkout.book_id)
		return_string = (
			f'returned on {checkout.returned_date}'
			if checkout.returned_date
			else f'due by {checkout.due_date}'
		)
		print(f'Checked out {book} on {checkout.checkout_date}, {return_string}')

def checkout_book(user: User, catalog: CatalogData):
	book = search_for_choice(
		'Search for book to checkout by title, author, or ISBN',
		catalog.books.read_all(),
		BookRelease.is_query_match,
	)

	if book is None:
		raise ValueError('Book not found.')

	print(f'Book selected: {book}')

	if not prompt_for_confirmation('Confirm checkout?'):
		return

	# TODO
	# This conditional block needs to be audited.
	# Provide feedback in comments, and determine if there are any bugs.
	if user.fines_due > 0:
		print(
			f'User has outstanding fines that must be paid first: ${user.fines_due:.2f}'
		)
		if not prompt_for_confirmation('Pay fines?'):
			return
		pay_fines(user, catalog)

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
		checkout for checkout in checkouts if checkout.returned_date is None
	]

	if not current_checkouts:
		print('No books currently borrowed.')
		return

	# Determine whether any of the user's books are eligible for renewal.
	renewable_checkouts = [
		checkout for checkout in current_checkouts if checkout.renewal_date is None
	]

	if not renewable_checkouts:
		print('No books cuurently eligible for renewal.')
		return

	# List the eligible books and prompt the user for a choice.
	checkout = prompt_for_choice(
		'Choose a book to renew:',
		[
			(checkout, str(catalog.get_book_by_id(checkout.book_id)))
			for checkout in renewable_checkouts
		],
	)

	if checkout is None:
		raise ValueError('Checkout not found.')

	book = catalog.get_book_by_id(checkout.book_id)
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
		checkout for checkout in checkouts if checkout.returned_date is None
	]

	if not current_checkouts:
		print('No books currently borrowed.')
		return

	checkout = prompt_for_choice(
		'Choose a book to return:',
		[
			(checkout, str(catalog.get_book_by_id(checkout.book_id)))
			for checkout in current_checkouts
		],
	)

	if checkout is None:
		raise ValueError('Checkout not found.')

	book = catalog.get_book_by_id(checkout.book_id)
	print(f'Book selected: {book}')
	if not prompt_for_confirmation('Confirm return?'):
		return

	catalog.return_book(checkout)
	if checkout.returned_date is None:
		raise ValueError('Book wasn\'t returned.')

	# TODO
	# This conditional block needs to be audited.
	# Provide feedback in comments, and determine if there are any bugs.

	# Charge a $0.20 fine per day late, up to a maximum of $5.00
	if checkout.due_date < checkout.returned_date:
		days_overdue = (checkout.returned_date - checkout.due_date).total_seconds() / (
			60 * 60 * 24
		)
		fine = days_overdue * 0.20
		fine = min(fine, 5.00)
		catalog.set_fine(user, fine)
		print(f'Book returned successfully. Fine of ${fine:.2f} applied.')

	print('Book returned successfully.')

def pay_fines(user: User, catalog: CatalogData):
	# TODO
	# This function needs to be audited.
	# Provide feedback in comments, and determine if there are any bugs.
	if user.fines_due == 0:
		print('No fines are due.')
		return

	print(f'Total fines due: ${user.fines_due:.2f}')
	if not prompt_for_confirmation('Pay fines?'):
		return

	catalog.pay_fines(user)
	print('Fines paid successfully.')
