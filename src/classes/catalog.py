import datetime
import os

from classes.data import Data
from classes.models import Book, Checkout, User
from utilities.util import string_to_date

# 21-day checkout period
CHECKOUT_PERIOD = 21

DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
BOOKS_FILENAME = os.path.join(DATA_DIRECTORY, 'books.csv')
USERS_FILENAME = os.path.join(DATA_DIRECTORY, 'users.csv')
CHECKOUTS_FILENAME = os.path.join(DATA_DIRECTORY, 'checkouts.csv')

BOOKS_FIELDNAMES = ['isbn', 'title', 'author', 'year']
USERS_FIELDNAMES = ['id', 'first_name', 'last_name', 'email', 'fines_due']
CHECKOUTS_FIELDNAMES = [
	'id',
	'user_id',
	'isbn',
	'checkout_date',
	'due_date',
	'returned_date',
]

class CatalogData:
	'''Stores all data for the library catalog.'''

	books: Data[Book]
	users: Data[User]
	checkouts: Data[Checkout]

	def __init__(self):
		self.books = Data(
			BOOKS_FILENAME, BOOKS_FIELDNAMES, 'isbn', Book.serialize, Book.deserialize
		)
		self.users = Data(
			USERS_FILENAME, USERS_FIELDNAMES, 'id', User.serialize, User.deserialize
		)
		self.checkouts = Data(
			CHECKOUTS_FILENAME,
			CHECKOUTS_FIELDNAMES,
			'id',
			Checkout.serialize,
			Checkout.deserialize,
		)

	def get_book_by_isbn(self, isbn: str) -> Book:
		return self.books.read_one(isbn)

	def get_user_by_id(self, user_id: int) -> User:
		return self.users.read_one(user_id)

	def get_checkouts_for_user(self, user: User) -> list[Checkout]:
		return [
			checkout
			for checkout in self.checkouts.read_all()
			if checkout.user_id == user.id
		]

	def get_checkouts_for_book(self, book: Book) -> list[Checkout]:
		return [
			checkout
			for checkout in self.checkouts.read_all()
			if checkout.isbn == book.isbn
		]

	def is_book_available(self, book: Book) -> bool:
		checkouts = self.get_checkouts_for_book(book)
		return all(checkout.returned_date is not None for checkout in checkouts)

	def checkout_book(self, user: User, book: Book):
		if not self.is_book_available(book):
			raise BookUnavailableException
		today = datetime.date.today()
		due_date = today + datetime.timedelta(days=CHECKOUT_PERIOD)

		# Create new checkout
		checkout = Checkout(
			id=len(self.checkouts.read_all()) + 1,
			user_id=user.id,
			isbn=book.isbn,
			checkout_date=today,
			due_date=due_date,
			returned_date=None,
		)
		self.checkouts.write_one(checkout)

	def return_book(self, checkout: Checkout):
		if checkout.returned_date is not None:
			raise Exception('Checkout has already been returned')

		checkout.returned_date = datetime.date.today()
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

class BookUnavailableException(Exception):
	pass
