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
    const full_name = document.getElementById('searchCustomerName').value.trim();
    const email = document.getElementById('searchCustomerEmail').value.trim();

    if (!full_name || !email) {
        displayMessage('Please provide customer name and email to search.');
        return;
    }

    try {
        showLoading();
        const response = await axios.post(`${apiUrl}/customer/search`, { full_name, email });
        displayPayload(response.data, formatCustomer, 'customersList');
    } catch (error) {
        displayMessage(error.response?.data?.msg || 'Search failed.');
    } finally {
        hideLoading();
    }
});
