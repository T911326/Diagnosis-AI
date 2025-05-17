// Findings page specific functionality
$(document).ready(function() {
    // Load diagnosis data when the page loads
    loadDiagnosisData();
    
    // Initialize event listeners
    initFindingsEventListeners();
});

// Initialize event listeners
function initFindingsEventListeners() {
    // Continue to conclusions button
    $('#continue-to-conclusions-btn').on('click', function() {
        window.location.href = '/conclusions_page';
    });
    
    // Back to diagnosis
    $('#back-to-diagnosis-btn').on('click', function() {
        window.location.href = '/diagnosis_page';
    });
    
    // Refresh findings button
    $('#refresh-findings-btn').on('click', function() {
        loadDiagnosisData();
    });

    // Chart button
    $('#findings-chart-btn').on('click', function() {
        showChart();
    });
}

// Load diagnosis data from the session
function loadDiagnosisData() {
    $.ajax({
        url: '/get-diagnosis-data',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                // Update the UI with the diagnosis data
                updateFindingsUI(response.results, response.symptoms);
            } else {
                $('#findings-container').html(`
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

// Update the findings UI with diagnosis data
function updateFindingsUI(results, symptoms) {
    if (!results || results.length === 0) {
        $('#findings-container').html(`
            <div class="alert alert-info">
                <h4>No conditions found</h4>
                <p>The diagnosis did not find any potential conditions matching your symptoms.</p>
            </div>
        `);
        return;
    }
    
    // Update selected symptoms
    const symptomsList = $('#selected-symptoms-list');
    symptomsList.empty();
    
    if (symptoms && symptoms.length > 0) {
        symptoms.forEach(symptom => {
            symptomsList.append(`<li class="list-group-item">${symptom}</li>`);
        });
    } else {
        symptomsList.append(`<li class="list-group-item">No symptoms selected</li>`);
    }
    
    // Update findings
    const findingsContainer = $('#findings-results');
    findingsContainer.empty();
    
    // Sort results by confidence
    const sortedResults = [...results].sort((a, b) => b.confidence - a.confidence);
    
    // Add primary finding (highest confidence)
    const primaryFinding = sortedResults[0];
    const primaryCard = createFindingCard(primaryFinding, true);
    findingsContainer.append(primaryCard);
    
    // Add secondary findings
    if (sortedResults.length > 1) {
        const secondaryFindings = $('<div class="secondary-findings mt-4"></div>');
        const secondaryTitle = $('<h4>Other Potential Conditions</h4>');
        secondaryFindings.append(secondaryTitle);
        
        const secondaryRow = $('<div class="row"></div>');
        
        for (let i = 1; i < sortedResults.length; i++) {
            const secondaryCol = $('<div class="col-md-6 mb-3"></div>');
            const secondaryCard = createFindingCard(sortedResults[i], false);
            secondaryCol.append(secondaryCard);
            secondaryRow.append(secondaryCol);
        }
        
        secondaryFindings.append(secondaryRow);
        findingsContainer.append(secondaryFindings);
    }
    
    // Enable the buttons
    $('#findings-chart-btn, #continue-to-conclusions-btn').prop('disabled', false);
}

// Create a card for a finding
function createFindingCard(finding, isPrimary) {
    let confidenceClass = 'low';
    if (finding.confidence >= 70) {
        confidenceClass = 'high';
    } else if (finding.confidence >= 50) {
        confidenceClass = 'medium';
    }
    
    const cardClass = isPrimary ? 'primary-finding' : '';
    
    return $(`
        <div class="finding-card ${cardClass}">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h4 class="mb-0">${finding.disease}</h4>
                    <span class="badge confidence-badge ${confidenceClass}">${finding.confidence}% Confidence</span>
                </div>
                <div class="card-body">
                    <div class="confidence-bar-container mb-3">
                        <div class="confidence-bar" style="width: ${finding.confidence}%; background-color: var(${finding.confidence >= 70 ? '--success' : finding.confidence >= 50 ? '--warning' : '--danger'})"></div>
                    </div>
                    <h5>Analysis:</h5>
                    <p>Based on your selected symptoms, our system has identified a potential match with ${finding.disease}.</p>
                    <h5>Medical Advice:</h5>
                    <p>${finding.advice}</p>
                </div>
            </div>
        </div>
    `);
}

// Show chart with diagnosis results
function showChart() {
    // Show the chart modal with loading spinner
    const chartModal = new bootstrap.Modal(document.getElementById('chart-modal'));
    chartModal.show();
    
    // Generate chart
    $.ajax({
        url: '/generate-chart-from-session',
        type: 'GET',
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
