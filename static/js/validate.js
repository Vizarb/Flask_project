document.addEventListener('DOMContentLoaded', function () {
    // Initialize all forms after DOM content is loaded
    initializeForms();
});

function initializeForms() {
    // Registration Form Validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', validateRegistrationForm);
    }

    // Customer Form Validation
    const customerForm = document.getElementById('registerCustomerForm');
    if (customerForm) {
        customerForm.addEventListener('submit', validateCustomerForm);
    }

    // Loan Form Validation
    const loanForm = document.getElementById('createLoanForm');
    if (loanForm) {
        loanForm.addEventListener('submit', validateLoanForm);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Registration Form Validation
    const registerForm = document.getElementById('registerForm');
    registerForm.addEventListener('submit', validateRegistrationForm);

    function validateRegistrationForm(event) {
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;

        // Clear previous error messages
        document.getElementById('usernameError').textContent = '';
        document.getElementById('passwordError').textContent = '';

        if (!/^[a-zA-Z0-9_]{3,15}$/.test(username)) {
            event.preventDefault();
            document.getElementById('usernameError').textContent = 'Username must be 3-15 characters long and can only contain letters, numbers, and underscores.';
            return;
        }

        if (password.length < 6) {
            event.preventDefault();
            document.getElementById('passwordError').textContent = 'Password must be at least 6 characters long.';
            return;
        }
    }
});



function validateCustomerForm(event) {
    const customerEmail = document.getElementById('customerEmail').value;
    const customerAge = parseInt(document.getElementById('customerAge').value);

    if (!validateEmail(customerEmail)) {
        event.preventDefault();
        showToast('Please enter a valid email.');
        return;
    }

    if (isNaN(customerAge) || customerAge < 18 || customerAge > 100) {
        event.preventDefault();
        showToast('Customer age must be between 18 and 100.');
        return;
    }
}

function validateLoanForm(event) {
    const loanDuration = document.getElementById('loanDuration').value;
    if (!loanDuration) {
        event.preventDefault();
        showToast('Please select a loan duration.');
    }
}

// Helper function to validate email format
function validateEmail(email) {
    const emailPattern = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    return emailPattern.test(email);
}

// Helper function to display toast messages
function showToast(message) {
    const toastBody = document.getElementById('toastBody');
    toastBody.innerText = message;
    const toast = new bootstrap.Toast(document.getElementById('messageToast'));
    toast.show();
}
