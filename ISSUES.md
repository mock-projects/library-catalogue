# BOOKS WITH MULTIPLES
Why the system is buggy with the book, "Alice's Adventures in Wonderland":
- When using the CLI to search the library's catalog for "Alice", the book shows up twice in the CLI's output list. This is probably not the best user experience, especially if a library had dozens of the same book in the catalog.
	- Selecting any of the duplicate options, brings you to the same list summary of the book's checkout history. This is problematic, as you would expect separate copies to have different checkout histories.
	- However, this shared checkout history is also itself problematic, as it creates an amalgamation of checkout histories amongst all copies of the book (for example, a book with three copies might be "checked out" thrice in a row, which is impossible to do with unique copies of a book).
	- This is likely because the system lists out the books by their ID in the CSV file, and not their ISBN.
- When using the CLI to view the system's checked out books, this title appears correctly along with with its borrowed and due dates for the relevant user.
	- This is something to watch, as the system lists out these books by their ISBN and not their ID. It is not possible to know which specific book ID is checked out, only the ISBN.

Why the system breaks with multiple books of the same ISBN:
- The system breaks because certain parts of the CLI rely upon a book's ID, where two books of the same ISBN can have different IDs. Other parts of the system rely upon a book's ISBN, which does not distinguish the difference between multiples of the same book.

How we should fix these issues:
- Throughout the system, we should carefully consider whether or not an ISBN or an ID should be used. For example, a book's description should be linked to its ISBN, but its checked out status should be linked to its unique ID.
- It may be pertinent to have each specific `Book` (based on unique ISBNs) in our database know about each of its unique `BookCopy` (based on unique IDs) in our catalogue. If we're representing the model in-memory, then we can have a `Book` class and a seperate `BookCopy` class.
