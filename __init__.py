from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Import models and routes
from .app import Books, Customers, log_message  # Adjust as necessary based on your actual structure

# Database seeding
def seed_database():
    """Seed the database with initial data."""
    db.create_all()  # Create all tables if they don't exist

    # Check if there are already books in the database
    if Books.query.count() == 0:
        # Add some initial books
        initial_books = [
            Books(name='1984', author='George Orwell', year_published=1949, loan_time_type=LoanType.TEN_DAYS),
            Books(name='Brave New World', author='Aldous Huxley', year_published=1932, loan_time_type=LoanType.FIVE_DAYS),
            Books(name='The Catcher in the Rye', author='J.D. Salinger', year_published=1951, loan_time_type=LoanType.TWO_DAYS)
        ]
        db.session.bulk_save_objects(initial_books)
        db.session.commit()
        log_message('INFO', "Database seeded with initial books.")

    # Check if there are already customers in the database
    if Customers.query.count() == 0:
        # Add some initial customers
        initial_customers = [
            Customers(full_name='John Doe', email='john@example.com', city=City.TEL_AVIV, age=30),
            Customers(full_name='Jane Smith', email='jane@example.com', city=City.JERUSALEM, age=28)
        ]
        db.session.bulk_save_objects(initial_customers)
        db.session.commit()
        log_message('INFO', "Database seeded with initial customers.")

if __name__ == '__main__':
    with app.app_context():
        seed_database()  # Seed the database when starting the app
    app.run(debug=True)