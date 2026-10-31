import os

from datetime import datetime, timedelta, timezone
from classes.book_release import BookRelease
from classes.checkout import Checkout
from classes.data import Data
from classes.user import User

# 21-day checkout period
CHECKOUT_PERIOD = 21

# Obtain the data
DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

BOOKS_FILENAME = os.path.join(DATA_DIRECTORY, 'book_releases.csv')
USERS_FILENAME = os.path.join(DATA_DIRECTORY, 'users.csv')
CHECKOUTS_FILENAME = os.path.join(DATA_DIRECTORY, 'checkouts.csv')

BOOKS_FIELDNAMES = [
	'id',
	'isbn',
	'title',
	'author',
	'year',
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
	'book_id',
	'checkout_date',
	'due_date',
	'renewal_date',
	'returned_date',
]

class CatalogData:
	'''Stores all data for the library catalog.'''

	books: Data[BookRelease]
	users: Data[User]
	checkouts: Data[Checkout]

	def __init__(self):
		self.books = Data(
			BOOKS_FILENAME,
			BOOKS_FIELDNAMES,
			'id',
			BookRelease.serialize,
			BookRelease.deserialize,
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

	##########################
	# READ methods for BOOKS #
	##########################

	def get_book_by_id(self, book_id: int) -> BookRelease:
		return self.books.read_one(book_id)

	def get_books_by_isbn(self, isbn: str) -> list[BookRelease]:
		return [book for book in self.books.read_all() if book.isbn == isbn]

	def is_book_available(self, book: BookRelease) -> bool:
		checkouts = self.get_checkouts_for_book(book)
		return all(checkout.returned_date is not None for checkout in checkouts)

	##########################
	# READ methods for USERS #
	##########################

	def get_user_by_id(self, user_id: int) -> User:
		return self.users.read_one(user_id)

	##############################
	# READ methods for CHECKOUTS #
	##############################

	def get_checkouts_for_book(self, book: BookRelease) -> list[Checkout]:
		return [
			checkout
			for checkout in self.checkouts.read_all()
			if checkout.book_id == book.id
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
		if not self.is_book_available(book):
			raise BookUnavailableError('Book is currently unavailable')
		today = datetime.now(tz=timezone.utc).date()
		due_date = today + timedelta(days=CHECKOUT_PERIOD)

		# Create new checkout
		checkout = Checkout(
			id=len(self.checkouts.read_all()) + 1,
			user_id=user.id,
			book_id=book.id,
			checkout_date=today,
			due_date=due_date,
			renewal_date=None,
			returned_date=None,
		)
		self.checkouts.write_one(checkout)

	def renew_book(self, checkout: Checkout):
		'''
		Extends the allowable checkout period of a user's book.
		'''
		if checkout.returned_date is not None:
			raise ValueError('Checkout has already been returned')
		elif checkout.renewal_date is not None:
			raise ValueError('Checkout has already been renewed once')

		checkout.renewal_date = datetime.now(tz=timezone.utc).date()
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
