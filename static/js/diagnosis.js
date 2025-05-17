// Diagnosis page specific functionality
$(document).ready(function() {
    // Initialize search functionality
    initSearch();
    
    // Initialize diagnosis-specific event listeners
    initDiagnosisEventListeners();
});

// Initialize search functionality for symptoms
function initSearch() {
    $('#symptom-search').on('keyup', function() {
        const searchTerm = $(this).val().toLowerCase();
        
        $('.symptom-item').each(function() {
            const symptomText = $(this).data('search');
            
            if (symptomText.includes(searchTerm)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
    
    $('#search-btn').on('click', function() {
        $('#symptom-search').trigger('keyup');
    });
}

// Initialize diagnosis-specific event listeners
function initDiagnosisEventListeners() {
    // Diagnose button
    $('#diagnose-btn').on('click', function() {
        diagnose();
    });
    
    // Clear button
    $('#clear-btn').on('click', function() {
        clearSelections();
    });
    
    // Chart buttons
    $('#chart-btn, #modal-chart-btn').on('click', function() {
        showChart();
    });
    
    // Export PDF buttons
    $('#export-btn, #modal-export-btn').on('click', function() {
        exportToPdf();
    });
    
    // Save results button
    $('#save-btn').on('click', function() {
        saveResults();
    });

    // Continue to findings button
    $('#continue-to-findings-btn').on('click', function() {
        saveDiagnosisAndRedirect('findings_page');
    });
}

// Global variable to store diagnosis results
let diagnosisResults = [];

// Run diagnosis
function diagnose() {
    // Get selected symptoms
    const selectedSymptoms = [];
    $('.symptom-checkbox:checked').each(function() {
        selectedSymptoms.push($(this).data('symptom-id'));
    });
    
    if (selectedSymptoms.length === 0) {
        showAlert('warning', translations.no_symptoms_selected);
        return;
    }
    
    // Send to server
    $.ajax({
        url: '/diagnose',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ symptoms: selectedSymptoms }),
        success: function(response) {
            if (response.success) {
                diagnosisResults = response.results;
                
                if (diagnosisResults.length === 0) {
                    showAlert('info', translations.no_disease_match);
                } else {
                    // Debug the results
                    console.log("Diagnosis results:", diagnosisResults);
                    displayDiagnosisResults(diagnosisResults);
                    enableResultButtons();
                }
            } else {
                showAlert('error', response.message || 'Error performing diagnosis');
            }
        },
        error: function(xhr, status, error) {
            console.error("AJAX Error:", status, error);
            showAlert('error', 'Failed to connect to the server: ' + error);
        }
    });
}

// Display diagnosis results in modal
function displayDiagnosisResults(results) {
    const resultsContainer = $('#diagnosis-results');
    resultsContainer.empty();
    
    console.log("Displaying results:", results);
    
    results.forEach(result => {
        // Determine confidence class
        let confidenceClass = 'low';
        if (result.confidence >= 70) {
            confidenceClass = 'high';
        } else if (result.confidence >= 50) {
            confidenceClass = 'medium';
        }
        
        // Create result card
        const resultCard = $(`
            <div class="result-card">
                <div class="result-header">
                    <h4 class="disease-name">${result.disease}</h4>
                    <span class="confidence ${confidenceClass}">${result.confidence}%</span>
                </div>
                <div class="confidence-bar-container mt-2">
                    <div class="confidence-bar" style="width: ${result.confidence}%; background-color: var(${result.confidence >= 70 ? '--success' : result.confidence >= 50 ? '--warning' : '--danger'})"></div>
                </div>
                <div class="result-body">
                    <p class="advice-title">${translations.advice_label}:</p>
                    <p class="advice-text">${result.advice}</p>
                </div>
            </div>
        `);
        
        resultsContainer.append(resultCard);
    });
    
    try {
        // Show the modal using direct DOM access
        const diagnosisModal = new bootstrap.Modal(document.getElementById('diagnosis-modal'));
        diagnosisModal.show();
    } catch (e) {
        console.error("Error showing modal:", e);
        alert("Diagnosis completed. Check results in the console.");
    }
}

// Enable buttons that depend on having results
function enableResultButtons() {
    $('#chart-btn, #export-btn, #save-btn, #continue-to-findings-btn').prop('disabled', false);
}

// Clear all symptom selections
function clearSelections() {
    $('.symptom-checkbox').prop('checked', false);
    diagnosisResults = [];
    $('#chart-btn, #export-btn, #save-btn, #continue-to-findings-btn').prop('disabled', true);
    showAlert('info', translations.selections_cleared || 'Symptom selections cleared.');
}

// Show chart with diagnosis results
function showChart() {
    if (diagnosisResults.length === 0) {
        showAlert('warning', translations.run_diagnosis_first || 'Please run the diagnosis first.');
        return;
    }
    
    // Show the chart modal with loading spinner
    const chartModal = new bootstrap.Modal(document.getElementById('chart-modal'));
    chartModal.show();
    
    // Generate chart
    $.ajax({
        url: '/generate-chart',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ results: diagnosisResults }),
        success: function(response) {
            if (response.success) {
                // Create image from base64 data
                const chartImg = $('<img>').attr({
                    'src': response.chart_data,
                    'class': 'img-fluid',
                    'alt': 'Diagnosis Chart'
                });
                
                $('#chart-container').empty().append(chartImg);
            } else {
                $('#chart-container').html('<p class="text-danger">Failed to generate chart</p>');
            }
        },
        error: function() {
            $('#chart-container').html('<p class="text-danger">Failed to connect to the server</p>');
        }
    });
}

// Export results to PDF
function exportToPdf() {
    if (diagnosisResults.length === 0) {
        showAlert('warning', translations.no_results_to_export || 'No diagnosis results to export.');
        return;
    }
    
    // Create a form to submit POST request for file download
    const form = $('<form>').attr({
        method: 'POST',
        action: '/export-pdf',
        target: '_blank'
    });
    
    $('body').append(form);
    form.submit().remove();
}

// Save results as JSON
function saveResults() {
    if (diagnosisResults.length === 0) {
        showAlert('warning', translations.no_results_to_save || 'No diagnosis results to save.');
        return;
    }
    
    // Create a form to submit POST request for file download
    const form = $('<form>').attr({
        method: 'POST',
        action: '/save-results',
        target: '_blank'
    });
    
    $('body').append(form);
    form.submit().remove();
}

// Save diagnosis to session and redirect
function saveDiagnosisAndRedirect(targetPage) {
    if (diagnosisResults.length === 0) {
        showAlert('warning', translations.run_diagnosis_first || 'Please run the diagnosis first.');
        return;
    }
    
    $.ajax({
        url: '/save-diagnosis-session',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ results: diagnosisResults }),
        success: function(response) {
            if (response.success) {
                window.location.href = `/${targetPage}`;
            } else {
                showAlert('error', response.message || 'Error saving diagnosis results');
            }
        },
        error: function() {
            showAlert('error', 'Failed to connect to the server');
        }
    });
}
