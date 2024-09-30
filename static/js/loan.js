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
        const bookId = bookResponse.data[0].id;

        const customerResponse = await axios.post(`${apiUrl}/customer/search`, { full_name: customerFullName, email: customerEmail });
        const customerId = customerResponse.data[0].id;

        const loanResponse = await axios.post(`${apiUrl}/loan`, { book_id: bookId, customer_id: customerId, loan_time_type: duration });
        displayMessage(loanResponse.data.msg || `Loan Created: ${JSON.stringify(loanResponse.data)}`);
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Failed to create loan.');
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
