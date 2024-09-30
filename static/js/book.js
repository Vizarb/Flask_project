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
        const response = await axios.post(`${apiUrl}/book`, { name, author, year_published: yearPublished, loan_time_type: loanTimeType, category });
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
