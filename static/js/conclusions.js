// Conclusions page specific functionality
$(document).ready(function() {
    // Load diagnosis data when the page loads
    loadConclusionsData();
    
    // Initialize event listeners
    initConclusionsEventListeners();
});

// Initialize event listeners
function initConclusionsEventListeners() {
    // Export PDF button
    $('#conclusions-export-btn').on('click', function() {
        exportToPdf();
    });
    
    // Back to findings
    $('#back-to-findings-btn').on('click', function() {
        window.location.href = '/findings_page';
    });
    
    // New diagnosis button
    $('#new-diagnosis-btn').on('click', function() {
        window.location.href = '/diagnosis_page';
    });
    
    // Questions button
    $('#go-to-questions-btn').on('click', function() {
        window.location.href = '/questions_page';
    });
}

// Load diagnosis data from the session
function loadConclusionsData() {
    $.ajax({
        url: '/get-diagnosis-data',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                // Update the UI with the diagnosis data
                updateConclusionsUI(response.results, response.symptoms);
            } else {
                $('#conclusions-container').html(`
                    <div class="alert alert-warning">
                        <h4>No diagnosis data found</h4>
                        <p>Please complete a diagnosis first.</p>
                        <a href="/diagnosis_page" class="btn btn-primary">Go to Diagnosis</a>
                    </div>
                `);
            }
        },
        error: function() {
            showAlert('error', 'Failed to load diagnosis data');
        }
    });
}

// Update the conclusions UI with diagnosis data
function updateConclusionsUI(results, symptoms) {
    if (!results || results.length === 0) {
        $('#conclusions-container').html(`
            <div class="alert alert-info">
                <h4>No conditions found</h4>
                <p>The diagnosis did not find any potential conditions matching your symptoms.</p>
            </div>
        `);
        return;
    }
    
    // Update diagnosis summary
    const summaryContainer = $('#diagnosis-summary');
    summaryContainer.empty();
    
    // Find the highest confidence condition
    const primaryCondition = [...results].sort((a, b) => b.confidence - a.confidence)[0];
    
    // Create summary content
    const summaryContent = $(`
        <div class="row">
            <div class="col-md-8">
                <h3>Primary Diagnosis: ${primaryCondition.disease}</h3>
                <div class="confidence-display mb-3">
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar bg-${primaryCondition.confidence >= 70 ? 'success' : primaryCondition.confidence >= 50 ? 'warning' : 'danger'}" 
                             role="progressbar" 
                             style="width: ${primaryCondition.confidence}%;" 
                             aria-valuenow="${primaryCondition.confidence}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                            ${primaryCondition.confidence}% Confidence
                        </div>
                    </div>
                </div>
                <h4>Recommended Actions:</h4>
                <div class="recommendations">
                    <p>${primaryCondition.advice}</p>
                    <div class="alert alert-info">
                        <strong>Important:</strong> This diagnosis is based on the symptoms you provided and should not replace professional medical advice. Please consult with a healthcare provider for a proper evaluation.
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="symptoms-summary">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0">Reported Symptoms</h5>
                        </div>
                        <div class="card-body">
                            <ul class="list-group">
                                ${symptoms && symptoms.length > 0 ? 
                                    symptoms.map(symptom => `<li class="list-group-item">${symptom}</li>`).join('') : 
                                    '<li class="list-group-item">No symptoms selected</li>'}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <h4>Other Potential Conditions</h4>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>Condition</th>
                                <th>Confidence</th>
                                <th>Advice</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${results.slice(1).map(condition => `
                                <tr>
                                    <td>${condition.disease}</td>
                                    <td>
                                        <div class="d-flex align-items-center">
                                            <div class="progress flex-grow-1" style="height: 10px;">
                                                <div class="progress-bar bg-${condition.confidence >= 70 ? 'success' : condition.confidence >= 50 ? 'warning' : 'danger'}" 
                                                     role="progressbar" 
                                                     style="width: ${condition.confidence}%;" 
                                                     aria-valuenow="${condition.confidence}" 
                                                     aria-valuemin="0" 
                                                     aria-valuemax="100">
                                                </div>
                                            </div>
                                            <span class="ms-2">${condition.confidence}%</span>
                                        </div>
                                    </td>
                                    <td>${condition.advice}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `);
    
    summaryContainer.append(summaryContent);
    
    // Enable action buttons
    $('#conclusions-export-btn, #go-to-questions-btn').prop('disabled', false);
}

// Export results to PDF
function exportToPdf() {
    // Create a form to submit POST request for file download
    const form = $('<form>').attr({
        method: 'POST',
        action: '/export-pdf',
        target: '_blank'
    });
    
    $('body').append(form);
    form.submit().remove();
}
