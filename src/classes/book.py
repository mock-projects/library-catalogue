class Book:
	id: int
	isbn: str
	title: str
	author: str
	year: int

	def __init__(self, id: int, isbn: str, title: str, author: str, year: int):
		self.id = id
		self.isbn = isbn
		self.title = title
		self.author = author
		self.year = year

	def __str__(self):
		return f'ID {self.id}: "{self.title}" by {self.author}'

	def serialize(self) -> dict[str, str]:
		return {
			'id': str(self.id),
			'isbn': self.isbn,
			'title': self.title,
			'author': self.author,
			'year': str(self.year),
		}

	@staticmethod
	def deserialize(row: dict[str, str]) -> 'Book':
		return Book(
			id=int(row['id']),
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
