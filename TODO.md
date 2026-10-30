> *This file was generated using AI.*

# Library Catalogue TODO
## Current status
The project is a working CLI prototype for a library catalog, but the data model and checkout logic still assume a single record per ISBN. This is causing problems when multiple copies of the same book exist, as documented in `ISSUES.md` and confirmed by duplicate ISBN rows in `src/data/books.csv`.

## High-priority bugs to fix
### 1. Separate book metadata from physical copies
- Problem: the system treats the `isbn` as the primary identity for both the book record and the individual copy being checked out.
- Why it matters: duplicate ISBNs create repeated catalog entries and mix checkout history across multiple copies.
- Suggested fix: introduce a `Book` model for metadata (title, author, ISBN) and a `BookCopy`/inventory model for unique IDs tied to each physical copy.
- Related files: `src/classes/catalog.py`, `src/classes/book.py`, `src/data/books.csv`

### 2. Fix availability checks for duplicate ISBNs
- Problem: `CatalogData.is_book_available()` checks whether all historical checkouts for a given ISBN were returned. This treats all copies as one shared item.
- Why it matters: if one copy is checked out, the entire title may appear unavailable even when another copy is available.
- Suggested fix: evaluate availability by unique copy ID, not only ISBN.

### 3. Correct renewal behavior
- Problem: `CatalogData.renew_book()` sets `renewal_date` but does not extend `due_date`.
- Why it matters: a renewed book still appears due on the original date, so the renewal effectively does nothing.
- Suggested fix: update `due_date` by the renewal policy and enforce a single renewal rule.

### 4. Fix fine accumulation logic
- Problem: `CatalogData.set_fine()` replaces the user's current fine balance instead of adding to it.
- Why it matters: returning multiple overdue books or additional fines can overwrite prior balances instead of accumulating correctly.
- Suggested fix: add the new fine to `user.fines_due` rather than assigning a new value.

### 5. Prevent mistaken checkout history aggregation
- Problem: status pages and analytics aggregate by title/ISBN rather than by unique copy.
- Why it matters: historical records become inaccurate when multiple copies share the same ISBN.
- Suggested fix: track checkouts by copy ID and report on copy-specific history where needed.

### 6. Validate CSV data assumptions
- Problem: `Data.write_one()` appends rows to CSV files without checking for a header or data integrity, and IDs are generated based on row count.
- Why it matters: this can create fragile behavior when data is edited manually or when records are removed or duplicated.
- Suggested fix: add validation and safer ID generation; consider using a persistent counter or a UUID-backed identifier where appropriate.

## Additional issues and risk areas
### Search and selection UX
- The search logic can match on empty queries because `query in ...` is true for an empty string.
- The CLI does not clearly distinguish between catalog entries and physical copies, which makes the user experience confusing.

### Analytics and reporting
- `print_book_analytics()` groups metrics by book title, which blurs together titles with identical ISBNs and multiple copies.
- Average checkout duration and counts should be computed by unique copy or by specific ISBN metadata, not just title.

### User management and fine payment
- `checkout_book()` allows a user with outstanding fines to pay them interactively before checking out a new book, but it does not clearly confirm whether the fine is being paid in full or being added to an existing balance.
- The flow should also protect against negative values or invalid fine amounts.

## Improvements to plan
### Data model cleanup
- Introduce `Book` and `BookCopy` classes.
- Move identifier logic to unique inventory IDs while preserving ISBN for metadata.
- Add migration logic for existing CSV data.

### Validation and reliability
- Add tests for: duplicate ISBNs, checkout availability, renewal behavior, overdue fines, and multiple-user checks.
- Add input validation for email, IDs, dates, and fine amounts.
- Guard against duplicate IDs in CSV persistence.

### User experience improvements
- Display unique copy IDs when multiple copies exist.
- Show whether a title has multiple available copies rather than a single on/off availability flag.
- Improve error messages for invalid selections, overdue books, and fine payment states.

### Maintainability
- Document the domain model for books, copies, users, and checkouts.
- Centralize policy decisions (checkout period, fine calculation, renewal rules) into clearly named configuration constants.
- Refactor repeated code in `search.py` and `users.py` for consistent validation and output formatting.

## Suggested priority order
1. Fix duplicate ISBN / copy identity bug
2. Fix book availability logic
3. Fix renewal and overdue fine calculation
4. Add validation and tests
5. Improve analytics and CLI UX

## Summary
The project is close to functional for single-copy inventory, but it is not safe for real library scenarios where multiple copies of the same title exist. The main design issue is conflating `ISBN` (book description) with a unique copy ID (checkout item), and that should be the first architectural fix.
