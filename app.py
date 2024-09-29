from enum import Enum
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity
import bcrypt  # For password hashing


# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

# Initialize SQLAlchemy
db = SQLAlchemy(app)
CORS(app)

# Initialize JWT Manager
jwt = JWTManager(app)

# Token Blacklist Check
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']  # Get the token ID
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    return token is not None  # Return True if the token is blacklisted

# Define Enums for City and Loan Type
class City(Enum):
    TEL_AVIV = "Tel Aviv"
    JERUSALEM = "Jerusalem"
    HAIFA = "Haifa"
    EILAT = "Eilat"

class LoanType(Enum):
    TEN_DAYS = 10
    FIVE_DAYS = 5
    TWO_DAYS = 2

# Define models for User, Books, Customers, Loans, and Log

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class TokenBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False)  # JWT ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TokenBlacklist {self.jti}>'


class Books(db.Model):
    """Model representing a book in the library."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    loan_time_type = db.Column(db.Enum(LoanType), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_loaned = db.Column(db.Boolean, default=False)

    def to_dict(self):
        """Convert the Book object to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'author': self.author,
            'year_published': self.year_published,
            'loan_time_type': self.loan_time_type.name,
            'is_active': self.is_active,
            'is_loaned': self.is_loaned
        }

class Customers(db.Model):
    """Model representing a customer of the library."""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    city = db.Column(db.Enum(City), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        """Convert the Customer object to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'city': self.city.name,
            'age': self.age,
            'is_active': self.is_active
        }

class Loans(db.Model):
    """Model representing a loan of a book."""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_time_type = db.Column(db.Enum(LoanType), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # New column for loan status

    def to_dict(self):
        """Convert the Loan object to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'book_id': self.book_id,
            'loan_time_type': self.loan_time_type.name,
            'loan_date': self.loan_date.isoformat(),
            'return_date': self.return_date.isoformat(),
            'is_active': self.is_active
        }

class Log(db.Model):
    """Model for logging messages."""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(10), nullable=False)
    message = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """Return a string representation of the Log entry."""
        return f'<Log {self.id}: {self.level} - {self.message}>'

def log_message(level, message):
    """Log a message to the Log model."""
    new_log = Log(level=level, message=message)
    db.session.add(new_log)
    db.session.commit()

def toggle_status(model_class, identifier_field, identifier_value):
    """Toggle the active status of a specific record."""
    record = model_class.query.filter(getattr(model_class, identifier_field) == identifier_value).first()
    if record is None:
        log_message('WARNING', f"{model_class.__name__} not found: {identifier_value}")
        abort(404, description=f"{model_class.__name__} not found.")

    record.is_active = not record.is_active  # Toggle active status
    db.session.commit()

    log_message('INFO', f"Toggled status for {model_class.__name__}: {identifier_value} (Active: {record.is_active})")
    return jsonify({'message': f"{model_class.__name__} '{identifier_value}' status updated to {'active' if record.is_active else 'inactive'}."}), 200

def search_record(model_class, identifier_field, identifier_value):
    """Search for a specific record in the database using case-insensitive matching."""
    record = model_class.query.filter(getattr(model_class, identifier_field).ilike(f'%{identifier_value}%')).first()
    
    if record is None:
        log_message('WARNING', f"{model_class.__name__} not found: {identifier_value}")
        abort(404, description=f"{model_class.__name__} not found.")

    log_message('INFO', f"Found {model_class.__name__}: {identifier_value}")
    return jsonify(record.to_dict()), 200  # Assuming to_dict() converts the model to a dictionary

def validate_fields(data, required_fields, enum_fields=None):
    # Check for required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        log_message('WARNING', f"Missing required fields: {missing_fields}")
        abort(400, description=f"Missing required fields: {', '.join(missing_fields)}")

    # Validate enum fields
    if enum_fields:
        for field, enum_class in enum_fields.items():
            if field in data and data[field] not in enum_class.__members__:
                log_message('ERROR', f"Invalid value for {field}: {data[field]}")
                abort(400, description=f"Invalid value for {field}. Must be one of: {', '.join(enum_class.__members__.keys())}.")

def get_records(model_class, status):
    """Retrieve records based on specified status: active, deactivated, late or all."""
    if status not in ['active', 'deactivated', 'all', 'late']:
        log_message('WARNING', f"Invalid status parameter provided for {model_class.__name__.lower()}s.")
        abort(400, description="Invalid status parameter. Use 'active', 'deactivated', or 'all'('late' == loans only).")

    if status == 'late':
        current_time = datetime.utcnow()
        records = model_class.query.filter(Loans.return_date>current_time).all()
        log_message('INFO', f"Retrieved all {model_class.__name__.lower()}s.")

    elif status == 'all':
        records = model_class.query.all()
        log_message('INFO', f"Retrieved all {model_class.__name__.lower()}s.")
    else:
        is_active = status == 'active'
        records = model_class.query.filter_by(is_active=is_active).all()
        log_message('INFO', f"Retrieved all {'active' if is_active else 'deactivated'} {model_class.__name__.lower()}s.")

    return records

# Routes for Auth
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Validate required fields
    if not username or not password:
        return jsonify({"msg": "Username and password are required."}), 400
    
        # Check if the user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create a new user
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully."}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    # Check if user exists and password is correct
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']  # Get the JWT ID
    # Add the token to the blacklist
    db.session.add(TokenBlacklist(jti=jti))
    db.session.commit()
    return jsonify({"msg": "User has been logged out."}), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)  # Fetch the user from the database
    if user is None:
        return jsonify({"msg": "User not found."}), 404
    
    return jsonify({"message": f"Hello user {user.username}!"}), 200

@app.route('/check_user/<username>', methods=['GET'])
def check_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify(msg='User exists'), 200
    else:
        return jsonify(msg='User does not exist'), 404


# Routes for books
@app.route('/book', methods=['POST'])
@jwt_required()  # Require authentication
def create_book():
    """Create a new book in the library."""
    data = request.json
    log_message('INFO', f"Received data for book creation: {data}")

    required_fields = ['name', 'author', 'year_published', 'loan_time_type']
    enum_fields = {'loan_time_type': LoanType}

    # Validate required and enum fields
    validate_fields(data, required_fields, enum_fields)

    new_book = Books(
        name=data['name'],
        author=data['author'],
        year_published=data['year_published'],
        loan_time_type=LoanType[data['loan_time_type']],
        is_loaned=data.get('is_loaned', False)
    )

    db.session.add(new_book)
    db.session.commit()

    log_message('INFO', f"Successfully created a new book: {new_book.name} (ID: {new_book.id})")
    return jsonify(new_book.to_dict()), 201

@app.route('/book/search', methods=['POST'])
def search_book():
    """Search for a specific book using a case-insensitive name."""
    data = request.json
    name = data.get('name')

    if not name:
        log_message('WARNING', "Book name is required for search.")
        abort(400, description="Book name is required for search.")

    return search_record(Books, 'name', name)

@app.route('/author/search', methods=['POST'])
def search_author():
    """Search for a specific book using a case-insensitive author."""
    data = request.json
    author = data.get('author')

    if not author:
        log_message('WARNING', "Book author is required for search.")
        abort(400, description="Book author is required for search.")

    return search_record(Books, 'author', author)

# Routes for books
@app.route('/books', methods=['GET'])
def get_books():
    """Retrieve books based on specified status: active, deactivated, or all."""
    status = request.args.get('status', default='active', type=str)
    books = get_records(Books, status)
    return jsonify([book.to_dict() for book in books]), 200

@app.route('/book/status', methods=['PUT'])
def toggle_book_status():
    """Toggle the active status of a specific book using name from JSON."""
    data = request.json
    name = data.get('name')

    if not name:
        log_message('WARNING', "Book name is required to toggle book status.")
        abort(400, description="Book name is required to toggle book status.")

    return toggle_status(Books, 'name', name)

@app.route('/book/<name>', methods=['DELETE'])
def delete_book(name):
    """Delete a specific book by its name."""
    book = Books.query.filter_by(name=name).first()
    if book is None:
        log_message('WARNING', f"Book not found for deletion: {name}")
        abort(404, description="Book not found.")

    db.session.delete(book)
    db.session.commit()
    
    log_message('INFO', f"Deleted book: {name}")
    return jsonify({'message': f"Book '{name}' deleted successfully."}), 200

# Routes for customers
@app.route('/customer', methods=['POST'])
def create_customer():
    """Create a new customer."""
    data = request.json
    log_message('INFO', f"Received data for customer creation: {data}")

    required_fields = ['full_name', 'email', 'city', 'age']
    enum_fields = {'city': City}

    # Validate required and enum fields
    validate_fields(data, required_fields, enum_fields)

    new_customer = Customers(
        full_name=data['full_name'],
        email=data['email'],
        city=City[data['city']],
        age=data['age']
    )

    db.session.add(new_customer)
    db.session.commit()

    log_message('INFO', f"Successfully created a new customer: {new_customer.full_name} (ID: {new_customer.id})")
    return jsonify(new_customer.to_dict()), 201

@app.route('/customer/status', methods=['PUT'])
def toggle_customer_status():
    """Toggle the active status of a specific customer using email from JSON."""
    data = request.json
    email = data.get('email')

    if not email:
        log_message('WARNING', "Email is required to toggle customer status.")
        abort(400, description="Email is required to toggle customer status.")

    return toggle_status(Customers, 'email', email)

@app.route('/customer/search', methods=['POST'])
def search_customer():
    """Search for a specific customer using email or full name."""
    data = request.json
    email = data.get('email')
    full_name = data.get('full_name')

    if not email and not full_name:
        log_message('WARNING', "Email or Full name is required for search.")
        abort(400, description="Email or Full name is required for search.")

    if email:
        return search_record(Customers, 'email', email)
    elif full_name:
        return search_record(Customers, 'full_name', full_name)

@app.route('/customers', methods=['GET'])
def get_customers():
    """Retrieve customers based on specified status: active, deactivated, or all."""
    status = request.args.get('status', default='active', type=str)
    customers = get_records(Customers, status)
    return jsonify([customer.to_dict() for customer in customers]), 200

@app.route('/customer/<email>', methods=['DELETE'])
def delete_customer(email):
    """Delete a specific customer by their email."""
    customer = Customers.query.filter_by(email=email).first()
    if customer is None:
        log_message('WARNING', f"Customer not found for deletion: {email}")
        abort(404, description="Customer not found.")

    db.session.delete(customer)
    db.session.commit()
    
    log_message('INFO', f"Deleted customer: {email}")
    return jsonify({'message': f"Customer '{email}' deleted successfully."}), 200

# Routes for loans
@app.route('/loan', methods=['POST'])
@jwt_required()
def create_loan():
    """Create a new loan for a book."""
    data = request.json
    log_message('INFO', f"Received data for loan creation: {data}")

    required_fields = ['customer_id', 'book_id', 'loan_time_type']
    enum_fields = {'loan_time_type': LoanType}

    # Validate required and enum fields
    validate_fields(data, required_fields, enum_fields)

    # Check if the book is available for loan
    book = Books.query.get(data['book_id'])
    if book is None or book.is_loaned:
        log_message('ERROR', f"Book is either unavailable or already loaned: {data['book_id']}")
        abort(400, description="Book is unavailable or already loaned.")

    customer = Customers.query.get(data['customer_id'])
    if customer is None:
        log_message('ERROR', f"Customer not found: {data['customer_id']}")
        abort(404, description="Customer not found.")

    return_date = datetime.utcnow() + timedelta(days=LoanType[data['loan_time_type']].value)
    new_loan = Loans(
        customer_id=data['customer_id'],
        book_id=data['book_id'],
        loan_time_type=LoanType[data['loan_time_type']],
        return_date=return_date
    )

    book.is_loaned = True
    db.session.add(new_loan)
    db.session.commit()

    log_message('INFO', f"Successfully created a new loan: {new_loan.id} for book ID: {data['book_id']}")
    return jsonify(new_loan.to_dict()), 201

@app.route('/loan/<int:loan_id>', methods=['DELETE'])
@jwt_required()
def delete_loan(loan_id):
    """Delete a specific loan by its ID."""
    loan = Loans.query.get(loan_id)
    if loan is None:
        log_message('WARNING', f"Loan not found for deletion: {loan_id}")
        abort(404, description="Loan not found.")

    # Mark the associated book as not loaned
    book = Books.query.get(loan.book_id)
    if book:
        book.is_loaned = False

    db.session.delete(loan)
    db.session.commit()
    
    log_message('INFO', f"Deleted loan: {loan_id}")
    return jsonify({'message': f"Loan '{loan_id}' deleted successfully."}), 200

@app.route('/return/<int:loan_id>', methods=['POST'])
@jwt_required()
def return_loan(loan_id):
    """Return a loan."""
    loan = Loans.query.get(loan_id)
    if loan is None:
        log_message('WARNING', f"Loan not found: {loan_id}")
        return jsonify({'error': 'Loan not found'}), 404

    # Check if the loan is already inactive
    if not loan.is_active:
        log_message('WARNING', f"Loan already returned: {loan_id}")
        return jsonify({'error': 'Loan already returned'}), 400

    # Update loan status to inactive and set return date
    loan.is_active = False
    loan.return_date = datetime.utcnow()  # Set the return date
    book = Books.query.get(loan.book_id)
    if book:
        book.is_loaned = False
    db.session.commit()

    log_message('INFO', f"Successfully returned book ID: {book.id} for loan ID: {loan_id}")
    return jsonify({'message': f'Loan {loan_id} for book "{book.name}" returned successfully.'}), 200

@app.route('/loans', methods=['GET'])
def get_loans():
    """Retrieve loans based on specified status: active, deactivated, or all."""
    status = request.args.get('status', default='active', type=str)
    loans = get_records(Loans, status)
    return jsonify([loans.to_dict() for loans in loans]), 200


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

