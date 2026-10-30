'''Utility functions used by the application.'''

import datetime
from collections.abc import Callable, Sequence
from typing import Optional, TypeVar

T = TypeVar('T')

def print_headline(content: str):
	length = len(content)
	print()
	print('=' * (length + 6))
	print(f'|  {" " * length}  |')
	print(f'|  {content}  |')
	print(f'|  {" " * length}  |')
	print('=' * (length + 6))
	print()

def print_subheadline(content: str):
	length = len(content)
	print()
	print('-' * (length + 4))
	print(f'| {content} |')
	print('-' * (length + 4))
	print()

def string_to_date(date_string: str) -> datetime.date:
	year, month, day = date_string.split('-')
	return datetime.date(int(year), int(month), int(day))

def prompt_for_confirmation(prompt: str) -> bool:
	response = input(f'{prompt} (y/n): ').strip().lower()
	return response == 'y'

def prompt_for_choice(prompt: str, options: Sequence[tuple[T, str]]) -> Optional[T]:
	print(prompt)
	for i, (_, title) in enumerate(options):
		print(f'({i + 1}) {title}')
	# Repeat until a valid choice is selected
	while True:
		choice = input(f'Choose an option: ').strip()
		print()
		if choice.isdigit():
			index = int(choice) - 1
			# If the choice is valid, return the corresponding option identifier
			if 0 <= index < len(options):
				return options[index][0]
		print('Invalid option, choose again.')

def search_for_choice(
	prompt: str, options: list[T], is_match: Callable[[T, str], bool]
) -> Optional[T]:
	# No options available
	if len(options) == 0:
		return None

	while True:
		# Prompt for query
		query = input(f'{prompt}: ')
		print()
		matches = [option for option in options if is_match(option, query)]

		# If no matches, try again
		if not matches:
			print('No results found matching query.')
			continue

		# If only one match, return it
		if len(matches) == 1:
			return matches[0]

		# If multiple matches, prompt user to select one
		choice = prompt_for_choice(
			'Matches:',
			[(match, str(match)) for match in matches] + [(None, 'Search again')],
		)

		# User didn't want any of the options
		if choice is None:
			continue

		return choice
