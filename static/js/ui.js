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
        delay: 5000,
        autohide: true
    });

    toastBody.innerText = msg;
    messageToast.show();
}

// Function to display payload in a container
function displayPayload(data, formatFunction, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = ''; 

    if (data.length > 0) {
        container.innerHTML = data.map(formatFunction).join('');
    } else {
        container.innerHTML = `<div>No items found.</div>`;
        displayMessage('No results found.');
    }
}

// Initialize Bootstrap toasts on page load
document.addEventListener('DOMContentLoaded', () => {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.forEach((toastEl) => new bootstrap.Toast(toastEl));
});
