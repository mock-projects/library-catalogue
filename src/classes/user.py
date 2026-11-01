class User:
	id: int
	first_name: str
	last_name: str
	email: str
	fines_due: float
	fines_paid: float

	def __init__(
		self,
		id: int,
		first_name: str,
		last_name: str,
		email: str,
		fines_due: float = 0.0,
		fines_paid: float = 0.0,
	):
		self.id = id
		self.first_name = first_name
		self.last_name = last_name
		self.email = email
		self.fines_due = fines_due
		self.fines_paid = fines_paid

	def __str__(self):
		return f'{self.first_name} {self.last_name}'

	def serialize(self) -> dict[str, str]:
		return {
			'id': str(self.id),
			'first_name': self.first_name,
			'last_name': self.last_name,
			'email': self.email,
			'fines_due': str(self.fines_due),
			'fines_paid': str(self.fines_paid),
		}

	@staticmethod
	def deserialize(row: dict[str, str]) -> 'User':
		return User(
			id=int(row['id']),
			first_name=row['first_name'],
			last_name=row['last_name'],
			email=row['email'],
			fines_due=float(row['fines_due']),
			fines_paid=float(row['fines_paid']),
		)

	def is_query_match(self, query: str) -> bool:
		name = f'{self.first_name}{self.last_name}'.replace(' ', '').lower()
		email = self.email.replace(' ', '').lower()
		query = query.replace(' ', '').lower()
		return query in name or query in email or query == str(self.id)
