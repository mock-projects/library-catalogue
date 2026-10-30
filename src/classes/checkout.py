from datetime import date

from utilities.util import string_to_date

class Checkout:
	id: int
	user_id: int
	book_id: int
	checkout_date: date
	due_date: date
	renewal_date: date | None
	returned_date: date | None

	def __init__(
		self,
		id: int,
		user_id: int,
		book_id: int,
		checkout_date: date,
		due_date: date,
		renewal_date: date | None,
		returned_date: date | None,
	):
		self.id = id
		self.user_id = user_id
		self.book_id = book_id
		self.checkout_date = checkout_date
		self.due_date = due_date
		self.renewal_date = renewal_date
		self.returned_date = returned_date

	def serialize(self) -> dict[str, str]:
		return {
			'id': str(self.id),
			'user_id': str(self.user_id),
			'book_id': str(self.book_id),
			'checkout_date': self.checkout_date.strftime('%Y-%m-%d'),
			'due_date': self.due_date.strftime('%Y-%m-%d'),
			'renewal_date': (
				self.renewal_date.strftime('%Y-%m-%d') if self.renewal_date else ''
			),
			'returned_date': (
				self.returned_date.strftime('%Y-%m-%d') if self.returned_date else ''
			),
		}

	@staticmethod
	def deserialize(row: dict[str, str]) -> 'Checkout':
		return Checkout(
			id=int(row['id']),
			user_id=int(row['user_id']),
			book_id=int(row['book_id']),
			checkout_date=string_to_date(row['checkout_date']),
			due_date=string_to_date(row['due_date']),
			renewal_date=(
				string_to_date(row['renewal_date']) if row['renewal_date'] else None
			),
			returned_date=(
				string_to_date(row['returned_date']) if row['returned_date'] else None
			),
		)

	def __str__(self):
		return_string = (
			f'returned on {self.returned_date}'
			if self.returned_date
			else f'due by {self.due_date}'
		)
		return f'User {self.user_id} checked out book {self.book_id} on {self.checkout_date}, {return_string}'
