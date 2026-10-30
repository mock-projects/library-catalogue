from classes.catalog import CatalogData
from utilities.search import search_catalog
from utilities.status import show_status_page
from utilities.users import manage_user
from utilities.util import print_headline, prompt_for_choice

def main():
	# Load all data about books and users
	catalog = CatalogData()

	# Options supported by the CLI
	options = [
		('book', 'Search for a book'),
		('user', 'Search for a user'),
		('status', 'Show status page'),
		('exit', 'Exit the program'),
	]

	# Loop until the user chooses to exit program
	while True:
		print_headline('Welcome to the Byte County Public Library CLI!')
		choice = prompt_for_choice('Available actions:', options)

		# Quit program
		if choice == 'exit':
			print('Exiting Byte County Public Library CLI...')
			break

		elif choice == 'book':
			search_catalog(catalog)

		elif choice == 'user':
			manage_user(catalog)

		elif choice == 'status':
			show_status_page(catalog)

if __name__ == '__main__':
	main()
