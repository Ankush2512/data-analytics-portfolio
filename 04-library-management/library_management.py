"""A beginner-friendly command-line Library Management System.

Demo credentials:
    admin / admin123
    librarian / lib123

This is an educational project. Do not use the demo credentials for real systems.
"""
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "books.json"
CREDENTIALS = {"admin": "admin123", "librarian": "lib123"}


def load_library():
    """Load saved books; create the data file with an empty library if needed."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        save_library({})
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read the book data. Starting with an empty library.")
        return {}


def save_library(library):
    """Save all book records to a JSON file."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(library, file, indent=4, ensure_ascii=False)


def display_books(library):
    if not library:
        print("\nNo books found in the library.")
        return
    print("\n" + "-" * 78)
    print(f"{'BOOK ID':<12}{'TITLE':<28}{'AUTHOR':<22}{'STATUS':<16}")
    print("-" * 78)
    for book_id, book in sorted(library.items()):
        status = "Issued" if not book["available"] else "Available"
        print(f"{book_id:<12}{book['title'][:26]:<28}{book['author'][:20]:<22}{status:<16}")
    print("-" * 78)


def add_book(library, book_id, title, author):
    book_id = book_id.strip().upper()
    title, author = title.strip(), author.strip()
    if not book_id or not title or not author or book_id in library:
        return False
    if any(item["title"].casefold() == title.casefold() for item in library.values()):
        return False
    library[book_id] = {
        "title": title,
        "author": author,
        "available": True,
        "issued_to": None,
    }
    return True


def modify_book(library, book_id, title, author):
    book_id = book_id.strip().upper()
    if book_id not in library or not title.strip() or not author.strip():
        return False
    if any(
        key != book_id and item["title"].casefold() == title.strip().casefold()
        for key, item in library.items()
    ):
        return False
    library[book_id]["title"] = title.strip()
    library[book_id]["author"] = author.strip()
    return True


def issue_book(library, book_id, borrower):
    book_id = book_id.strip().upper()
    borrower = borrower.strip()
    if book_id not in library or not library[book_id]["available"] or not borrower:
        return False
    library[book_id]["available"] = False
    library[book_id]["issued_to"] = borrower
    return True


def return_book(library, book_id):
    book_id = book_id.strip().upper()
    if book_id not in library or library[book_id]["available"]:
        return False
    library[book_id]["available"] = True
    library[book_id]["issued_to"] = None
    return True


def view_issued_books(library):
    issued = [(book_id, book) for book_id, book in library.items() if not book["available"]]
    if not issued:
        print("\nThere are currently no issued books.")
        return
    print("\nCurrently issued books:")
    for book_id, book in sorted(issued):
        print(
            f"ID: {book_id} | Title: {book['title']} | "
            f"Borrower: {book['issued_to']}"
        )


def login():
    print("=" * 48)
    print("       LIBRARY MANAGEMENT SYSTEM")
    print("=" * 48)
    for attempt in range(3):
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        if CREDENTIALS.get(username) == password:
            print(f"\nWelcome, {username}!")
            return True
        remaining = 2 - attempt
        if remaining:
            print(f"Invalid login. Attempts remaining: {remaining}")
    print("Maximum login attempts reached. Exiting.")
    return False


def main():
    if not login():
        return

    library = load_library()
    menu = {
        "1": "View Books",
        "2": "Add a Book",
        "3": "Modify Book Details",
        "4": "Issue a Book",
        "5": "Return a Book",
        "6": "View Issued Books",
        "7": "Exit",
    }

    while True:
        print("\n" + "=" * 48)
        print("                  MAIN MENU")
        print("=" * 48)
        for key, label in menu.items():
            print(f"{key}. {label}")

        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == "1":
            display_books(library)
        elif choice == "2":
            book_id = input("Enter a unique book ID: ")
            title = input("Enter book title: ")
            author = input("Enter author name: ")
            if add_book(library, book_id, title, author):
                save_library(library)
                print("Book added successfully.")
            else:
                print("Book not added. Check the ID/title and required fields.")
        elif choice == "3":
            book_id = input("Enter the book ID to modify: ")
            title = input("Enter updated title: ")
            author = input("Enter updated author: ")
            if modify_book(library, book_id, title, author):
                save_library(library)
                print("Book details updated.")
            else:
                print("Update failed. Check the ID and ensure the title is unique.")
        elif choice == "4":
            book_id = input("Enter the book ID to issue: ")
            borrower = input("Enter borrower's name: ")
            if issue_book(library, book_id, borrower):
                save_library(library)
                print("Book issued successfully.")
            else:
                print("Issue failed. Book may not exist, may already be issued, or borrower is blank.")
        elif choice == "5":
            book_id = input("Enter the book ID to return: ")
            if return_book(library, book_id):
                save_library(library)
                print("Book returned successfully.")
            else:
                print("Return failed. Check the ID and current issue status.")
        elif choice == "6":
            view_issued_books(library)
        elif choice == "7":
            save_library(library)
            print("Library data saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main()
