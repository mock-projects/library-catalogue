import os

from datetime import datetime, timedelta, timezone
from classes.book_copy import BookCopy
from classes.book_release import BookRelease
from classes.checkout import Checkout
from classes.data import Data
from classes.user import User

# 21-day checkout period
CHECKOUT_PERIOD = 21

# Obtain the data
DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

BOOKS_FILENAME = os.path.join(DATA_DIRECTORY, 'book_releases.csv')
COPIES_FILENAME = os.path.join(DATA_DIRECTORY, 'book_copies.csv')
USERS_FILENAME = os.path.join(DATA_DIRECTORY, 'users.csv')
CHECKOUTS_FILENAME = os.path.join(DATA_DIRECTORY, 'checkouts.csv')

BOOKS_FIELDNAMES = [
	'isbn',
	'title',
	'author',
	'year',
]

COPIES_FIELDNAMES = [
	'id',
	'isbn',
]

USERS_FIELDNAMES = [
	'id',
	'first_name',
	'last_name',
	'email',
	'fines_due',
]

CHECKOUTS_FIELDNAMES = [
	'id',
	'user_id',
	'copy_id',
	'checkout_date',
	'due_date',
	'renewal_date',
	'returned_date',
]

class CatalogData:
	'''Stores all data for the library catalog.'''


	books: Data[BookRelease]
	'''Books describe production releases with a particular unique isbn.'''

	copies: Data[BookCopy]
	'''Copies describe physical books, which may or may not share an isbn.'''

	users: Data[User]
	'''Users are stored in our database to track who has checked out which books.'''

	checkouts: Data[Checkout]
	'''Checkouts is how we track when a user takes out or returns a book.'''

	def __init__(self):
		self.books = Data(
			BOOKS_FILENAME,
			BOOKS_FIELDNAMES,
			'isbn',
			BookRelease.serialize,
			BookRelease.deserialize,
		)

		self.copies = Data(
			COPIES_FILENAME,
			COPIES_FIELDNAMES,
			'id',
			BookCopy.serialize,
			BookCopy.deserialize,
		)

		self.users = Data(
			USERS_FILENAME,
			USERS_FIELDNAMES,
			'id',
			User.serialize,
			User.deserialize,
		)

		self.checkouts = Data(
			CHECKOUTS_FILENAME,
			CHECKOUTS_FIELDNAMES,
			'id',
			Checkout.serialize,
			Checkout.deserialize,
		)

	##################################
	# READ methods for BOOK RELEASES #
	##################################

	def get_book_by_isbn(self, isbn: str) -> BookRelease:
		return self.books.read_one(isbn)

	def get_book_by_copy_id(self, copy_id: int) -> BookRelease:
		book_copy = self.get_copy_by_id(copy_id)
		return self.books.read_one(book_copy.isbn)

	def is_book_available(self, book: BookRelease) -> bool:
		book_copies = self.get_copies_by_isbn(book.isbn)
		return any(
			self.is_copy_available(copy)
			for copy in book_copies
		)

	################################
	# READ methods for BOOK COPIES #
	################################

	def get_copy_by_id(self, copy_id: int) -> BookCopy:
		return self.copies.read_one(copy_id)

	def get_available_copy_by_isbn(self, isbn: str) -> BookCopy:
		for book_copy in self.get_copies_by_isbn(isbn):
			if self.is_copy_available(book_copy):
				return book_copy
		raise BookUnavailableError('Book is currently unavailable')

	def get_copies_by_isbn(self, isbn: str) -> list[BookCopy]:
		return [book for book in self.copies.read_all() if book.isbn == isbn]

	def is_copy_available(self, copy: BookCopy) -> bool:
		checkouts = self.get_checkouts_for_copy(copy)
		return all(
			checkout.returned_date is not None
			for checkout in checkouts
		)

	##########################
	# READ methods for USERS #
	##########################

	def get_user_by_id(self, user_id: int) -> User:
		return self.users.read_one(user_id)

	##############################
	# READ methods for CHECKOUTS #
	##############################

	def get_checkouts_for_book(self, book: BookRelease) -> list[Checkout]:
		copy_ids = {
			book_copy.id
			for book_copy in self.get_copies_by_isbn(book.isbn)
		}

		return [
			checkout
			for checkout in self.checkouts.read_all()
			if checkout.copy_id in copy_ids
		]

	def get_checkouts_for_copy(self, copy: BookCopy) -> list[Checkout]:
		return [
			checkout
			for checkout in self.checkouts.read_all()
			if checkout.copy_id == copy.id
		]

	def get_checkouts_for_user(self, user: User) -> list[Checkout]:
		return [
			checkout
			for checkout in self.checkouts.read_all()
			if checkout.user_id == user.id
		]

	####################
	# MUTATION methods #
	####################

	def checkout_book(self, user: User, book: BookRelease):
		available_copy = self.get_available_copy_by_isbn(book.isbn)
		self.checkout_copy(user, available_copy)

	def checkout_copy(self, user: User, copy: BookCopy):
		today = datetime.now(tz=timezone.utc).date()
		due_date = today + timedelta(days=CHECKOUT_PERIOD)

		# Create new checkout
		checkout = Checkout(
			id=len(self.checkouts.read_all()) + 1,
			user_id=user.id,
			copy_id=copy.id,
			checkout_date=today,
			due_date=due_date,
			renewal_date=None,
			returned_date=None,
		)
		self.checkouts.write_one(checkout)

	def renew_book(self, checkout: Checkout, extension: int = 3):
		'''
		Extends the allowable checkout period of a user's book.
		The `extension` parameter is measured in days.
		'''
		if checkout.returned_date is not None:
			raise ValueError('Checkout has already been returned')
		elif checkout.renewal_date is not None:
			raise ValueError('Checkout has already been renewed once')
		elif extension <= 0:
			raise ValueError('Renewal period must be greater than zero days')

		today = datetime.now(tz=timezone.utc).date()
		due_date = today + timedelta(days=extension)
		checkout.renewal_date = today
		checkout.due_date = due_date
		self.checkouts.update_one(checkout)

	def return_book(self, checkout: Checkout):
		if checkout.returned_date is not None:
			raise ValueError('Checkout has already been returned')

		checkout.returned_date = datetime.now(tz=timezone.utc).date()
		self.checkouts.update_one(checkout)

	def pay_fines(self, user: User):
		# TODO
		# This function needs to be audited.
		# Provide feedback in comments, and determine if there are any bugs.

		# Mark fines as paid
		user.fines_due = 0
		self.users.update_one(user)

	def set_fine(self, user: User, fine: float):
		# TODO
		# This function needs to be audited.
		# Provide feedback in comments, and determine if there are any bugs.

		user.fines_due = fine
		self.users.update_one(user)

class BookUnavailableError(ValueError):
	pass
