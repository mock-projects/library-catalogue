import csv
from collections.abc import Callable
from typing import Any, Generic, TypeVar

T = TypeVar('T')

class Data(Generic[T]):
	'''Represents a model that is persisted across runs of the program.'''

	# Where to persist data
	filename: str

	# Properties of each persisted object
	properties: list[str]

	# Property name to use as identifier for each object
	id: str

	# Convert an object to a dictionary mapping properties to values serialized as strings
	serialize: Callable[[T], dict[str, str]]

	# Convert a dictionary of properties/values to a deserialized object
	deserialize: Callable[[dict[str, str]], T]

	def __init__(
		self,
		filename: str,
		properties: list[str],
		id: str,
		serialize: Callable[[T], dict[str, str]],
		deserialize: Callable[[dict[str, str]], T],
	):
		self.filename = filename
		self.properties = properties
		self.id = id
		self.serialize = serialize
		self.deserialize = deserialize

	def read_all(self) -> list[T]:
		'''Read all persisted objects from the data file.'''
		with open(self.filename, 'r') as file:
			reader = csv.DictReader(file)
			return [self.deserialize(row) for row in reader]

	def read_one(self, id: Any) -> T:
		'''Read a single persisted object from the data file by ID.'''
		with open(self.filename, 'r') as file:
			reader = csv.DictReader(file)
			for row in reader:
				obj = self.deserialize(row)
				if getattr(obj, self.id) == id:
					return obj
		raise ValueError(f'Object with ID {id} not found in {self.filename}')

	def write_all(self, objects: list[T]):
		'''Write a list of objects to the data file.'''
		with open(self.filename, 'w') as file:
			writer = csv.DictWriter(file, fieldnames=self.properties)
			writer.writeheader()
			writer.writerows([self.serialize(obj) for obj in objects])

	def write_one(self, object: T):
		'''Write a single object to end of the data file.'''
		with open(self.filename, 'a') as file:
			writer = csv.DictWriter(file, fieldnames=self.properties)
			writer.writerow(self.serialize(object))

	def update_one(self, object: T):
		'''Update an object in the data file.'''
		objects = self.read_all()
		object_id = getattr(object, self.id)
		index = next(
			(i for i, obj in enumerate(objects) if getattr(obj, self.id) == object_id),
			None,
		)
		if index is not None:
			objects[index] = object
		else:
			raise ValueError(f'Object with ID {object_id} not found in {self.filename}')
		self.write_all(objects)
