// Common functionality shared across all pages
$(document).ready(function() {
    // Language selector functionality
    $('#language-select').on('change', function() {
        const selectedLanguage = $(this).val();
        changeLanguage(selectedLanguage);
    });

    // Initialize any tooltips
    initTooltips();
});

// Change language
function changeLanguage(lang) {
    $.ajax({
        url: '/set-language',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ language: lang }),
        success: function(response) {
            if (response.success) {
                // Update translations and reload the page
                window.location.reload();
            } else {
                showAlert('error', response.message);
            }
        },
        error: function() {
            showAlert('error', 'Failed to change language');
        }
    });
}

// Initialize Bootstrap tooltips
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// Show alert message
function showAlert(type, message) {
    // Create alert element
    const alertElement = $(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);
    
    // Append to body
    $('body').append(alertElement);
    
    // Position the alert at the top of the page
    alertElement.css({
        'position': 'fixed',
        'top': '20px',
        'left': '50%',
        'transform': 'translateX(-50%)',
        'z-index': 9999,
        'min-width': '300px'
    });
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        alertElement.alert('close');
    }, 5000);
}