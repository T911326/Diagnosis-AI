// Questions page specific functionality
$(document).ready(function() {
    // Initialize event listeners
    initQuestionsEventListeners();
    
    // Load any existing diagnosis data
    loadDiagnosisData();
});

// Initialize event listeners
function initQuestionsEventListeners() {
    // Submit question button
    $('#submit-question-btn').on('click', function() {
        submitQuestion();
    });
    
    // Back to conclusions
    $('#back-to-conclusions-btn').on('click', function() {
        window.location.href = '/conclusions_page';
    });
    
    // Question text area - enable submit on enter
    $('#question-text').on('keypress', function(e) {
        if (e.which === 13 && !e.shiftKey) {
            e.preventDefault();
            submitQuestion();
        }
    });
    
    // FAQ accordion items
    $('.faq-question').on('click', function() {
        const answer = $(this).next('.faq-answer');
        answer.slideToggle(200);
        $(this).toggleClass('active');
        
        // Toggle the icon
        const icon = $(this).find('i');
        if (icon.hasClass('fa-chevron-down')) {
            icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
        } else {
            icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
        }
    });
}

// Load diagnosis data from the session
function loadDiagnosisData() {
    $.ajax({
        url: '/get-diagnosis-data',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                // Show the condition in the questions context
                updateQuestionsContext(response.results);
            } else {
                $('#diagnosis-context').html(`
                    <div class="alert alert-warning">
                        <p>No diagnosis data found. Your questions will be answered in a general context.</p>
                    </div>
                `);
            }
        },
        error: function() {
            showAlert('error', 'Failed to load diagnosis data');
        }
    });
}

// Update the questions context UI with diagnosis data
function updateQuestionsContext(results) {
    if (!results || results.length === 0) {
        return;
    }
    
    // Get primary condition (highest confidence)
    const primaryCondition = [...results].sort((a, b) => b.confidence - a.confidence)[0];
    
    // Update the context UI
    $('#diagnosis-context').html(`
        <div class="alert alert-info">
            <p>Your questions will be answered in the context of your diagnosis: <strong>${primaryCondition.disease}</strong></p>
        </div>
    `);
}

// Submit a question
function submitQuestion() {
    const questionText = $('#question-text').val().trim();
    
    if (!questionText) {
        showAlert('warning', 'Please enter a question');
        return;
    }
    
    // Show loading indicator
    $('#question-loading').removeClass('d-none');
    $('#submit-question-btn').prop('disabled', true);
    
    // Send question to server
    $.ajax({
        url: '/answer-question',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ question: questionText }),
        success: function(response) {
            // Hide loading indicator
            $('#question-loading').addClass('d-none');
            $('#submit-question-btn').prop('disabled', false);
            
            if (response.success) {
                // Add the Q&A to the history
                addQuestionToHistory(questionText, response.answer);
                
                // Clear the question input
                $('#question-text').val('');
            } else {
                showAlert('error', response.message || 'Failed to get an answer');
            }
        },
        error: function() {
            // Hide loading indicator
            $('#question-loading').addClass('d-none');
            $('#submit-question-btn').prop('disabled', false);
            
            showAlert('error', 'Failed to connect to the server');
        }
    });
}

// Add a question and answer to the history
function addQuestionToHistory(question, answer) {
    const historyContainer = $('#qa-history');
    
    // Create a new QA item
    const qaItem = $(`
        <div class="qa-item mb-4">
            <div class="qa-question">
                <div class="d-flex">
                    <div class="qa-icon me-2">
                        <i class="fas fa-user-circle text-primary fa-2x"></i>
                    </div>
                    <div class="qa-content">
                        <p class="mb-0">${question}</p>
                    </div>
                </div>
            </div>
            <div class="qa-answer mt-2">
                <div class="d-flex">
                    <div class="qa-icon me-2">
                        <i class="fas fa-robot text-secondary fa-2x"></i>
                    </div>
                    <div class="qa-content">
                        <p class="mb-0">${answer}</p>
                    </div>
                </div>
            </div>
        </div>
    `);
    
    // Add to the beginning of the history
    historyContainer.prepend(qaItem);
    
    // If this is the first question, remove the placeholder
    if (historyContainer.find('.qa-placeholder').length > 0) {
        historyContainer.find('.qa-placeholder').remove();
    }
}
