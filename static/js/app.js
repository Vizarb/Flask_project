const apiUrl = 'http://localhost:5000'; // Replace with your API URL

// Function to store token in local storage
function storeToken(token) {
    localStorage.setItem('jwtToken', token);
}

// Function to get token from local storage
function getToken() {
    return localStorage.getItem('jwtToken');
}

// Function to set token in axios headers
function setAuthHeader() {
    const token = getToken();
    if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
}

// Function to clear the token from local storage and axios headers
function clearToken() {
    localStorage.removeItem('jwtToken');
    delete axios.defaults.headers.common['Authorization'];
}

// Set the token header when the app loads
setAuthHeader();

// Display loading indicator
function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

/**
 * Display a message in the toast
 * @param {string} msg - The message to display.
 */
function displayMessage(msg) {
    const toastBody = document.getElementById('toastBody');
    const messageToast = new bootstrap.Toast(document.getElementById('messageToast'), {
        delay: 5000, // Display for 5 seconds
        autohide: true // Auto-hide after the delay
    });

    // Set the message and show the toast
    toastBody.innerText = msg;
    messageToast.show(); // Show the toast
}

// Function to check if a user exists
async function checkUserExists(username) {
    try {
        const response = await axios.get(`${apiUrl}/check_user/${username}`);
        return response.data.exists; // Adjust based on your API response structure
    } catch (error) {
        console.error('Error checking if user exists:', error);
        return false; // Assume user does not exist in case of an error
    }
}

// Logout function
async function logout() {
    try {
        await axios.post(`${apiUrl}/logout`); // Call the logout endpoint
        clearToken(); // Clear the token from local storage
        displayMessage('Logged out successfully.');
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Logout failed.');
        console.error(error); // Log the error for debugging
    }
}

// Attach logout event listener
document.getElementById('logoutBtn').addEventListener('click', logout);

/**
 * Display payload in the specified container.
 * @param {Array} data - The data to display.
 * @param {Function} formatFunction - Function to format the data.
 * @param {string} containerId - The ID of the container to display data.
 */
function displayPayload(data, formatFunction, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = ''; // Clear existing content

    if (data.length > 0) {
        container.innerHTML = data.map(formatFunction).join('');
    } else {
        container.innerHTML = `<div>No items found.</div>`;
        displayMessage('No results found.'); // Notify user when no results are found
    }
}

// Format functions for different data types
function formatBook(book) {
    return `
        <div class="border p-3 mb-3">
            <h3>${book.name} by ${book.author}</h3>
            <p>Published: ${book.year_published}</p>
            <p>Status: ${book.is_active ? 'Active' : 'Inactive'}</p>
            <p>Loan Time: ${book.loan_time_type.replace('_', ' ').toLowerCase()}</p>
            <p>Category: ${book.category.replace('_', ' ').toLowerCase()}</p>
            <p>Loaned: ${book.is_loaned ? 'Yes' : 'No'}</p>
        </div>
    `;
}

function formatLoan(loan) {
    return `<div class="border p-2 mb-2">Loan ID: ${loan.id}, Book: ${loan.book.name}, Customer: ${loan.customer.full_name}, Due Date: ${loan.return_date}, Status: (${loan.is_active ? 'active' : 'inactive'})</div>`;
}

function formatCustomer(customer) {
    return `<div class="border p-2 mb-2">Name: ${customer.full_name}, Email: ${customer.email}, City: ${customer.city}, Age: ${customer.age}</div>`;
}

// User registration
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('registerUsername').value.trim();
    const password = document.getElementById('registerPassword').value.trim();

    // Validate fields
    if (!username || !password) {
        displayMessage('Username and password are required.');
        return;
    }

    const userExists = await checkUserExists(username);
    if (userExists) {
        displayMessage('User already exists. Please choose a different username.');
        return;
    }

    try {
        showLoading();
        const response = await axios.post(`${apiUrl}/register`, { username, password });
        displayMessage(response.data.msg);
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Registration failed.');
    } finally {
        hideLoading();
    }
});

// User login
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value.trim();

    if (!username || !password) {
        displayMessage('Username and password are required.');
        return;
    }

    try {
        showLoading();
        const response = await axios.post(`${apiUrl}/login`, { username, password });
        storeToken(response.data.access_token);
        setAuthHeader();
        displayMessage(response.data.msg || 'Login successful.');
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Login failed.');
    } finally {
        hideLoading();
    }
});

// Create book
document.getElementById('createBookForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('bookName').value.trim();
    const author = document.getElementById('bookAuthor').value.trim();
    const yearPublished = document.getElementById('yearPublished').value.trim();
    const loanTimeType = document.getElementById('loanTimeType').value.trim();
    const category = document.getElementById('bookCategory').value.trim();

    if (!name || !author || !yearPublished || !loanTimeType || !category) {
        displayMessage('All fields are required to create a book.');
        return;
    }

    try {
        showLoading();
        const response = await axios.post(`${apiUrl}/book`, {
            name,
            author,
            year_published: yearPublished,
            loan_time_type: loanTimeType,
            category
        });
        displayMessage(response.data.msg || `Book Created: ${response.data.name}`);
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Failed to create book.');
    } finally {
        hideLoading();
    }
});

// Search book
document.getElementById('searchBookForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('searchBookName').value.trim();

    if (!name) {
        displayMessage('Please provide a book name to search.');
        return;
    }

    try {
        showLoading();
        const response = await axios.post(`${apiUrl}/book/search`, { name });
        displayPayload(response.data, formatBook, 'booksList');
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Search failed.');
    } finally {
        hideLoading();
    }
});

// Toggle book status
document.getElementById('toggleBookStatusForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('toggleBookName').value.trim();

    if (!name) {
        displayMessage('Please provide a book name to toggle status.');
        return;
    }

    try {
        showLoading();
        const response = await axios.put(`${apiUrl}/book/status`, { name });
        displayMessage(response.data.msg || JSON.stringify(response.data));
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Failed to toggle status.');
    } finally {
        hideLoading();
    }
});

// Register customer
document.getElementById('registerCustomerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const full_name = document.getElementById('customerName').value.trim();
    const email = document.getElementById('customerEmail').value.trim();
    const city = document.getElementById('customerCity').value.trim();
    const age = parseInt(document.getElementById('customerAge').value.trim());

    if (!full_name || !email || !city || isNaN(age)) {
        displayMessage('All fields are required to register a customer.');
        return;
    }

    try {
        showLoading();
        const response = await axios.post(`${apiUrl}/customer`, { full_name, email, city, age });
        displayMessage(response.data.msg || `Customer Created: ${response.data.full_name}`);
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Failed to register customer.');
    } finally {
        hideLoading();
    }
});

// Search customer
document.getElementById('searchCustomerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fullName = document.getElementById('searchCustomerName').value.trim();
    const email = document.getElementById('searchCustomerEmail').value.trim() || null;

    if (!fullName && !email) {
        displayMessage('Please provide a customer name or email to search.');
        return;
    }

    try {
        showLoading();
        const response = await axios.post(`${apiUrl}/customer/search`, { email, full_name: fullName });
        displayPayload(response.data, formatCustomer, 'customersList');
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Search failed.');
    } finally {
        hideLoading();
    }
});

// Create loan
document.getElementById('createLoanForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const bookName = document.getElementById('loanBookName').value.trim();
    const customerFullName = document.getElementById('loanCustomerFullName').value.trim();
    const customerEmail = document.getElementById('loanCustomerEmail').value.trim();
    const duration = document.getElementById('loanDuration').value.trim();

    if (!bookName || !customerFullName || !customerEmail || !duration) {
        displayMessage('All fields are required to create a loan.');
        return;
    }

    try {
        showLoading();
        const bookResponse = await axios.post(`${apiUrl}/book/search`, { name: bookName });
        if (bookResponse.data.length === 0) {
            displayMessage(`Book not found.`);
            throw new Error("Book not found.");
        }

        const bookId = bookResponse.data[0].id;

        const customerResponse = await axios.post(`${apiUrl}/customer/search`, {
            full_name: customerFullName,
            email: customerEmail
        });
        if (customerResponse.data.length === 0) {
            displayMessage(`Customer not found.`);
            throw new Error("Customer not found.");
        }

        const customerId = customerResponse.data[0].id;

        const loanResponse = await axios.post(`${apiUrl}/loan`, {
            book_id: bookId,
            customer_id: customerId,
            loan_time_type: duration
        });

        displayMessage(loanResponse.data.msg || `Loan Created: ${JSON.stringify(loanResponse.data)}`);
    } catch (error) {
        displayMessage(error.response?.data?.msg || error.message || 'Failed to create loan.');
    } finally {
        hideLoading();
    }
});

// Get all books based on selected type
document.getElementById('getBooksBtn').addEventListener('click', async () => {
    const bookType = document.getElementById('bookTypeSelect').value;
    try {
        showLoading();
        const response = await axios.get(`${apiUrl}/books?status=${bookType}`);
        displayPayload(response.data, formatBook, 'booksList');
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Failed to retrieve books.');
    } finally {
        hideLoading();
    }
});

// Get all loans based on selected type
document.getElementById('getLoansBtn').addEventListener('click', async () => {
    const loanType = document.getElementById('loanTypeSelect').value;
    try {
        showLoading();
        const response = await axios.get(`${apiUrl}/loans?status=${loanType}`);
        displayPayload(response.data, formatLoan, 'loansList');
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Failed to retrieve loans.');
    } finally {
        hideLoading();
    }
});

// Get all customers based on selected type
document.getElementById('getCustomersBtn').addEventListener('click', async () => {
    const customerType = document.getElementById('customerTypeSelect').value;
    try {
        showLoading();
        const response = await axios.get(`${apiUrl}/customers?status=${customerType}`);
        displayPayload(response.data, formatCustomer, 'customersList');
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Failed to retrieve customers.');
    } finally {
        hideLoading();
    }
});

// Return loan
document.getElementById('returnLoanForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const loanId = document.getElementById('returnLoanId').value.trim();

    if (!loanId) {
        displayMessage('Loan ID is required to return a loan.');
        return;
    }

    try {
        showLoading();
        const response = await axios.post(`${apiUrl}/return/${loanId}`);
        displayMessage(response.data.message || 'Loan returned successfully.');
    } catch (error) {
        displayMessage(error.response?.data?.error || 'Failed to return loan.');
    } finally {
        hideLoading();
    }
});

// Initialize Bootstrap toasts on page load
document.addEventListener('DOMContentLoaded', () => {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl);
    });
});
