# Flask-Based Library Management System

## Project Overview

This project is a library management system built using Flask and SQLAlchemy, featuring:

- **Book, Customer, and Loan Management**: Add, manage, and search for books, customers, and loans.
- **Git Collaboration**: Developed collaboratively using Git.
- **ENUM**: Used to define loan types and cities.
- **Bootstrap Components**: At least three different components, including a carousel.
- **SQLAlchemy ORM**: For easy database handling.
- **Soft Deletes (CRUD)**: Entities are marked as inactive rather than deleted.
- **Searchable Fields**: Enables searching by various fields (e.g., book name, customer name).
- **Logger Integration**: Logs server activity.
- **Responsive UI**: Ensures a smooth and user-friendly experience.

## Database Structure

### Books Table
- **Id (PK)**: Unique identifier for each book.
- **Name**: Title of the book.
- **Author**: Author of the book.
- **Year Published**: Year the book was published.
- **Loan Time Type (ENUM)**: Maximum loan period:
  - **TEN_DAYS**: 10 days
  - **FIVE_DAYS**: 5 days
  - **TWO_DAYS**: 2 days
- **Is Active**: Indicates if the book is available.
- **Is Loaned**: Indicates if the book is currently loaned out.

### Customers Table
- **Id (PK)**: Unique identifier for each customer.
- **Full Name**: Name of the customer.
- **Email**: Customer's email address.
- **City (ENUM)**: City where the customer resides (e.g., Tel Aviv, Jerusalem).
- **Age**: Customer's age.
- **Is Active**: Indicates if the customer is active.

### Loans Table
- **Id (PK)**: Unique identifier for each loan.
- **Customer ID**: Foreign key linking to the Customers table.
- **Book ID**: Foreign key linking to the Books table.
- **Loan Time Type (ENUM)**: Defines loan duration.
- **Loan Date**: Date the book was loaned.
- **Return Date**: Date the book is to be returned.
- **Is Active**: Indicates if the loan is active.

### Log Table
- **Id (PK)**: Unique identifier for each log entry.
- **Timestamp**: When the log entry was created.
- **Level**: Severity level of the log (e.g., INFO, WARNING).
- **Message**: Log message content.

## Project Structure

### DAL (Data Access Layer)
The Data Access Layer (DAL) is structured into different modules, each representing a specific entity (Books, Customers, Loans).

### Client Application
The client interface includes a menu with operations such as:
- **Add a new customer/book**: Allows adding new entries.
- **Loan/Return a book**: Manages the loan lifecycle.
- **Display records**: Lists all books, customers, or loans.
- **Display late loans**: Lists overdue loans.
- **Find records**: Search books or customers by their name.
- **Soft Delete**: Mark records as inactive instead of deleting them.

### Frontend and Bootstrap Components
The web application uses **Bootstrap** for styling and responsiveness, featuring at least three components:
- **Navbar**: For easy navigation.
- **Carousel**: To display book covers dynamically.
- **Modals**: For adding new records.

### Logging
A **Logger** is integrated into the server for tracking key events and requests, making debugging easier.

## Unit Tests
Unit tests are implemented to ensure functionality, including:
- CRUD operations (create, read, update, and mark as inactive).
- Searching by different fields.
- Loan and return operations.

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/library-management-system.git
   cd library-management-system
