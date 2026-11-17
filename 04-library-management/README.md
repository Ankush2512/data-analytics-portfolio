# Project 04 – Library Management System (Python)

## Overview
A beginner-friendly, menu-driven command-line application for a librarian to manage a small book catalogue. It demonstrates Python fundamentals through a practical workflow.

## Features
- Librarian login with a maximum of three attempts.
- View all books and their availability.
- Add books with a unique book ID and title.
- Modify a book's title and author.
- Issue available books and record the borrower's name.
- Return issued books.
- View the list of currently issued books.
- Save and reload book records using a local JSON file.

## Technology
- Python 3
- Built-in modules: `json`, `pathlib`
- No external packages required.

## Run the project
From the project directory:

```bash
python library_management.py
```

## Demo login
- Username: `admin` | Password: `admin123`
- Username: `librarian` | Password: `lib123`

These credentials are hard-coded for this learning exercise only. This is not a production authentication system; passwords are not securely hashed.

## Data storage
The application reads and writes `data/books.json`. The JSON file is included with a few sample records. Changes made through the application are saved locally when an operation succeeds and when the user exits.

## Project structure
```text
04-library-management/
├── README.md
├── library_management.py
├── data/
│   └── books.json
└── tests/
    └── test_library.py
```

## Concepts demonstrated
Variables, dictionaries, functions, conditionals, loops, user input, validation, sorting, exception handling, JSON file handling, and basic unit testing.

## Validation
Run the automated tests from this folder:

```bash
python -m unittest discover -s tests -v
```

## Scope and limitations
This is a self-directed educational portfolio project based on a Python mini-project brief. It is not a deployed library system and does not represent professional library-management experience. The demo login is intentionally simple. The program is designed for a single local user and does not support simultaneous users, due dates, fines, or audit history.

## Possible future improvements
Add due dates and overdue tracking, a graphical interface, stronger authentication, and a database such as SQLite.
