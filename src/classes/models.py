from datetime import date
from typing import Optional

from utilities.util import string_to_date

class Book:
	isbn: str
	title: str
	author: str
	year: int

	def __init__(self, isbn: str, title: str, author: str, year: int):
		self.isbn = isbn
		self.title = title
		self.author = author
		self.year = year

	def __str__(self):
		return f'"{self.title}" by {self.author}'

	def serialize(self) -> dict[str, str]:
		return {
			'isbn': self.isbn,
			'title': self.title,
			'author': self.author,
			'year': str(self.year),
		}

	@staticmethod
	def deserialize(row: dict[str, str]) -> 'Book':
		return Book(
			isbn=row['isbn'],
			title=row['title'],
			author=row['author'],
			year=int(row['year']),
		)

	def is_query_match(self, query: str) -> bool:
		title = self.title.replace(' ', '').lower()
		author = self.author.replace(' ', '').lower()
		query = query.replace(' ', '').lower()
		return query in title or query in author or query in self.isbn

class User:
	id: int
	first_name: str
	last_name: str
	email: str
	fines_due: float

	def __init__(
		self, id: int, first_name: str, last_name: str, email: str, fines_due: float
	):
		self.id = id
		self.first_name = first_name
		self.last_name = last_name
		self.email = email
		self.fines_due = fines_due

	def __str__(self):
		return f'{self.first_name} {self.last_name}'

	def serialize(self) -> dict[str, str]:
		return {
			'id': str(self.id),
			'first_name': self.first_name,
			'last_name': self.last_name,
			'email': self.email,
			'fines_due': str(self.fines_due),
		}

	@staticmethod
	def deserialize(row: dict[str, str]) -> 'User':
		return User(
			id=int(row['id']),
			first_name=row['first_name'],
			last_name=row['last_name'],
			email=row['email'],
			fines_due=float(row['fines_due']),
		)

	def is_query_match(self, query: str) -> bool:
		name = f'{self.first_name}{self.last_name}'.replace(' ', '').lower()
		email = self.email.replace(' ', '').lower()
		query = query.replace(' ', '').lower()
		return query in name or query in email or query == str(self.id)

class Checkout:
	id: int
	user_id: int
	isbn: str
	checkout_date: date
	due_date: date
	returned_date: Optional[date]

	def __init__(
		self,
		id: int,
		user_id: int,
		isbn: str,
		checkout_date: date,
		due_date: date,
		returned_date: Optional[date],
	):
		self.id = id
		self.user_id = user_id
		self.isbn = isbn
		self.checkout_date = checkout_date
		self.due_date = due_date
		self.returned_date = returned_date

	def serialize(self) -> dict[str, str]:
		return {
			'id': str(self.id),
			'user_id': str(self.user_id),
			'isbn': self.isbn,
			'checkout_date': self.checkout_date.strftime('%Y-%m-%d'),
			'due_date': self.due_date.strftime('%Y-%m-%d'),
			'returned_date': (
				self.returned_date.strftime('%Y-%m-%d') if self.returned_date else ''
			),
		}

	@staticmethod
	def deserialize(row: dict[str, str]) -> 'Checkout':
		return Checkout(
			id=int(row['id']),
			user_id=int(row['user_id']),
			isbn=row['isbn'],
			checkout_date=string_to_date(row['checkout_date']),
			due_date=string_to_date(row['due_date']),
			returned_date=string_to_date(row['returned_date']),
		)

	def __str__(self):
		return_string = (
			f'returned on {self.returned_date}'
			if self.returned_date
			else f'due by {self.due_date}'
		)
		return f'User {self.user_id} checked out book {self.isbn} on {self.checkout_date}, {return_string}'
