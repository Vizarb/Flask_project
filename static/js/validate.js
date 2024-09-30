document.addEventListener('DOMContentLoaded', function () {
    // Registration Form Validation
    const registerForm = document.getElementById('registerForm');
    registerForm.addEventListener('submit', function (event) {
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;

        if (!/^[a-zA-Z0-9_]{3,15}$/.test(username)) {
            event.preventDefault();
            showToast('Username must be 3-15 characters long and can only contain letters, numbers, and underscores.');
            return;
        }

        if (password.length < 6) {
            event.preventDefault();
            showToast('Password must be at least 6 characters long.');
            return;
        }
    });

    // Customer Form Validation
    const customerForm = document.getElementById('registerCustomerForm');
    customerForm.addEventListener('submit', function (event) {
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
    });

    // Loan Form Validation
    const loanForm = document.getElementById('createLoanForm');
    loanForm.addEventListener('submit', function (event) {
        const loanDuration = document.getElementById('loanDuration').value;
        if (!loanDuration) {
            event.preventDefault();
            showToast('Please select a loan duration.');
        }
    });

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
});
