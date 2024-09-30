import unittest
from flask import Flask
from app import app, db, User, Books, Customers, Loans  # Adjust imports as necessary

class LibraryManagementSystemTestCase(unittest.TestCase):

    def setUp(self):
        """Create a test client and set up the database."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()  # Create the database tables

        # Create a test user
        self.test_user = User(username='testuser')
        self.test_user.set_password('testpass')  # Assuming you have a method to set password
        db.session.add(self.test_user)
        db.session.commit()

        # Log in to get a token
        response = self.app.test_client().post('/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        self.token = response.json['access_token']


    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()  # Drop all tables
        self.app_context.pop()

    def test_create_user(self):
        """Test creating a new user."""
        response = self.app.test_client().post('/user', json={
            'username': 'newuser',
            'password': 'newpass'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'User created successfully', response.data)

    def test_create_book(self):
        """Test creating a new book."""
        response = self.app.test_client().post('/book', json={
            'name': '1984',
            'author': 'George Orwell',
            'year_published': 1949,
            'loan_time_type': 'TEN_DAYS'
        }, headers={'Authorization': f'Bearer {self.token}'})  # Include the token
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'1984', response.data)

    def test_search_book(self):
        """Test searching for a book."""
        self.app.test_client().post('/book', json={
            'name': '1984',
            'author': 'George Orwell',
            'year_published': 1949,
            'loan_time_type': 'TEN_DAYS'
        }, headers={'Authorization': f'Bearer {self.token}'})  # Include the token

        response = self.app.test_client().post('/book/search', json={'name': '1984'}, headers={'Authorization': f'Bearer {self.token}'})  # Include the token
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'1984', response.data)

if __name__ == '__main__':
    unittest.main()
