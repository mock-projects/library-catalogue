'''Represents a release of a title, unique by isbn only.'''
class BookRelease:
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
		return f'ISBN {self.isbn}: "{self.title}" by {self.author}'

	def serialize(self) -> dict[str, str]:
		return {
			'isbn': self.isbn,
			'title': self.title,
			'author': self.author,
			'year': str(self.year),
		}

	@staticmethod
	def deserialize(row: dict[str, str]) -> 'BookRelease':
		return BookRelease(
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
