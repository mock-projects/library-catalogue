class BookCopy:
	id: int
	isbn: str

	def __init__(self, id: int, isbn: str):
		self.id = id
		self.isbn = isbn

	def serialize(self) -> dict[str, str]:
		return {'id': str(self.id), 'isbn': self.isbn}

	@staticmethod
	def deserialize(row: dict[str, str]) -> 'BookCopy':
		return BookCopy(id=int(row['id']), isbn=row['isbn'])
