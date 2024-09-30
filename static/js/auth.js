const apiUrl = 'https://flask-project-a035.onrender.com'; // Replace with your API URL

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

// User registration
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('registerUsername').value.trim();
    const password = document.getElementById('registerPassword').value.trim();

    if (!username || !password) {
        displayMessage('Username and password are required.');
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

// Logout function
async function logout() {
    try {
        await axios.post(`${apiUrl}/logout`);
        clearToken();
        displayMessage('Logged out successfully.');
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Logout failed.');
        console.error(error);
    }
}

// Attach logout event listener
document.getElementById('logoutBtn').addEventListener('click', logout);
