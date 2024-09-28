import unittest
import json
from app import app, db, Books, Customers, Loans, LoanType, City

class LibraryAppTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a test client and a new database for each test."""
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()  # Create the tables in the test database
            # Seed the database with initial data for testing
            self.seed_database()

    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def seed_database(self):
        """Seed the database with initial data for testing."""
        initial_books = [
            Books(name='1984', author='George Orwell', year_published=1949, loan_time_type=LoanType.TEN_DAYS),
            Books(name='Brave New World', author='Aldous Huxley', year_published=1932, loan_time_type=LoanType.FIVE_DAYS)
        ]
        initial_customers = [
            Customers(full_name='John Doe', email='john@example.com', city=City.TEL_AVIV, age=30)
        ]
        db.session.bulk_save_objects(initial_books)
        db.session.bulk_save_objects(initial_customers)
        db.session.commit()

    def test_create_book(self):
        """Test creating a new book."""
        response = self.app.post('/book', json={
            'name': 'Fahrenheit 451',
            'author': 'Ray Bradbury',
            'year_published': 1953,
            'loan_time_type': 'TEN_DAYS'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('Fahrenheit 451', data['name'])

    def test_create_customer(self):
        """Test creating a new customer."""
        response = self.app.post('/customer', json={
            'full_name': 'Alice Wonderland',
            'email': 'alice@example.com',
            'city': 'Tel Aviv',
            'age': 25
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('Alice Wonderland', data['full_name'])

    def test_search_book(self):
        """Test searching for a book."""
        response = self.app.post('/book/search', json={'name': '1984'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], '1984')

    def test_toggle_book_status(self):
        """Test toggling a book's status."""
        response = self.app.put('/book/status', json={'name': '1984'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('inactive', data['message'])  # Assuming it toggled to inactive

    def test_delete_book(self):
        """Test deleting a book."""
        response = self.app.delete('/book/1984')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Book '1984' deleted successfully.", json.loads(response.data)['message'])

    def test_create_loan(self):
        """Test creating a loan."""
        response = self.app.post('/loan', json={
            'customer_id': 1,
            'book_id': 1,
            'loan_time_type': 'TEN_DAYS'
        })
        self.assertEqual(response.status_code, 201)

    def test_return_loan(self):
        """Test returning a loan."""
        self.app.post('/loan', json={
            'customer_id': 1,
            'book_id': 1,
            'loan_time_type': 'TEN_DAYS'
        })
        response = self.app.post('/return/1')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
